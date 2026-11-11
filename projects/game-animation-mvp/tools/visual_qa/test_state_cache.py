#!/usr/bin/env python3
"""Unit tests for Visual QA dependency hashing and incremental invalidation."""
from __future__ import annotations

import json
import shutil
import struct
import sys
import tempfile
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORKSPACE = PROJECT.parent.parent
sys.path.insert(0, str(HERE))

import state_cache


def copy_inputs(project_copy: Path, workspace_copy: Path) -> None:
    paths = [
        "project.godot",
        "scenes/demo_2d.tscn",
        "scenes/demo_3d.tscn",
        "scripts/demo_2d.gd",
        "scripts/demo_3d.gd",
        "assets/2d/robot_atlas.png",
        "assets/2d/robot_atlas.png.import",
        "assets/3d/gamebot_animated.glb",
        "assets/3d/gamebot_animated.glb.import",
        "tools/visual_qa/capture_2d.gd",
        "tools/visual_qa/capture_3d_multiview.gd",
        "tools/visual_qa/build_contact_sheet.gd",
        "tools/visual_qa/state_cache.py",
        "tools/visual_qa/run_visual_qa.py",
    ]
    for relative in paths:
        source = PROJECT / relative
        destination = project_copy / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    for relative in ("tools/godot.sh", "tools/godot-xvfb.sh"):
        source = WORKSPACE / relative
        destination = workspace_copy / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def png_chunk(kind: bytes, payload: bytes) -> bytes:
    return (
        struct.pack(">I", len(payload)) + kind + payload
        + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)
    )


def write_rgba8_png(path: Path, width: int, height: int, rows: list[bytes]) -> None:
    raw = b"".join(b"\0" + row for row in rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", zlib.compress(raw))
        + png_chunk(b"IEND", b"")
    )


def mutate_atlas_frame(path: Path, frame_index: int) -> None:
    width, height, rows = state_cache._decode_rgba8_png(path)
    mutable = [bytearray(row) for row in rows]
    x = frame_index * 64
    mutable[0][x * 4] ^= 0x7F
    write_rgba8_png(path, width, height, [bytes(row) for row in mutable])


def mutate_glb_clip(path: Path, clip_name: str) -> None:
    document, _binary = state_cache._read_glb(path)
    animation = next(item for item in document["animations"] if item["name"].lower() == clip_name.lower())
    other_views = set()
    for other in document["animations"]:
        if other is animation:
            continue
        for sampler in other.get("samplers", []):
            for key in ("input", "output"):
                other_views.add(document["accessors"][sampler[key]].get("bufferView"))
    view_index = None
    for sampler in animation.get("samplers", []):
        accessor_index = sampler["output"]
        candidate = document["accessors"][accessor_index].get("bufferView")
        if candidate is not None and candidate not in other_views:
            view_index = candidate
            break
    if view_index is None:
        raise AssertionError(f"No clip-exclusive output view for {clip_name}")
    view_offset = int(document["bufferViews"][view_index].get("byteOffset", 0))

    data = bytearray(path.read_bytes())
    offset = 12
    binary_start = None
    while offset + 8 <= len(data):
        length, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        if chunk_type == 0x004E4942:
            binary_start = offset
            break
        offset += length
    if binary_start is None:
        raise AssertionError("GLB BIN chunk not found")
    data[binary_start + view_offset] ^= 0x01
    path.write_bytes(data)


