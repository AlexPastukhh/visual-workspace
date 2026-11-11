#!/usr/bin/env python3
"""Run the complete, read-only Visual QA capture workflow for this Godot project."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from state_cache import compute_state_keys, sha256_file

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSPACE_ROOT = PROJECT_ROOT.parent.parent
PROFILE_DEFAULT = PROJECT_ROOT / "tools" / "visual_qa" / "profile.json"
GODOT = WORKSPACE_ROOT / "tools" / "godot.sh"
GODOT_XVFB = WORKSPACE_ROOT / "tools" / "godot-xvfb.sh"
CAPTURE_2D = "res://tools/visual_qa/capture_2d.gd"
CAPTURE_3D = "res://tools/visual_qa/capture_3d_multiview.gd"
CONTACT_SHEET = str(WORKSPACE_ROOT / "tools" / "visual_qa" / "build_contact_sheet.gd")
CACHE_ROOT = PROJECT_ROOT / ".fortis-state" / "visual-qa" / "state-cache"
CACHE_INDEX = CACHE_ROOT / "index.json"
STATES = ("idle", "walk", "run", "jump")


def git_status():
    result = subprocess.run(
        ["git", "status", "--porcelain=v1"],
        cwd=WORKSPACE_ROOT, text=True, capture_output=True, check=False,
    )
    return result.stdout.splitlines()


def run_step(name, command, cwd, log_path, timeout):
    started = time.monotonic()
    exit_code = -1
    error = None
    with log_path.open("w", encoding="utf-8") as log:
        try:
            result = subprocess.run(
                [str(part) for part in command], cwd=cwd,
                stdout=log, stderr=subprocess.STDOUT, text=True,
                timeout=timeout, check=False,
            )
            exit_code = result.returncode
        except subprocess.TimeoutExpired:
            error = f"Timed out after {timeout} seconds"
        except Exception as exc:
            error = repr(exc)
    duration = round(time.monotonic() - started, 3)
    status = "PASS" if exit_code == 0 else "FAIL"
    print(f"[{status}] {name} | {duration:.1f}s | exit={exit_code} | log={log_path}")
    return {
        "name": name, "command": [str(part) for part in command],
        "exit_code": exit_code, "duration_seconds": duration,
        "log": str(log_path), "error": error,
    }


def test_input_fingerprint():
    """Hash project inputs, imported Godot artifacts, and the selected engine wrapper/version."""
    digest = hashlib.sha256()
    excluded_dirs = {".git", ".godot", ".fortis-state", "__pycache__"}
    file_count = 0
    for path in sorted(PROJECT_ROOT.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(PROJECT_ROOT)
        if any(part in excluded_dirs for part in relative.parts):
            continue
        if relative.parts[:2] == ("tests", "results"):
            continue
        digest.update(relative.as_posix().encode("utf-8") + b"\0")
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)
        file_count += 1

    imported_dir = PROJECT_ROOT / ".godot" / "imported"
    imported_files = sorted(path for path in imported_dir.rglob("*") if path.is_file()) if imported_dir.is_dir() else []
    if not imported_files:
        return None
    for path in imported_files:
        relative = path.relative_to(PROJECT_ROOT / ".godot")
        digest.update(b"godot-imported/" + relative.as_posix().encode("utf-8") + b"\0")
        with path.open("rb") as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(chunk)

    wrapper = WORKSPACE_ROOT / "tools" / "godot.sh"
    if not wrapper.is_file():
        return None
    digest.update(b"godot-wrapper\0")
    digest.update(wrapper.read_bytes())
    version = subprocess.run(
        [str(GODOT), "--headless", "--version"],
        cwd=PROJECT_ROOT, text=True, capture_output=True, check=False,
    )
    if version.returncode != 0:
        return None
    engine_version = (version.stdout + version.stderr).strip()
    digest.update(engine_version.encode("utf-8"))
    digest.update(b"godot-bin-override\0")
    digest.update(os.environ.get("GODOT_BIN", "").encode("utf-8"))
    return {
        "key": digest.hexdigest(),
        "engine_version": engine_version,
        "project_file_count": file_count,
        "imported_file_count": len(imported_files),
    }


def run_cached_tests(output, timeout, force=False):
    tests = PROJECT_ROOT / "tools" / "run_tests.sh"
    log_path = output / "01-static-tests.log"
    cache_path = PROJECT_ROOT / ".fortis-state" / "visual-qa" / "test-cache.json"
    fingerprint = test_input_fingerprint()
    cache = {}
    if cache_path.is_file():
        try:
            cache = json.loads(cache_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cache = {}
    if not force and fingerprint and cache.get("schema_version") == 1 and cache.get("fingerprint") == fingerprint["key"]:
        print("[CACHED] structural-and-smoke-tests | inputs and imported resources unchanged")
        return {
            "name": "structural-and-smoke-tests",
            "command": [str(tests)],
            "exit_code": 0,
            "duration_seconds": 0.0,
            "log": None,
            "error": None,
            "cached": True,
            "cache_key": fingerprint["key"],
            "validated_at_utc": cache.get("validated_at_utc"),
            "engine_version": fingerprint["engine_version"],
        }

    step = run_step(
        "structural-and-smoke-tests", [tests], PROJECT_ROOT, log_path, timeout,
    )
    step["cached"] = False
    step["cache_key"] = fingerprint["key"] if fingerprint else None
    if fingerprint:
        step["engine_version"] = fingerprint["engine_version"]
    if step["exit_code"] == 0 and fingerprint:
        post_test_fingerprint = test_input_fingerprint()
        if post_test_fingerprint:
            fingerprint = post_test_fingerprint
            step["cache_key"] = fingerprint["key"]
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_data = {
            "schema_version": 1,
            "fingerprint": fingerprint["key"],
            "validated_at_utc": datetime.now(timezone.utc).isoformat(),
            "engine_version": fingerprint["engine_version"],
            "project_file_count": fingerprint["project_file_count"],
            "imported_file_count": fingerprint["imported_file_count"],
        }
        temporary = cache_path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(cache_data, indent=2), encoding="utf-8")
        temporary.replace(cache_path)
        step["cache_written"] = str(cache_path)
    return step


def engine_identity():
    version = subprocess.run(
        [str(GODOT), "--headless", "--version"],
        cwd=PROJECT_ROOT, text=True, capture_output=True, check=False,
    )
    if version.returncode != 0:
        return None
    if os.environ.get("GODOT_BIN"):
        binary = Path(os.environ["GODOT_BIN"])
    else:
        binary = WORKSPACE_ROOT / ".local-tools" / "godot-4.7.2" / "Godot_v4.7.2-stable_linux.x86_64"
    if not binary.is_file():
        return None
    return {
        "version": (version.stdout + version.stderr).strip(),
        "binary_sha256": sha256_file(binary),
        "godot_wrapper_sha256": sha256_file(WORKSPACE_ROOT / "tools" / "godot.sh"),
        "xvfb_wrapper_sha256": sha256_file(WORKSPACE_ROOT / "tools" / "godot-xvfb.sh"),
        "renderer_environment": {
            key: os.environ.get(key, "")
            for key in (
                "LIBGL_ALWAYS_SOFTWARE", "GALLIUM_DRIVER",
                "MESA_LOADER_DRIVER_OVERRIDE", "MESA_GL_VERSION_OVERRIDE",
                "MESA_GLSL_VERSION_OVERRIDE",
            )
        },
    }


def load_state_cache_index():
    if not CACHE_INDEX.is_file():
        return {"schema_version": 1, "project_id": "game-animation-mvp", "states": {}}
    try:
        value = json.loads(CACHE_INDEX.read_text(encoding="utf-8"))
        if (
            value.get("schema_version") != 1
            or value.get("project_id") != "game-animation-mvp"
            or not isinstance(value.get("states"), dict)
        ):
            raise ValueError("unsupported cache index schema")
        return value
    except Exception as exc:
        print(f"[CACHE INVALID] state cache index will be ignored: {exc}")
        return {"schema_version": 1, "project_id": "game-animation-mvp", "states": {}}


def safe_cache_path(root, relative):
    value = Path(str(relative))
    if value.is_absolute() or ".." in value.parts:
        return None
    candidate = (root / value).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate


def files_match(artifact_dir, expected_files):
    if not isinstance(expected_files, dict) or not expected_files:
        return False
    for relative, expected_hash in expected_files.items():
        path = safe_cache_path(artifact_dir, relative)
        if path is None or not path.is_file():
            return False
        try:
            if sha256_file(path) != expected_hash:
                return False
        except OSError:
            return False
    return True


def png_dimensions(path):
    data = path.read_bytes()[:24]
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"Invalid PNG: {path}")
    import struct
    return struct.unpack(">II", data[16:24])


def rewrite_contact_sheet_manifests(output, dimension, state):
    bases = [output / "2d" / state] if dimension == "2d" else [
        output / "3d" / "perspective" / state,
        output / "3d" / "multiview" / state,
    ]
    for base in bases:
        manifest_path = base / "contact_sheet.json"
        if not manifest_path.is_file():
            continue
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["input_dir"] = str(base)
        manifest["contact_sheet"] = str(base / "contact_sheet.png")
        manifest["selected_dir"] = str(base / "selected")
        for frame in manifest.get("frames", []):
            frame["source"] = str(base / Path(frame.get("source", "")).name)
            frame["selected"] = str(base / "selected" / Path(frame.get("selected", "")).name)
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def expected_state_counts(profile, dimension, state):
    capture = profile["capture"]
    count = int(capture[f"{dimension}_samples_per_segment"][state])
    multiview = (
        int(capture.get("3d_multiview_samples_per_state", 0))
        if dimension == "3d" else 0
    )
    return count, multiview


def load_cached_state(index, dimension, state, keys, profile, output):
    cache_record = index.get("states", {}).get(f"{dimension}:{state}")
    if not isinstance(cache_record, dict) or cache_record.get("capture_key") != keys["capture_key"]:
        return None
    artifact_dir = safe_cache_path(CACHE_ROOT, cache_record.get("artifact_dir", ""))
    if artifact_dir is None or not artifact_dir.is_dir():
        return None
    manifest_path = artifact_dir / "manifest.json"
    metrics_path = artifact_dir / "metrics.json"
    if not manifest_path.is_file() or not metrics_path.is_file():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if (
            manifest.get("schema_version") != 1
            or manifest.get("dimension") != dimension
            or manifest.get("state") != state
            or manifest.get("capture_key") != keys["capture_key"]
        ):
            return None
        if not files_match(artifact_dir, manifest.get("capture_files", {})):
            return None
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        samples = metrics.get("samples", [])
        expected_count, expected_multiview = expected_state_counts(profile, dimension, state)
        if len(samples) != expected_count or metrics.get("sample_count") != expected_count:
            return None
        if any(str(sample.get("expected_state", "")).lower() != state for sample in samples):
            return None
        for sample in samples:
            image_relative = sample.get("image")
            image_path = safe_cache_path(artifact_dir, image_relative)
            if image_path is None or not image_path.is_file():
                return None
            width, height = png_dimensions(image_path)
            if dimension == "2d" and (width, height) != (1280, 720):
                return None
            if dimension == "3d" and (width, height) != (640, 360):
                return None
            if dimension == "3d" and sample.get("multiview_captured"):
                multiview_relative = sample.get("multiview_image")
                multiview_path = safe_cache_path(artifact_dir, multiview_relative)
                if multiview_path is None or not multiview_path.is_file():
                    return None
                if png_dimensions(multiview_path) != (1280, 720):
                    return None
        actual_multiview = sum(bool(sample.get("multiview_captured")) for sample in samples)
        if actual_multiview != expected_multiview:
            return None

        # Capture frames and metrics are reusable independently of contact-sheet settings.
        for relative in manifest["capture_files"]:
            if relative == "metrics.json":
                continue
            source = safe_cache_path(artifact_dir, relative)
            destination = output / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)

        for sample in samples:
            sample["image"] = str(output / sample["image"])
            if sample.get("multiview_image"):
                sample["multiview_image"] = str(output / sample["multiview_image"])

        sheet_valid = (
            cache_record.get("sheet_key") == keys["sheet_key"]
            and files_match(artifact_dir, manifest.get("sheet_files", {}))
        )
        if sheet_valid:
            required_sheets = (
                [f"2d/{state}/contact_sheet.png", f"2d/{state}/contact_sheet.json"]
                if dimension == "2d" else [
                    f"3d/perspective/{state}/contact_sheet.png",
                    f"3d/perspective/{state}/contact_sheet.json",
                    f"3d/multiview/{state}/contact_sheet.png",
                    f"3d/multiview/{state}/contact_sheet.json",
                ]
            )
            if any(relative not in manifest["sheet_files"] for relative in required_sheets):
                sheet_valid = False
        if sheet_valid:
            for relative in manifest["sheet_files"]:
                source = safe_cache_path(artifact_dir, relative)
                destination = output / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            rewrite_contact_sheet_manifests(output, dimension, state)

        return {
            "metrics": metrics,
            "sheets_cached": sheet_valid,
            "artifact_dir": str(artifact_dir),
        }
    except Exception:
        return None


def merge_dimension_metrics(dimension, state_results, profile, output):
    state_metrics = [state_results[(dimension, state)]["metrics"] for state in STATES]
    base = dict(state_metrics[0])
    samples = []
    for metrics in state_metrics:
        samples.extend(metrics.get("samples", []))
    samples.sort(key=lambda item: float(item.get("timestamp_seconds", -1.0)))
    indices = [int(sample.get("sequence_index", -1)) for sample in samples]
    if len(indices) != len(set(indices)):
        raise ValueError(f"{dimension}: duplicate sequence indices while merging state captures")
    base["samples"] = samples
    base["sample_count"] = len(samples)
    base["captured_states"] = list(STATES)
    base["sampling_schedule"] = profile["capture"][f"{dimension}_segments"]
    if dimension == "3d":
        base["multiview_sample_count"] = sum(
            bool(sample.get("multiview_captured")) for sample in samples
        )
    metrics_path = output / dimension / "metrics.json"
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(base, indent=2), encoding="utf-8")
    return base


def state_sheet_relative_paths(dimension, state, output):
    bases = [Path("2d") / state] if dimension == "2d" else [
        Path("3d") / "perspective" / state,
        Path("3d") / "multiview" / state,
    ]
    result = []
    for base in bases:
        result.extend([
            base / "contact_sheet.png",
            base / "contact_sheet.json",
        ])
        selected = base / "selected"
        if (output / selected).is_dir():
            result.extend(
                (base / "selected" / item.name)
                for item in sorted((output / selected).glob("*.png"))
            )
    return result


def store_state_artifact(dimension, state, keys, merged_metrics, output):
    samples = [
        sample for sample in merged_metrics["samples"]
        if str(sample.get("expected_state", "")).lower() == state
    ]
    expected_count = len(samples)
    if expected_count < 1:
        raise ValueError(f"Cannot cache empty state {dimension}/{state}")

    state_parent = CACHE_ROOT / "artifacts" / dimension / state
    state_parent.mkdir(parents=True, exist_ok=True)
    token = (
        f"{keys['capture_key'][:12]}-{keys['sheet_key'][:12]}-"
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}"
    )
    temporary = state_parent / (token + ".tmp")
    final = state_parent / token
    if temporary.exists():
        shutil.rmtree(temporary)
    temporary.mkdir(parents=True)

    capture_files = {"metrics.json": ""}
    sheet_files = {}
    state_metrics = dict(merged_metrics)
    state_metrics["samples"] = []
    state_metrics["sample_count"] = len(samples)
    state_metrics["captured_states"] = [state]
    if dimension == "3d":
        state_metrics["multiview_sample_count"] = sum(
            bool(sample.get("multiview_captured")) for sample in samples
        )

    try:
        for original in samples:
            sample = dict(original)
            for field in ("image", "multiview_image"):
                value = sample.get(field)
                if not value:
                    continue
                source = Path(value)
                if not source.is_absolute():
                    source = output / source
                relative = source.resolve().relative_to(output.resolve())
                destination = temporary / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
                sample[field] = relative.as_posix()
                capture_files[relative.as_posix()] = sha256_file(destination)
            state_metrics["samples"].append(sample)

        metrics_path = temporary / "metrics.json"
        metrics_path.write_text(json.dumps(state_metrics, indent=2), encoding="utf-8")
        capture_files["metrics.json"] = sha256_file(metrics_path)

        for relative in state_sheet_relative_paths(dimension, state, output):
            source = output / relative
            if not source.is_file():
                raise FileNotFoundError(f"Cannot cache missing contact-sheet artifact: {source}")
            destination = temporary / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            sheet_files[relative.as_posix()] = sha256_file(destination)

        if dimension == "2d":
            selected_count = sum(
                1 for path in sheet_files if path.startswith(f"2d/{state}/selected/")
            )
            required = [f"2d/{state}/contact_sheet.png", f"2d/{state}/contact_sheet.json"]
        else:
            selected_count = sum(
                1 for path in sheet_files if path.startswith(f"3d/perspective/{state}/selected/")
            ) + sum(
                1 for path in sheet_files if path.startswith(f"3d/multiview/{state}/selected/")
            )
            required = [
                f"3d/perspective/{state}/contact_sheet.png",
                f"3d/perspective/{state}/contact_sheet.json",
                f"3d/multiview/{state}/contact_sheet.png",
                f"3d/multiview/{state}/contact_sheet.json",
            ]
        if selected_count < 4 or any(path not in sheet_files for path in required):
            raise ValueError(f"Incomplete contact-sheet artifacts for {dimension}/{state}")

        manifest = {
            "schema_version": 1,
            "dimension": dimension,
            "state": state,
            "capture_key": keys["capture_key"],
            "sheet_key": keys["sheet_key"],
            "sample_count": expected_count,
            "multiview_sample_count": state_metrics.get("multiview_sample_count", 0),
            "capture_files": capture_files,
            "sheet_files": sheet_files,
        }
        (temporary / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        temporary.rename(final)
    except Exception:
        shutil.rmtree(temporary, ignore_errors=True)
        raise

    return {
        "capture_key": keys["capture_key"],
        "sheet_key": keys["sheet_key"],
        "artifact_dir": final.relative_to(CACHE_ROOT).as_posix(),
        "updated_at_utc": datetime.now(timezone.utc).isoformat(),
        "sample_count": expected_count,
        "multiview_sample_count": state_metrics.get("multiview_sample_count", 0),
    }


def commit_state_cache_index(index, pending_records):
    if not pending_records:
        return
    old_directories = []
    for key, record in pending_records.items():
        old = index["states"].get(key)
        if isinstance(old, dict) and old.get("artifact_dir") != record.get("artifact_dir"):
            old_path = safe_cache_path(CACHE_ROOT, old.get("artifact_dir", ""))
            if old_path is not None:
                old_directories.append(old_path)
        index["states"][key] = record
    CACHE_ROOT.mkdir(parents=True, exist_ok=True)
    temporary = CACHE_INDEX.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(index, indent=2), encoding="utf-8")
    os.replace(temporary, CACHE_INDEX)
    for old_path in old_directories:
        shutil.rmtree(old_path, ignore_errors=True)


def synthetic_cached_step(name, details=None):
    print(f"[CACHED] {name}")
    return {
        "name": name, "command": [], "exit_code": 0,
        "duration_seconds": 0.0, "log": None, "error": None,
        "cached": True, "details": details or {},
    }


def build_sheet_jobs(output, profile, states_to_build):
    capture = profile["capture"]
    jobs = []
    for dimension, state in states_to_build:
        channels = [("", "2d")] if dimension == "2d" else [
            ("perspective", "3d-perspective"),
            ("multiview", "3d-multiview"),
        ]
        for channel, _label in channels:
            state_dir = output / dimension
            if channel:
                state_dir = state_dir / channel
            state_dir = state_dir / state
            jobs.append({
                "input_dir": str(state_dir),
                "output": str(state_dir / "contact_sheet.png"),
                "prefix": f"{state}_",
                "max_frames": int(capture.get("contact_sheet_max_frames", 24)),
                "columns": int(capture.get("contact_sheet_columns", 6)),
                "tile_width": int(capture.get("tile_width", 320)),
                "tile_height": int(capture.get("tile_height", 180)),
                "metrics": str(output / dimension / "metrics.json"),
                "selected_dir": str(state_dir / "selected"),
            })
    return jobs


def write_review_package(output, profile, profile_path):
    sources = [
        ("2d", "", "2d", "image"),
        ("3d", "perspective", "3d-perspective", "image"),
        ("3d", "multiview", "3d-multiview", "multiview_image"),
    ]
    groups = []
    contact_sheets = []
    for dimension, channel, label, image_key in sources:
        metrics_path = output / dimension / "metrics.json"
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        frames = []
        for sample in metrics.get("samples", []):
            if channel == "multiview" and not sample.get("multiview_captured"):
                continue
            image_path = Path(sample.get(image_key, ""))
            if not image_path.is_file():
                raise FileNotFoundError(f"Review image missing: {image_path}")
            frames.append({
                "sequence_index": sample.get("sequence_index"),
                "timestamp_seconds": sample.get("timestamp_seconds"),
                "expected_state": sample.get("expected_state"),
                "actual_state": sample.get("state"),
                "path": str(image_path),
            })
        frames.sort(key=lambda item: int(item["sequence_index"]))
        groups.append({
            "id": label, "frame_count": len(frames),
            "metrics_path": str(metrics_path), "frames": frames,
        })
        for state in ["idle", "walk", "run", "jump"]:
            state_dir = output / dimension
            if channel:
                state_dir = state_dir / channel
            sheet = state_dir / state / "contact_sheet.png"
            if not sheet.is_file():
                raise FileNotFoundError(f"Contact sheet missing: {sheet}")
            contact_sheets.append({"id": f"{label}-{state}", "path": str(sheet)})

    prompt_source = PROJECT_ROOT / "tools" / "visual_qa" / "REVIEW_PROMPT.md"
    prompt_output = output / "review_prompt.md"
    prompt_output.write_text(prompt_source.read_text(encoding="utf-8"), encoding="utf-8")
    manifest = {
        "schema_version": 1,
        "project_id": profile.get("project_id"),
        "output_dir": str(output),
        "profile_path": str(profile_path),
        "review_prompt_path": str(prompt_output),
        "recommended_image_batch_size": 4,
        "contact_sheets": contact_sheets,
        "image_groups": groups,
        "review_order": [
            "Inspect all contact sheets first.",
            "Inspect 2D runtime frames in chronological order.",
            "Inspect 3D perspective frames in chronological order.",
            "Inspect synchronized 3D multiview frames in chronological order.",
            "Compare visual observations with metrics and deterministic findings.",
        ],
    }
    manifest_path = output / "review_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"REVIEW_PACKAGE_READY | groups={len(groups)} | sheets={len(contact_sheets)} | manifest={manifest_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", type=Path, default=PROFILE_DEFAULT)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument(
        "--force-tests", action="store_true",
        help="Run structural/smoke tests even when their input fingerprint is unchanged.",
    )
    parser.add_argument(
        "--force-rebuild", action="store_true",
        help="Ignore all state caches and regenerate every capture and contact sheet.",
    )
    args = parser.parse_args()
    profile_path = args.profile.resolve()
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = args.output_dir.resolve() if args.output_dir else (
        PROJECT_ROOT / ".fortis-state" / "visual-qa" / f"run-{timestamp}"
    )
    if output.exists():
        raise FileExistsError(f"Output directory already exists: {output}")
    output.mkdir(parents=True)
    before_status = git_status()
    steps = []
    state_cache_report = {
        "mode": "force-rebuild" if args.force_rebuild else "incremental",
        "states": [],
        "captured_state_count": 0,
        "reused_capture_state_count": 0,
        "rebuilt_sheet_state_count": 0,
        "reused_sheet_state_count": 0,
        "cache_committed": False,
    }
    pending_records = {}
    cache_index = load_state_cache_index()
    cache_enabled = True
    reuse_cache = not args.force_rebuild
    try:
        identity = engine_identity()
        if identity is None:
            cache_enabled = False
            print("[CACHE DISABLED] Could not establish a stable Godot engine identity.")
            state_keys = {}
        else:
            state_keys = compute_state_keys(
                PROJECT_ROOT, WORKSPACE_ROOT, profile, identity,
            )
    except Exception as exc:
        cache_enabled = False
        state_keys = {}
        print(f"[CACHE DISABLED] Dependency fingerprinting failed safely: {exc}")

    # Full project smoke tests retain their own broader fingerprint. Force Rebuild
    # explicitly bypasses that cache as well.
    steps.append(run_cached_tests(
        output, args.timeout,
        force=(args.force_tests or args.force_rebuild),
    ))

    state_results = {}
    states_needing_capture = {"2d": [], "3d": []}
    states_needing_sheets = []
    for dimension in ("2d", "3d"):
        for state in STATES:
            keys = state_keys.get((dimension, state)) if cache_enabled else None
            cached = None
            if keys is not None and reuse_cache:
                cached = load_cached_state(
                    cache_index, dimension, state, keys, profile, output,
                )
            if cached is None:
                states_needing_capture[dimension].append(state)
                state_cache_report["captured_state_count"] += 1
                sheet_cached = False
                metrics = None
                capture_status = "captured"
            else:
                metrics = cached["metrics"]
                capture_status = "reused"
                state_cache_report["reused_capture_state_count"] += 1
                sheet_cached = cached["sheets_cached"]
            if not sheet_cached:
                states_needing_sheets.append((dimension, state))
                state_cache_report["rebuilt_sheet_state_count"] += 1
            else:
                state_cache_report["reused_sheet_state_count"] += 1
            state_results[(dimension, state)] = {
                "metrics": metrics,
                "capture_status": capture_status,
                "sheet_status": "reused" if sheet_cached else "rebuild",
                "keys": keys,
            }
            state_cache_report["states"].append({
                "dimension": dimension,
                "state": state,
                "capture": capture_status,
                "contact_sheets": "reused" if sheet_cached else "rebuild",
                "capture_key": keys["capture_key"] if keys else None,
                "sheet_key": keys["sheet_key"] if keys else None,
            })

    try:
        fixed_fps = int(profile["capture"].get("fixed_fps", 24))
        for dimension, capture_script, log_name in (
            ("2d", CAPTURE_2D, "02-capture-2d.log"),
            ("3d", CAPTURE_3D, "03-capture-3d.log"),
        ):
            selected = states_needing_capture[dimension]
            if not selected:
                steps.append(synthetic_cached_step(
                    f"capture-{dimension}-runtime",
                    {"states": list(STATES)},
                ))
                continue
            output_dimension = output / dimension
            output_dimension.mkdir(parents=True, exist_ok=True)
            step = run_step(
                f"capture-{dimension}-runtime", [
                    GODOT_XVFB, "--fixed-fps", str(fixed_fps),
                    "--path", PROJECT_ROOT, "--script", capture_script,
                    "--", "--profile", profile_path,
                    "--output-dir", output_dimension,
                    "--states", ",".join(selected),
                ], PROJECT_ROOT, output / log_name, args.timeout,
            )
            step["captured_states"] = selected
            step["cached_states"] = [
                state for state in STATES if state not in selected
            ]
            steps.append(step)
            if step["exit_code"] != 0:
                raise RuntimeError(f"{dimension} runtime capture failed: {step.get('error') or step['exit_code']}")
            partial_path = output_dimension / "metrics.json"
            if not partial_path.is_file():
                raise FileNotFoundError(f"{dimension} capture did not write metrics.json")
            partial = json.loads(partial_path.read_text(encoding="utf-8"))
            for state in selected:
                expected_count, expected_multiview = expected_state_counts(profile, dimension, state)
                samples = [
                    sample for sample in partial.get("samples", [])
                    if str(sample.get("expected_state", "")).lower() == state
                ]
                if len(samples) != expected_count:
                    raise ValueError(
                        f"{dimension}/{state}: expected {expected_count} captured samples, got {len(samples)}"
                    )
                if dimension == "3d":
                    actual_multiview = sum(bool(sample.get("multiview_captured")) for sample in samples)
                    if actual_multiview != expected_multiview:
                        raise ValueError(
                            f"3D/{state}: expected {expected_multiview} multiview samples, got {actual_multiview}"
                        )
                state_metrics = dict(partial)
                state_metrics["samples"] = samples
                state_metrics["sample_count"] = len(samples)
                state_metrics["captured_states"] = [state]
                if dimension == "3d":
                    state_metrics["multiview_sample_count"] = sum(
                        bool(sample.get("multiview_captured")) for sample in samples
                    )
                state_results[(dimension, state)]["metrics"] = state_metrics

        merged_metrics = {}
        for dimension in ("2d", "3d"):
            if any(state_results[(dimension, state)]["metrics"] is None for state in STATES):
                raise RuntimeError(f"{dimension}: one or more state metrics are unavailable")
            merged_metrics[dimension] = merge_dimension_metrics(
                dimension, state_results, profile, output,
            )

        jobs = build_sheet_jobs(output, profile, states_needing_sheets)
        if jobs:
            jobs_path = output / "04-contact-sheet-jobs.json"
            jobs_path.write_text(json.dumps(jobs, indent=2), encoding="utf-8")
            sheet_step = run_step(
                "build-contact-sheets", [
                    GODOT, "--headless", "--path", PROJECT_ROOT,
                    "--script", CONTACT_SHEET, "--",
                    "--jobs-json", jobs_path,
                ], PROJECT_ROOT, output / "04-contact-sheets.log", args.timeout,
            )
            sheet_step["rebuilt_states"] = [
                f"{dimension}/{state}" for dimension, state in states_needing_sheets
            ]
            steps.append(sheet_step)
            if sheet_step["exit_code"] != 0:
                raise RuntimeError(f"Contact-sheet generation failed: {sheet_step.get('error') or sheet_step['exit_code']}")
            for dimension, state in states_needing_sheets:
                rewrite_contact_sheet_manifests(output, dimension, state)
        else:
            steps.append(synthetic_cached_step(
                "build-contact-sheets", {"states": 12, "reason": "all contact sheets are current"},
            ))

        try:
            write_review_package(output, profile, profile_path)
            steps.append({
                "name": "prepare-review-package", "exit_code": 0,
                "duration_seconds": 0.0, "error": None,
            })
        except Exception as exc:
            steps.append({
                "name": "prepare-review-package", "exit_code": 1,
                "duration_seconds": 0.0, "error": repr(exc),
            })
            raise

        steps.append(run_step(
            "verify-capture-bundle", [
                sys.executable, PROJECT_ROOT / "tools" / "visual_qa" / "verify_bundle.py",
                "--project-root", PROJECT_ROOT, "--profile", profile_path,
                "--output-dir", output,
            ], PROJECT_ROOT, output / "05-verify-bundle.log", args.timeout,
        ))

    except Exception as exc:
        print(f"VISUAL_QA_WORKFLOW_ERROR | {exc}")
        steps.append({
            "name": "incremental-workflow", "exit_code": 1,
            "duration_seconds": 0.0, "error": repr(exc),
        })

    after_status = git_status()
    findings_path = output / "findings.json"
    finding_count = None
    if findings_path.is_file():
        finding_count = json.loads(findings_path.read_text(encoding="utf-8")).get("finding_count")
    all_steps_passed = all(step["exit_code"] == 0 for step in steps)
    if all_steps_passed and before_status == after_status and cache_enabled:
        try:
            for dimension in ("2d", "3d"):
                for state in STATES:
                    result = state_results[(dimension, state)]
                    if result["capture_status"] == "reused" and result["sheet_status"] == "reused":
                        continue
                    keys = result["keys"]
                    if keys is None:
                        continue
                    record = store_state_artifact(
                        dimension, state, keys, merged_metrics[dimension], output,
                    )
                    pending_records[f"{dimension}:{state}"] = record
            commit_state_cache_index(cache_index, pending_records)
            state_cache_report["cache_committed"] = bool(pending_records)
        except Exception as exc:
            all_steps_passed = False
            print(f"STATE_CACHE_COMMIT_FAILED | {exc}")
            steps.append({
                "name": "commit-state-cache", "exit_code": 1,
                "duration_seconds": 0.0, "error": repr(exc),
            })

    report = {
        "schema_version": 2,
        "project_id": profile.get("project_id"),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "output_dir": str(output),
        "profile": str(profile_path),
        "steps": steps,
        "all_steps_passed": all_steps_passed,
        "deterministic_finding_count": finding_count,
        "git_status_unchanged": before_status == after_status,
        "git_status_before": before_status,
        "git_status_after": after_status,
        "state_cache": state_cache_report,
    }
    (output / "run.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    if before_status != after_status:
        print("WARNING | tracked or unignored Git status changed during QA run")
    if not report["all_steps_passed"]:
        print(f"VISUAL_QA_TOOL_ERROR | output={output}")
        return 1
    print(
        "VISUAL_QA_BUNDLE_READY"
        f" | findings={finding_count}"
        f" | captured_states={state_cache_report['captured_state_count']}"
        f" | reused_states={state_cache_report['reused_capture_state_count']}"
        f" | rebuilt_sheets={state_cache_report['rebuilt_sheet_state_count']}"
        f" | output={output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
