#!/usr/bin/env python3
"""Validate a Visual QA capture bundle and report deterministic runtime findings."""
from __future__ import annotations

import argparse
import json
import struct
import sys
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n" or len(data) < 24:
        raise ValueError(f"Invalid PNG: {path}")
    return struct.unpack(">II", data[16:24])


def add_finding(items, finding_id, severity, title, evidence):
    items.append({
        "id": finding_id,
        "severity": severity,
        "title": title,
        "evidence": evidence,
    })


def validate_samples(metrics, expected_count, label, errors):
    samples = metrics.get("samples", [])
    if len(samples) != expected_count:
        errors.append(f"{label}: expected {expected_count} samples, got {len(samples)}")
    previous = -1.0
    for sample in samples:
        timestamp = float(sample.get("timestamp_seconds", -1.0))
        if timestamp <= previous:
            errors.append(f"{label}: timestamps are not strictly increasing")
            break
        previous = timestamp
        image = Path(sample.get("image", ""))
        if not image.is_file():
            errors.append(f"{label}: missing captured image {image}")
            break
    return samples


def expected_schedule(segments, counts):
    result = []
    for state_name, intervals in segments.items():
        total_length = sum(float(end) - float(start) for start, end in intervals)
        count = int(counts.get(state_name, 24))
        if total_length <= 0.0 or count < 1:
            continue
        for sample_index in range(count):
            remaining = (sample_index + 0.5) * total_length / count
            target_time = 0.0
            for start, end in intervals:
                interval_length = float(end) - float(start)
                if remaining < interval_length:
                    target_time = float(start) + remaining
                    break
                remaining -= interval_length
            result.append((target_time, str(state_name)))
    result.sort(key=lambda item: item[0])
    return result