def main() -> int:
    profile = json.loads((PROJECT / "tools/visual_qa/profile.json").read_text(encoding="utf-8"))
    identity = {
        "version": "unit-test",
        "binary_sha256": "stable-engine",
        "godot_wrapper_sha256": "stable-wrapper",
        "xvfb_wrapper_sha256": "stable-xvfb",
        "renderer_environment": {},
    }
    with tempfile.TemporaryDirectory(prefix="visual-qa-state-cache-test-") as temporary:
        root = Path(temporary)
        project_copy = root / "project"
        workspace_copy = root / "workspace"
        project_copy.mkdir()
        workspace_copy.mkdir()
        copy_inputs(project_copy, workspace_copy)

        original = state_cache.compute_state_keys(project_copy, workspace_copy, profile, identity)

        # One atlas frame is changed: only animations that reference that atlas cell are stale.
        mutate_atlas_frame(project_copy / "assets/2d/robot_atlas.png", 0)
        after_atlas = state_cache.compute_state_keys(project_copy, workspace_copy, profile, identity)
        changed_2d = {
            state for state in state_cache.STATES
            if original[("2d", state)]["capture_key"] != after_atlas[("2d", state)]["capture_key"]
        }
        assert changed_2d == {"idle"}, changed_2d
        assert all(
            original[("3d", state)]["capture_key"] == after_atlas[("3d", state)]["capture_key"]
            for state in state_cache.STATES
        )

        # A single embedded GLB clip changes its own state and the next state's incoming cross-fade.
        mutate_glb_clip(project_copy / "assets/3d/gamebot_animated.glb", "Walk")
        after_clip = state_cache.compute_state_keys(project_copy, workspace_copy, profile, identity)
        changed_3d = {
            state for state in state_cache.STATES
            if after_atlas[("3d", state)]["capture_key"] != after_clip[("3d", state)]["capture_key"]
        }
        assert changed_3d == {"walk", "run"}, changed_3d
        assert all(
            after_atlas[("3d", state)]["common_key"] == after_clip[("3d", state)]["common_key"]
            for state in state_cache.STATES
        )

        # A timeline edit can shift global chronological sequence indices for
        # every state in that dimension; invalidate the dimension as a unit.
        changed_schedule = json.loads(json.dumps(profile))
        changed_schedule["capture"]["2d_segments"]["idle"][1][1] -= 0.2
        after_schedule = state_cache.compute_state_keys(
            project_copy, workspace_copy, changed_schedule, identity,
        )
        assert all(
            after_clip[("2d", state)]["capture_key"] != after_schedule[("2d", state)]["capture_key"]
            for state in state_cache.STATES
        )
        assert all(
            after_clip[("3d", state)]["capture_key"] == after_schedule[("3d", state)]["capture_key"]
            for state in state_cache.STATES
        )

        # Contact-sheet layout changes rebuild sheets only, not runtime captures.
        changed_layout = json.loads(json.dumps(profile))
        changed_layout["capture"]["contact_sheet_columns"] += 1
        after_layout = state_cache.compute_state_keys(
            project_copy, workspace_copy, changed_layout, identity,
        )
        for dimension in ("2d", "3d"):
            for state in state_cache.STATES:
                assert (
                    after_clip[(dimension, state)]["capture_key"]
                    == after_layout[(dimension, state)]["capture_key"]
                )
                assert (
                    after_clip[(dimension, state)]["sheet_key"]
                    != after_layout[(dimension, state)]["sheet_key"]
                )

        # A shared runtime script change invalidates every state in that dimension only.
        script = project_copy / "scripts/demo_2d.gd"
        script.write_text(script.read_text(encoding="utf-8") + "\n# cache invalidation probe\n", encoding="utf-8")
        after_script = state_cache.compute_state_keys(project_copy, workspace_copy, profile, identity)
        assert all(
            after_layout[("2d", state)]["capture_key"] != after_script[("2d", state)]["capture_key"]
            for state in state_cache.STATES
        )
        assert all(
            after_layout[("3d", state)]["capture_key"] == after_script[("3d", state)]["capture_key"]
            for state in state_cache.STATES
        )

    print("STATE_CACHE_TEST_PASS")
    print("PASS | atlas frame invalidates only dependent 2D animation")
    print("PASS | GLB Walk clip invalidates Walk and incoming Run transition only")
    print("PASS | shared model/rig hash stays stable for animation-only edit")
    print("PASS | contact-sheet layout change rebuilds sheets without recapturing")
    print("PASS | timeline change invalidates all states in the affected dimension")
    print("PASS | shared 2D runtime script invalidates 2D only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
