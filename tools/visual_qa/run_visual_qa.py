#!/usr/bin/env python3
"""Capture and package one asset's real Godot playback using the shared QA contract."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORKSPACE_ROOT = HERE.parents[1]
GODOT = WORKSPACE_ROOT / "tools" / "godot.sh"
GODOT_XVFB = WORKSPACE_ROOT / "tools" / "godot-xvfb.sh"
CAPTURE_SCRIPT = HERE / "capture_asset.gd"
CONTACT_SHEET_SCRIPT = HERE / "build_contact_sheet.gd"
sys.path.insert(0, str(HERE))
from validate_asset import validate as validate_manifest


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def git_status() -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1"], cwd=WORKSPACE_ROOT,
        text=True, capture_output=True, check=False,
    )
    return result.stdout.splitlines()


def safe_project_path(project_root: Path, relative: str) -> Path:
    value = Path(relative)
    if value.is_absolute() or ".." in value.parts:
        raise ValueError(f"dependency must stay inside project: {relative}")
    path = (project_root / value).resolve()
    path.relative_to(project_root.resolve())
    return path

def engine_identity(project_root: Path) -> dict:
    version = subprocess.run(
        [str(GODOT), "--headless", "--path", str(project_root), "--version"],
        cwd=WORKSPACE_ROOT, text=True, capture_output=True, check=False,
    )
    if version.returncode:
        raise RuntimeError("Godot version query failed: " + version.stderr[-1000:])
    binary = Path(os.environ.get("GODOT_BIN", WORKSPACE_ROOT / ".local-tools" /
                                 "godot-4.7.2" / "Godot_v4.7.2-stable_linux.x86_64"))
    if not binary.is_file():
        raise FileNotFoundError(f"Godot binary for cache identity not found: {binary}")
    return {
        "version": (version.stdout + version.stderr).strip(),
        "binary_sha256": sha256_file(binary),
        "godot_wrapper_sha256": sha256_file(GODOT),
        "xvfb_wrapper_sha256": sha256_file(GODOT_XVFB),
    }


def expected_samples(phase: dict, capture: dict) -> int:
    fps = int(capture["fps"])
    total = int(math.ceil(float(capture["duration_seconds"]) * fps))
    start, end = float(phase["start"]), float(phase["end"])
    return sum(1 for index in range(total) if index / fps + 1e-5 >= start and index / fps < end)


def phase_keys(manifest: dict, phase: dict, project_root: Path, engine: dict) -> tuple[str, str]:
    dependencies = set(manifest.get("dependencies", []))
    dependencies.update(phase.get("dependencies", []))
    dependencies.add(str(manifest["scene"])[6:])
    file_hashes = {}
    for relative in sorted(dependencies):
        path = safe_project_path(project_root, relative)
        if not path.is_file():
            raise FileNotFoundError(f"Missing capture dependency: {relative}")
        file_hashes[relative] = sha256_file(path)

    capture = manifest["capture"]
    capture_payload = {
        "schema_version": manifest["schema_version"],
        "asset_id": manifest["asset_id"],
        "kind": manifest["kind"],
        "scene": manifest["scene"],
        "actors": manifest["actors"],
        "phase": {key: phase[key] for key in ("id", "start", "end", "expected_clip") if key in phase},
        "capture": {
            key: capture[key] for key in (
                "fps", "duration_seconds", "resolution", "time_control", "multiview_samples_per_phase", "multiview"
            ) if key in capture
        },
        "dependencies": file_hashes,
        "capture_script_sha256": sha256_file(CAPTURE_SCRIPT),
        "engine": engine,
    }
    capture_key = stable_hash(capture_payload)
    sheet_payload = {
        "layout": {
            key: capture.get(key) for key in (
                "contact_sheet_max_frames", "contact_sheet_columns", "tile_size"
            )
        },
        "builder_sha256": sha256_file(CONTACT_SHEET_SCRIPT),
    }
    return capture_key, stable_hash(sheet_payload)


def png_dimensions(path: Path) -> tuple[int, int]:
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"invalid PNG: {path}")
    import struct
    return struct.unpack(">II", data[16:24])


def files_match(root: Path, files: dict) -> bool:
    if not isinstance(files, dict) or not files:
        return False
    for relative, digest in files.items():
        path = root / relative
        if not path.is_file() or sha256_file(path) != digest:
            return False
    return True

def load_cache(cache_dir: Path, capture_key: str, sheet_key: str,
               expected_count: int, kind: str, multiview_count: int) -> tuple[dict | None, bool]:
    marker = cache_dir / "cache-manifest.json"
    if not marker.is_file():
        return None, False
    try:
        record = json.loads(marker.read_text(encoding="utf-8"))
        if record.get("schema_version") != 1 or record.get("capture_key") != capture_key:
            return None, False
        if not files_match(cache_dir, record.get("capture_files", {})):
            return None, False
        metrics = json.loads((cache_dir / "metrics.json").read_text(encoding="utf-8"))
        samples = metrics.get("samples", [])
        if len(samples) != expected_count or metrics.get("sample_count") != expected_count:
            return None, False
        for sample in samples:
            image = cache_dir / str(sample.get("image", ""))
            if not image.is_file():
                return None, False
            if png_dimensions(image) != tuple(record.get("resolution", [])):
                return None, False
            multiview = sample.get("multiview_image")
            if multiview:
                path = cache_dir / str(multiview)
                if not path.is_file() or png_dimensions(path) != (1280, 720):
                    return None, False
        actual_multiview = sum(bool(sample.get("multiview_image")) for sample in samples)
        if actual_multiview != multiview_count:
            return None, False
        sheet_valid = (
            record.get("sheet_key") == sheet_key
            and files_match(cache_dir, record.get("sheet_files", {}))
        )
        return record, sheet_valid
    except Exception:
        return None, False


def copy_cache_files(cache_dir: Path, output_phase: Path, record: dict, include_sheets: bool) -> None:
    relatives = list(record["capture_files"])
    if include_sheets:
        relatives.extend(record.get("sheet_files", {}).keys())
    for relative in relatives:
        source = cache_dir / relative
        destination = output_phase / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    if include_sheets:
        rewrite_sheet_manifests(output_phase)

def rewrite_sheet_manifests(phase_dir: Path) -> None:
    for path in phase_dir.rglob("contact_sheet.json"):
        data = json.loads(path.read_text(encoding="utf-8"))
        parent = path.parent
        data["input_dir"] = str(parent / ("frames" if parent == phase_dir else ""))
        if parent.name == "multiview":
            data["input_dir"] = str(parent)
        data["contact_sheet"] = str(path.with_suffix(".png"))
        data["selected_dir"] = str(parent / "selected")
        data["metrics"] = str(phase_dir / "metrics.json")
        for frame in data.get("frames", []):
            frame["source"] = str(Path(data["input_dir"]) / Path(frame.get("source", "")).name)
            frame["selected"] = str(Path(data["selected_dir"]) / Path(frame.get("selected", "")).name)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def run_logged(name: str, command: list[str], cwd: Path, output: Path, timeout: int) -> dict:
    log_path = output / f"{name}.log"
    started = time.monotonic()
    with log_path.open("w", encoding="utf-8") as log:
        try:
            result = subprocess.run(
                command, cwd=cwd, stdout=log, stderr=subprocess.STDOUT,
                text=True, timeout=timeout, check=False,
            )
            code, error = result.returncode, None
        except subprocess.TimeoutExpired:
            code, error = -1, f"timed out after {timeout}s"
    duration = round(time.monotonic() - started, 3)
    step = {"name": name, "command": command, "exit_code": code,
            "duration_seconds": duration, "log": str(log_path), "error": error}
    print(f"[{'PASS' if code == 0 else 'FAIL'}] {name} | {duration:.1f}s | log={log_path}")
    if code:
        raise RuntimeError(f"{name} failed; see {log_path}")
    return step

def build_sheet_jobs(manifest: dict, phase_ids: list[str], output: Path) -> list[dict]:
    capture = manifest["capture"]
    width, height = capture.get("tile_size", [320, 180])
    jobs = []
    for phase_id in phase_ids:
        phase_dir = output / phase_id
        metrics = phase_dir / "metrics.json"
        jobs.append({
            "input_dir": str(phase_dir / "frames"),
            "output": str(phase_dir / "contact_sheet.png"),
            "prefix": "frame_",
            "max_frames": int(capture.get("contact_sheet_max_frames", 24)),
            "columns": int(capture.get("contact_sheet_columns", 6)),
            "tile_width": int(width), "tile_height": int(height),
            "fps": float(capture["fps"]), "metrics": str(metrics),
            "selected_dir": str(phase_dir / "selected"),
        })
        multiview_dir = phase_dir / "multiview"
        if multiview_dir.is_dir() and any(multiview_dir.glob("*.png")):
            jobs.append({
                "input_dir": str(multiview_dir),
                "output": str(multiview_dir / "contact_sheet.png"),
                "prefix": "frame_",
                "max_frames": int(capture.get("contact_sheet_max_frames", 24)),
                "columns": int(capture.get("contact_sheet_columns", 6)),
                "tile_width": int(width), "tile_height": int(height),
                "fps": float(capture["fps"]), "metrics": str(metrics),
                "selected_dir": str(multiview_dir / "selected"),
            })
    return jobs


def artifact_file_sets(phase_dir: Path) -> tuple[dict, dict]:
    capture_files, sheet_files = {}, {}
    for path in sorted(item for item in phase_dir.rglob("*") if item.is_file()):
        relative = path.relative_to(phase_dir).as_posix()
        digest = sha256_file(path)
        if relative == "metrics.json" or relative.startswith("frames/") or (
            relative.startswith("multiview/") and path.suffix.lower() == ".png"
            and path.name.startswith("frame_")
        ):
            capture_files[relative] = digest
        elif relative != "cache-manifest.json":
            sheet_files[relative] = digest
    return capture_files, sheet_files

def store_cache(phase_dir: Path, cache_dir: Path, capture_key: str, sheet_key: str,
                expected_count: int, resolution: list[int]) -> None:
    capture_files, sheet_files = artifact_file_sets(phase_dir)
    if not capture_files or not sheet_files:
        raise RuntimeError(f"incomplete capture/sheet bundle: {phase_dir}")
    temp = cache_dir.with_name(cache_dir.name + f".tmp-{os.getpid()}")
    if temp.exists():
        shutil.rmtree(temp)
    shutil.copytree(phase_dir, temp)
    record = {
        "schema_version": 1, "capture_key": capture_key, "sheet_key": sheet_key,
        "expected_sample_count": expected_count, "resolution": resolution,
        "capture_files": capture_files, "sheet_files": sheet_files,
    }
    (temp / "cache-manifest.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    cache_dir.parent.mkdir(parents=True, exist_ok=True)
    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    temp.replace(cache_dir)



def read_brief(manifest_path: Path) -> tuple[str, str]:
    path = manifest_path.parent / "brief.md"
    if not path.is_file():
        return "missing", "(No brief.md supplied.)"
    text = path.read_text(encoding="utf-8")
    body = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    body = "\n".join(line.strip() for line in body.splitlines()
                     if line.strip() and not line.lstrip().startswith("#"))
    if not body:
        return "empty", text
    if "brief-status: draft" in text or body.startswith("Describe the intended result and acceptance criteria"):
        return "draft", text
    # Presence is not semantic approval; GPT must still assess adequacy and the asset.
    return "provided", text


def make_review_package(manifest_path: Path, manifest: dict, output: Path,
                        phase_ids: list[str], cache_report: list[dict]) -> dict:
    brief_path = manifest_path.parent / "brief.md"
    brief_status, brief = read_brief(manifest_path)
    final_acceptance = "pending_visual_review" if brief_status == "provided" else "blocked_by_brief"
    module_text = []
    for module_id in manifest["qa_modules"]:
        module_path = WORKSPACE_ROOT / "qa" / "modules" / f"{module_id}.md"
        if not module_path.is_file():
            raise FileNotFoundError(f"QA module not found: {module_path}")
        module_text.append(module_path.read_text(encoding="utf-8"))

    phase_entries, contact_sheets = [], []
    for phase in manifest["phases"]:
        phase_id = phase["id"]
        if phase_id not in phase_ids:
            continue
        phase_dir = output / phase_id
        metrics = json.loads((phase_dir / "metrics.json").read_text(encoding="utf-8"))
        frames = []
        for sample in metrics.get("samples", []):
            frames.append({
                "sequence_index": sample["sequence_index"],
                "timestamp_seconds": sample["timestamp_seconds"],
                "image": str(phase_dir / sample["image"]),
                "multiview_image": str(phase_dir / sample["multiview_image"]) if sample.get("multiview_image") else None,
                "actors": sample.get("actors", []),
                "animation_clip": sample.get("animation_clip"),
            })
        phase_entries.append({
            "id": phase_id, "focus": phase["focus"], "expected_clip": phase.get("expected_clip"),
            "sample_count": len(frames), "frames": frames,
        })
        contact_sheets.append(str(phase_dir / "contact_sheet.png"))
        if (phase_dir / "multiview" / "contact_sheet.png").is_file():
            contact_sheets.append(str(phase_dir / "multiview" / "contact_sheet.png"))
    actor_entries = []
    for actor in manifest["actors"]:
        actor_entries.append({
            "id": actor["id"],
            "dimension": actor["dimension"],
            "forward_axis": actor["forward_axis"],
            "character": actor.get("character"),
        })
    review_manifest = {
        "schema_version": 1, "asset_id": manifest["asset_id"], "kind": manifest["kind"],
        "fps": manifest["capture"]["fps"], "capture": manifest["capture"], "actors": actor_entries,
        "phases": phase_entries, "contact_sheets": contact_sheets,
        "brief": {"path": str(brief_path), "status": brief_status}, "final_acceptance": final_acceptance,
    }
    (output / "review_manifest.json").write_text(json.dumps(review_manifest, indent=2), encoding="utf-8")

    prompt = [
        "# GPT Visual Review",
        f"Asset: {manifest['asset_id']} ({manifest['kind']})",
        "Review actual Godot runtime images in chronological order. The brief defines intent.",
        "Inspect the contact sheets for overview, then the individual PNGs. Do not infer artistic quality from technical PASS alone.",
        "For every finding cite actor ID, phase, frame index and timestamp. Separate visual observation, metric-backed evidence and hypothesis.",
        ("First judge whether the brief is sufficient; presence alone does not approve it. Report strengths, problems, uncertainties and valuable improvements; give a visual verdict only with adequate intent."
         if brief_status == "provided" else
         f"Brief is {brief_status}. Final artistic acceptance is BLOCKED. This is a technical draft capture; report observations but do not issue a final PASS."),
        "",
        "## Asset brief", brief,
        "## Phase-specific focus",
    ]
    for phase in phase_entries:
        prompt.append(f"- {phase['id']}: {phase['focus']}")
    prompt.extend(["", "## Capture actor configuration"])
    for actor in manifest["actors"]:
        prompt.append(
            f"- {actor['id']} ({actor['dimension']}), forward axis={actor['forward_axis']}"
        )
        character = actor.get("character")
        if character:
            feet = character.get("foot_bones", {})
            prompt.append(
                "  - Character capture: motion_mode=%s; skeleton=%s; feet left=%s, right=%s"
                % (
                    character.get("motion_mode", "unspecified"),
                    character.get("skeleton_path", "unspecified"),
                    feet.get("left", "unspecified"),
                    feet.get("right", "unspecified"),
                )
            )
            prompt.append(
                "  - Animation: player=%s; tree=%s; expected loops=%s; jump=%s; landing=%s"
                % (
                    character.get("animation_player_path", "not configured"),
                    character.get("animation_tree_path", "not configured"),
                    character.get("loop_states", []),
                    character.get("jump_state", "not configured"),
                    character.get("landing_policy", "not configured"),
                )
            )
    prompt.extend(["", "## Selected reusable QA modules", *module_text])
    (output / "review_prompt.md").write_text("\n\n".join(prompt) + "\n", encoding="utf-8")
    summary = [
        f"# Visual QA run — {manifest['asset_id']}",
        f"Kind: {manifest['kind']}",
        f"Phases captured: {', '.join(phase_ids)}",
        f"Brief: {brief_status}. Final acceptance: {final_acceptance}.",
        "Capture result: technical bundle complete. Artistic verdict requires GPT Visual Review.",
        "",
        "## Phase coverage",
    ]
    for phase in phase_entries:
        summary.append(f"- {phase['id']}: {phase['sample_count']} runtime frames — {phase['focus']}")
    summary.extend(["", "## Cache"])
    for item in cache_report:
        summary.append(f"- {item['phase']}: capture={item['capture']}, contact_sheets={item['sheets']}")
    (output / "summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")
    return review_manifest

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--asset", required=True, type=Path, help="Path to asset.qa.json")
    parser.add_argument("--phase", help="Capture only one phase ID")
    parser.add_argument("--force-rebuild", action="store_true", help="Ignore cache for selected phases")
    parser.add_argument("--output-dir", type=Path, help="Optional output directory (otherwise .fortis-state)")
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    started = time.monotonic()
    manifest_path = args.asset.resolve()
    output = None
    output_created = False
    steps, cache_report = [], []
    before_status = git_status()
    try:
        manifest = validate_manifest(manifest_path)
        project_root = (manifest_path.parent / manifest["project_root"]).resolve()
        engine = engine_identity(project_root)
        phases = [phase for phase in manifest["phases"] if args.phase is None or phase["id"] == args.phase]
        if not phases:
            raise ValueError(f"unknown phase: {args.phase}")
        phase_ids = [phase["id"] for phase in phases]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        output = args.output_dir.resolve() if args.output_dir else (
            project_root / ".fortis-state" / "visual-qa" / manifest["asset_id"] / f"run-{timestamp}"
        )
        if output.exists():
            raise FileExistsError(f"refusing to overwrite output: {output}")
        output.mkdir(parents=True)
        output_created = True
        capture = manifest["capture"]

        missing_capture, sheets_to_build, phase_data = [], [], {}
        cache_root = project_root / ".fortis-state" / "visual-qa" / "asset-cache" / manifest["asset_id"]
        for phase in phases:
            capture_key, sheet_key = phase_keys(manifest, phase, project_root, engine)
            expected = expected_samples(phase, capture)
            multiview = min(int(capture.get("multiview_samples_per_phase", 0)), expected) if manifest["kind"] == "3d_scene" else 0
            cache_dir = cache_root / phase["id"] / capture_key
            record, sheet_valid = (None, False) if args.force_rebuild else load_cache(
                cache_dir, capture_key, sheet_key, expected, manifest["kind"], multiview,
            )
            phase_dir = output / phase["id"]
            phase_dir.mkdir(parents=True)
            if record is not None:
                copy_cache_files(cache_dir, phase_dir, record, sheet_valid)
                capture_status = "reused"
            else:
                missing_capture.append(phase["id"])
                capture_status = "captured"
                sheet_valid = False
            if not sheet_valid:
                sheets_to_build.append(phase["id"])
            phase_data[phase["id"]] = {
                "capture_key": capture_key, "sheet_key": sheet_key,
                "cache_dir": cache_dir, "expected": expected,
                "capture_status": capture_status,
            }
            cache_report.append({
                "phase": phase["id"], "capture": capture_status,
                "sheets": "reused" if sheet_valid else "rebuild",
            })
        if missing_capture:
            # Import source assets (GLB, textures, etc.) before a headless runtime
            # script tries to preload their generated Godot resources.
            import_command = [
                str(GODOT), "--headless", "--path", str(project_root), "--import",
            ]
            steps.append(run_logged("asset-import", import_command, WORKSPACE_ROOT, output, args.timeout))
            command = [
                str(GODOT_XVFB), "--path", str(project_root), "--script", str(CAPTURE_SCRIPT),
                "--", "--manifest", str(manifest_path), "--output-dir", str(output),
                "--phases", ",".join(missing_capture),
            ]
            steps.append(run_logged("runtime-capture", command, WORKSPACE_ROOT, output, args.timeout))

        if sheets_to_build:
            jobs = build_sheet_jobs(manifest, sheets_to_build, output)
            jobs_path = output / ".contact-sheet-jobs.json"
            jobs_path.write_text(json.dumps(jobs, indent=2), encoding="utf-8")
            command = [
                str(GODOT), "--headless", "--path", str(project_root),
                "--script", str(CONTACT_SHEET_SCRIPT), "--", "--jobs-json", str(jobs_path),
            ]
            steps.append(run_logged("contact-sheets", command, WORKSPACE_ROOT, output, args.timeout))
        for phase in phases:
            phase_id = phase["id"]
            phase_dir = output / phase_id
            metrics = json.loads((phase_dir / "metrics.json").read_text(encoding="utf-8"))
            expected = phase_data[phase_id]["expected"]
            if metrics.get("sample_count") != expected or len(metrics.get("samples", [])) != expected:
                raise RuntimeError(f"{phase_id}: expected {expected} frames, got {metrics.get('sample_count')}")
            for sample in metrics.get("samples", []):
                frame_path = phase_dir / str(sample.get("image", ""))
                if not frame_path.is_file() or png_dimensions(frame_path) != tuple(capture["resolution"]):
                    raise RuntimeError(f"{phase_id}: missing or incorrectly sized runtime frame: {frame_path}")
                multiview = sample.get("multiview_image")
                if multiview:
                    multiview_path = phase_dir / str(multiview)
                    if not multiview_path.is_file() or png_dimensions(multiview_path) != (1280, 720):
                        raise RuntimeError(f"{phase_id}: missing or incorrectly sized multiview frame: {multiview_path}")
            if not (phase_dir / "contact_sheet.png").is_file():
                raise RuntimeError(f"{phase_id}: contact sheet missing")
            rewrite_sheet_manifests(phase_dir)
        review_manifest = make_review_package(manifest_path, manifest, output, phase_ids, cache_report)
        after_status = git_status()
        git_unchanged = before_status == after_status
        cache_committed = False
        if git_unchanged:
            for phase in phases:
                phase_id = phase["id"]
                item = phase_data[phase_id]
                store_cache(
                    output / phase_id, item["cache_dir"], item["capture_key"], item["sheet_key"],
                    item["expected"], list(capture["resolution"]),
                )
            cache_committed = True

        run_report = {
            "schema_version": 1, "asset_id": manifest["asset_id"], "kind": manifest["kind"],
            "phases": phase_ids, "all_steps_passed": True, "git_status_unchanged": git_unchanged,
            "brief_status": review_manifest["brief"]["status"], "final_acceptance": review_manifest["final_acceptance"],
            "cache_committed": cache_committed, "cache": cache_report, "steps": steps,
            "output_dir": str(output), "review_manifest": str(output / "review_manifest.json"),
            "elapsed_seconds": round(time.monotonic() - started, 3),
        }
        (output / "run.json").write_text(json.dumps(run_report, indent=2), encoding="utf-8")
        print(f"ASSET_VISUAL_QA_PASS | {manifest['asset_id']} | phases={len(phase_ids)} | brief={review_manifest['brief']['status']} | final={review_manifest['final_acceptance']} | output={output}")
        return 0
    except Exception as exc:
        if output_created and output is not None and output.is_dir():
            failure = {
                "all_steps_passed": False, "error": str(exc),
                "steps": steps, "cache": cache_report,
                "output_dir": str(output), "elapsed_seconds": round(time.monotonic() - started, 3),
            }
            (output / "run.json").write_text(json.dumps(failure, indent=2), encoding="utf-8")
        print(f"ASSET_VISUAL_QA_FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