def validate_state_sheets(output_dir, dimension, states, errors):
    for state in states:
        state_dir = output_dir / dimension / state
        sheet = state_dir / "contact_sheet.png"
        manifest = state_dir / "contact_sheet.json"
        selected = state_dir / "selected"
        if not sheet.is_file() or not manifest.is_file() or not selected.is_dir():
            errors.append(f"{dimension}/{state}: contact sheet bundle is incomplete")
            continue
        try:
            png_dimensions(sheet)
            selection = load_json(manifest)
            count = len(selection.get("frames", []))
            if count < 2:
                errors.append(f"{dimension}/{state}: fewer than two selected frames")
        except Exception as exc:
            errors.append(f"{dimension}/{state}: {exc}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--profile", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args()
    project = args.project_root.resolve()
    output = args.output_dir.resolve()
    profile = load_json(args.profile.resolve())
    capture = profile["capture"]
    expected_2d = sum(int(value) for value in capture["2d_samples_per_segment"].values())
    expected_3d = sum(int(value) for value in capture["3d_samples_per_segment"].values())
    errors = []
    findings = []
    metrics_2d_path = output / "2d" / "metrics.json"
    metrics_3d_path = output / "3d" / "metrics.json"
    if not metrics_2d_path.is_file() or not metrics_3d_path.is_file():
        print("BUNDLE_INVALID: capture metrics are missing", file=sys.stderr)
        return 1
    metrics_2d = load_json(metrics_2d_path)
    metrics_3d = load_json(metrics_3d_path)
    samples_2d = validate_samples(metrics_2d, expected_2d, "2D", errors)
    samples_3d = validate_samples(metrics_3d, expected_3d, "3D", errors)
    for sample in samples_2d:
        if sample.get("sprite_frame_count") is None or int(sample.get("sprite_frame_count", 0)) < 1:
            errors.append(
                f"2D: sample {sample.get('sequence_index')} is missing a valid sprite_frame_count"
            )
            break
        if not isinstance(sample.get("sprite_animation_looping"), bool):
            errors.append(
                f"2D: sample {sample.get('sequence_index')} is missing sprite_animation_looping"
            )
            break
    for sample in samples_3d:
        if sample.get("animation_loop_mode") is None:
            errors.append(
                f"3D: sample {sample.get('sequence_index')} is missing animation_loop_mode"
            )
            break
    fixed_fps = max(1.0, float(capture.get("fixed_fps", 24)))
    max_drift = float(capture.get("max_schedule_drift_frames", 2)) / fixed_fps
    for label, samples, segments_key, counts_key in [
        ("2D", samples_2d, "2d_segments", "2d_samples_per_segment"),
        ("3D", samples_3d, "3d_segments", "3d_samples_per_segment"),
    ]:
        schedule = expected_schedule(capture[segments_key], capture[counts_key])
        if len(schedule) == len(samples):
            for index, (sample, (target_time, expected_state)) in enumerate(zip(samples, schedule)):
                drift = float(sample.get("timestamp_seconds", -1.0)) - target_time
                if abs(drift) > max_drift:
                    errors.append(
                        f"{label}: sample {index} timestamp drift {drift:.4f}s exceeds "
                        f"{max_drift:.4f}s ({capture.get('max_schedule_drift_frames', 2)} frames)"
                    )
                    break
                recorded_expected = str(sample.get("expected_state", "")).lower()
                if recorded_expected != expected_state.lower():
                    errors.append(
                        f"{label}: sample {index} records expected_state={recorded_expected!r}, "
                        f"but profile schedule requires {expected_state!r}"
                    )
                    break
                actual_state = str(sample.get("state", "")).lower()
                if not actual_state:
                    errors.append(f"{label}: sample {index} has no actual runtime state")
                    break
                if actual_state != expected_state.lower():
                    add_finding(
                        findings, f"{label}-STATE-SCHEDULE-MISMATCH", "high",
                        f"{label} controller state differs from the profile sampling schedule",
                        {
                            "sequence_index": sample.get("sequence_index"),
                            "timestamp_seconds": sample.get("timestamp_seconds"),
                            "expected_state": expected_state.lower(),
                            "actual_state": actual_state,
                        },
                    )
                    break
                runtime_animation = str(
                    sample.get("sprite_animation" if label == "2D" else "animation_tree_node", "")
                ).lower()
                if not runtime_animation:
                    errors.append(f"{label}: sample {index} has no active animation identifier")
                    break
                if runtime_animation != expected_state.lower():
                    add_finding(
                        findings, f"{label}-ANIMATION-SCHEDULE-MISMATCH", "high",
                        f"{label} active animation differs from the profile sampling schedule",
                        {
                            "sequence_index": sample.get("sequence_index"),
                            "timestamp_seconds": sample.get("timestamp_seconds"),
                            "expected_animation": expected_state.lower(),
                            "actual_animation": runtime_animation,
                        },
                    )
                    break
        else:
            errors.append(
                f"{label}: reconstructed schedule has {len(schedule)} samples, "
                f"but metrics contain {len(samples)}"
            )
    states = ["idle", "walk", "run", "jump"]
    validate_state_sheets(output, "2d", states, errors)
    validate_state_sheets(output, "3d/perspective", states, errors)
    validate_state_sheets(output, "3d/multiview", states, errors)

    manifest_path = output / "review_manifest.json"
    prompt_path = output / "review_prompt.md"
    if not manifest_path.is_file() or not prompt_path.is_file():
        errors.append("review package is missing its manifest or prompt")
    else:
        review_manifest = load_json(manifest_path)
        if len(review_manifest.get("contact_sheets", [])) != 12:
            errors.append("review manifest must list all 12 contact sheets")
        for sheet in review_manifest.get("contact_sheets", []):
            if not Path(sheet.get("path", "")).is_file():
                errors.append(f"review manifest references a missing contact sheet: {sheet}")
        for group in review_manifest.get("image_groups", []):
            previous_index = -1
            previous_time = -1.0
            for frame in group.get("frames", []):
                index = int(frame.get("sequence_index", -1))
                timestamp = float(frame.get("timestamp_seconds", -1.0))
                if index <= previous_index or timestamp <= previous_time:
                    errors.append(f"review group {group.get('id')} is not chronologically ordered")
                    break
                if not Path(frame.get("path", "")).is_file():
                    errors.append(f"review group {group.get('id')} references a missing frame")
                    break
                previous_index = index
                previous_time = timestamp

    expected_multiview = int(capture.get("3d_multiview_samples_per_state", 3)) * len(
        capture.get("3d_segments", {})
    )
    actual_multiview = sum(1 for sample in samples_3d if sample.get("multiview_captured"))
    if actual_multiview != expected_multiview:
        errors.append(
            f"3D: expected {expected_multiview} synchronized multiview samples, got {actual_multiview}"
        )
    for sample in samples_3d:
        if sample.get("multiview_captured") and not Path(sample.get("multiview_image", "")).is_file():
            errors.append(f"3D: missing multiview image for sample {sample.get('sequence_index')}")

    atlas_path = project / "assets" / "2d" / "robot_atlas.json"
    if atlas_path.is_file():
        atlas = load_json(atlas_path)
        animations = atlas.get("animations", {})
        run_frames = animations.get("run", [])
        walk_frames = set(animations.get("walk", []))
        if profile.get("expectations", {}).get("2d_run_must_be_independent", False):
            if run_frames and set(run_frames).issubset(walk_frames):
                add_finding(
                    findings, "2D-RUN-REUSES-WALK", "warning",
                    "2D Run is not an independent animation",
                    {"run_frames": run_frames, "walk_frames": sorted(walk_frames)},
                )

    for state_name, should_loop in profile.get("expectations", {}).get("2d_loop", {}).items():
        state_samples = [
            sample for sample in samples_2d
            if str(sample.get("expected_state", "")).lower() == state_name.lower()
        ]
        if not state_samples:
            continue
        wrong_loop_mode = [
            sample for sample in state_samples
            if sample.get("sprite_animation_looping") is not bool(should_loop)
        ]
        if wrong_loop_mode:
            add_finding(
                findings, f"2D-{state_name.upper()}-LOOP-MODE-MISMATCH", "high",
                f"2D {state_name} loop mode does not match the profile",
                {
                    "expected_looping": bool(should_loop),
                    "observed_looping": wrong_loop_mode[0].get("sprite_animation_looping"),
                    "sequence_index": wrong_loop_mode[0].get("sequence_index"),
                },
            )
        if should_loop:
            stopped = [sample for sample in state_samples if not sample.get("sprite_is_playing", True)]
            if stopped:
                add_finding(
                    findings, f"2D-{state_name.upper()}-NOT-PLAYING", "high",
                    f"2D {state_name} animation is not playing during its scheduled segment",
                    {"sequence_index": stopped[0].get("sequence_index"),
                     "timestamp_seconds": stopped[0].get("timestamp_seconds")},
                )

    jump_airborne = [
        sample for sample in samples_2d
        if sample.get("state") == "jump" and not sample.get("actor_is_on_floor", True)
    ]
    jump_stopped_before_final_pose = [
        sample for sample in jump_airborne
        if not sample.get("sprite_is_playing", True)
        and int(sample.get("sprite_frame", 0)) < int(sample.get("sprite_frame_count", 1)) - 1
    ]
    if len(jump_stopped_before_final_pose) >= 2:
        add_finding(
            findings, "2D-JUMP-FREEZES-IN-AIR", "high",
            "2D Jump animation stops before reaching its final pose and before physical landing",
            {
                "airborne_samples": len(jump_airborne),
                "stopped_before_final_pose_samples": len(jump_stopped_before_final_pose),
                "first_stopped_time": jump_stopped_before_final_pose[0].get("timestamp_seconds"),
            },
        )
    jump_samples_2d = [
        sample for sample in samples_2d
        if str(sample.get("expected_state", "")).lower() == "jump"
    ]
    if jump_samples_2d and jump_samples_2d[-1].get("sprite_frame_count") is not None:
        last_jump_2d = jump_samples_2d[-1]
        final_frame = int(last_jump_2d["sprite_frame_count"]) - 1
        if (
            int(last_jump_2d.get("sprite_frame", -1)) != final_frame
            or bool(last_jump_2d.get("sprite_is_playing", True))
        ):
            add_finding(
                findings, "2D-JUMP-NOT-COMPLETED-BY-SEGMENT-END", "high",
                "2D Jump has not reached and held its final frame by the end of the scheduled Jump segment",
                {
                    "sequence_index": last_jump_2d.get("sequence_index"),
                    "timestamp_seconds": last_jump_2d.get("timestamp_seconds"),
                    "sprite_frame": last_jump_2d.get("sprite_frame"),
                    "final_frame": final_frame,
                    "sprite_is_playing": last_jump_2d.get("sprite_is_playing"),
                },
            )

    expected_loops = profile.get("expectations", {}).get("3d_loop", {})
    for clip_name, should_loop in expected_loops.items():
        observed = {
            sample.get("animation_loop_mode")
            for sample in samples_3d
            if sample.get("animation_tree_node") == clip_name
        }
        expected_mode = 1 if should_loop else 0
        if observed and any(mode != expected_mode for mode in observed):
            add_finding(
                findings, f"3D-{clip_name.upper()}-LOOP-MODE-MISMATCH", "high",
                f"3D {clip_name} loop mode does not match the profile",
                {
                    "expected_loop_mode": expected_mode,
                    "observed_loop_modes": sorted(mode for mode in observed if mode is not None),
                },
            )

    jump_samples_3d = [
        sample for sample in samples_3d
        if str(sample.get("expected_state", "")).lower() == "jump"
        and sample.get("animation_tree_node") == "Jump"
    ]
    if jump_samples_3d:
        last_jump_3d = jump_samples_3d[-1]
        position = last_jump_3d.get("animation_position_seconds")
        length = last_jump_3d.get("animation_length_seconds")
        if position is None or length is None or float(position) < float(length) - 0.02:
            add_finding(
                findings, "3D-JUMP-NOT-COMPLETED-BY-SEGMENT-END", "high",
                "3D Jump has not reached the end of its one-shot clip by the end of the scheduled Jump segment",
                {
                    "sequence_index": last_jump_3d.get("sequence_index"),
                    "timestamp_seconds": last_jump_3d.get("timestamp_seconds"),
                    "animation_position_seconds": position,
                    "animation_length_seconds": length,
                },
            )

    jump_landing_policy = profile["expectations"].get(
        "jump_state_after_landing", "hold_final_pose_until_segment_end"
    )
    if jump_landing_policy not in {
        "hold_final_pose_until_segment_end",
        "return_to_idle_on_landing",
    }:
        errors.append(f"unsupported jump_state_after_landing policy: {jump_landing_policy!r}")
    elif jump_landing_policy == "return_to_idle_on_landing":
        for label, samples in [("2D", samples_2d), ("3D", samples_3d)]:
            grounded_jump = [
                sample for sample in samples
                if str(sample.get("state", "")).lower() == "jump"
                and sample.get("actor_is_on_floor", False)
            ]
            if grounded_jump:
                add_finding(
                    findings, f"{label}-JUMP-STATE-AFTER-LANDING", "high",
                    f"{label} controller keeps Jump active after landing",
                    {
                        "sequence_index": grounded_jump[0].get("sequence_index"),
                        "timestamp_seconds": grounded_jump[0].get("timestamp_seconds"),
                        "grounded_jump_samples": len(grounded_jump),
                    },
                )
    advancing_during_capture = [
        sample for sample in samples_3d
        if sample.get("animation_advanced_during_capture", False)
    ]
    if advancing_during_capture:
        add_finding(
            findings, "3D-MULTIVIEW-NOT-FROZEN", "critical",
            "Animation advanced while the synchronized capture was being rendered",
            {"affected_samples": len(advancing_during_capture),
             "sample_indices": [sample.get("sequence_index") for sample in advancing_during_capture[:10]]},
        )

    if profile["expectations"].get("3d_facing_alignment_required", False):
        threshold = float(profile["expectations"].get("3d_facing_alignment_min", 0.9))
        locomotion = [
            sample for sample in samples_3d
            if sample.get("animation_tree_node") in {"Walk", "Run"}
            and sample.get("facing_alignment_dot") is not None
        ]
        if locomotion:
            average_alignment = sum(float(s["facing_alignment_dot"]) for s in locomotion) / len(locomotion)
            if average_alignment < threshold:
                add_finding(
                    findings, "3D-FACING-VELOCITY-MISMATCH", "high",
                    "3D model facing is not aligned with locomotion direction",
                    {"average_alignment_dot": round(average_alignment, 4),
                     "required_minimum": threshold, "samples": len(locomotion)},
                )

    for dimension, metrics in [("2d", metrics_2d), ("3d", metrics_3d)]:
        if metrics.get("sample_count") != len(metrics.get("samples", [])):
            errors.append(f"{dimension}: sample_count does not match samples array")
    if errors:
        print("BUNDLE_INVALID")
        for error in errors:
            print(f"- {error}")
        return 1

    report = {
        "schema_version": 1,
        "project_id": profile.get("project_id"),
        "output_dir": str(output),
        "structural_bundle_valid": True,
        "finding_count": len(findings),
        "findings": findings,
        "note": "Findings are deterministic QA signals, not an artistic verdict. Visual review remains required.",
    }
    (output / "findings.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    lines = [
        "# Visual QA findings",
        "",
        f"- Project: {profile.get('project_id')}",
        "- Structural bundle: VALID",
        f"- Deterministic findings: {len(findings)}",
        "",
        "These checks do not replace direct visual review of the captured images.",
        "",
    ]
    for finding in findings:
        lines.extend([
            f"## {finding['id']} — {finding['severity'].upper()}",
            "",
            finding["title"],
            "",
            "Evidence:",
            "",
            json.dumps(finding["evidence"], indent=2),
            "",
        ])
    if not findings:
        lines.append("No deterministic findings were triggered by the configured checks.")
    (output / "summary.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"BUNDLE_VALID | 2D={len(samples_2d)} samples | 3D={len(samples_3d)} samples | findings={len(findings)}")
    for finding in findings:
        print(f"FINDING | {finding['severity'].upper()} | {finding['id']} | {finding['title']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"BUNDLE_VALIDATION_ERROR: {exc}", file=sys.stderr)
        raise
