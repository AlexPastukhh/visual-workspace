#!/usr/bin/env python3
"""Validate the versioned, asset-centric Visual Workspace QA contract."""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
# Shared structural constraints have one source. Python adds project/cross-field semantics.
SCHEMA = json.loads(Path(__file__).with_name("asset-contract.schema.json").read_text(encoding="utf-8"))
PROPERTIES = SCHEMA["properties"]
CAPTURE_SCHEMA = PROPERTIES["capture"]
CAPTURE_PROPERTIES = CAPTURE_SCHEMA["properties"]
ACTOR_SCHEMA = PROPERTIES["actors"]["items"]
ACTOR_PROPERTIES = ACTOR_SCHEMA["properties"]
CHARACTER_SCHEMA = ACTOR_PROPERTIES["character"]
CHARACTER_PROPERTIES = CHARACTER_SCHEMA["properties"]
PHASE_SCHEMA = PROPERTIES["phases"]["items"]
FRAMING_SCHEMA = CAPTURE_PROPERTIES["multiview"]
MODULES = set(PROPERTIES["qa_modules"]["items"]["enum"])
TOP_KEYS = set(PROPERTIES)
CAPTURE_KEYS = set(CAPTURE_PROPERTIES)
ACTOR_KEYS = set(ACTOR_PROPERTIES)
CHARACTER_KEYS = set(CHARACTER_PROPERTIES)
PHASE_KEYS = set(PHASE_SCHEMA["properties"])
MAX_DURATION = CAPTURE_PROPERTIES["duration_seconds"]["maximum"]


def fail(message: str) -> None:
    raise ValueError(message)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def is_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)



def schema_number(value: Any, spec: dict) -> bool:
    numeric = is_integer(value) if spec.get("type") == "integer" else is_number(value)
    return numeric and all((
        value >= spec.get("minimum", -math.inf),
        value <= spec.get("maximum", math.inf),
        value > spec.get("exclusiveMinimum", -math.inf),
        value < spec.get("exclusiveMaximum", math.inf),
    ))


def schema_pair(value: Any, spec: dict) -> bool:
    return (isinstance(value, list) and len(value) == len(spec["prefixItems"])
            and all(schema_number(v, item) for v, item in zip(value, spec["prefixItems"])))


def check_keys(value: dict, allowed: set[str], required: set[str], label: str) -> None:
    missing, unknown = required - value.keys(), value.keys() - allowed
    if missing:
        fail(f"{label} missing keys: {sorted(missing)}")
    if unknown:
        fail(f"{label} has unsupported keys: {sorted(unknown)}")


def safe_project_file(project_root: Path, relative: str) -> Path:
    if not isinstance(relative, str) or not relative:
        fail("project paths must be non-empty strings")
    value = Path(relative)
    if value.is_absolute() or ".." in value.parts:
        fail(f"path must stay inside project_root: {relative}")
    candidate = (project_root / value).resolve()
    try:
        candidate.relative_to(project_root.resolve())
    except ValueError:
        fail(f"path escapes project_root: {relative}")
    return candidate


def validate(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("manifest root must be an object")
    check_keys(data, TOP_KEYS, set(SCHEMA["required"]), "manifest")
    if not is_integer(data["schema_version"]) or data["schema_version"] != PROPERTIES["schema_version"]["const"]:
        fail("unsupported schema_version")
    if not isinstance(data["asset_id"], str) or not re.fullmatch(PROPERTIES["asset_id"]["pattern"], data["asset_id"]):
        fail("asset_id must be a lowercase kebab-case identifier")
    if data["kind"] not in PROPERTIES["kind"]["enum"]:
        fail("kind must be 2d_scene or 3d_scene")
    if not isinstance(data["project_root"], str) or not data["project_root"]:
        fail("project_root must be a non-empty relative path")
    project_root = (path.parent / data["project_root"]).resolve()
    if not project_root.is_dir():
        fail(f"project_root does not exist: {project_root}")
    try:
        project_root.relative_to(WORKSPACE_ROOT)
    except ValueError:
        fail("project_root must stay inside the Visual Workspace repository")
    if not (project_root / "project.godot").is_file():
        fail(f"project.godot not found in project_root: {project_root}")

    scene = data["scene"]
    if not isinstance(scene, str) or not scene.startswith("res://"):
        fail("scene must use a res:// path")
    scene_path = safe_project_file(project_root, scene[6:])
    if not scene_path.is_file():
        fail(f"Godot scene does not exist: {scene}")

    capture = data["capture"]
    if not isinstance(capture, dict):
        fail("capture must be an object")
    check_keys(capture, CAPTURE_KEYS, set(CAPTURE_SCHEMA["required"]), "capture")
    fps, duration, resolution = capture["fps"], capture["duration_seconds"], capture["resolution"]
    if not schema_number(fps, CAPTURE_PROPERTIES["fps"]):
        fail("capture fps outside schema bounds")
    if not schema_number(duration, CAPTURE_PROPERTIES["duration_seconds"]):
        fail("capture duration_seconds outside schema bounds")
    if capture["time_control"] != CAPTURE_PROPERTIES["time_control"]["const"]:
        fail("time_control must be qa_set_time for deterministic frame/timestamp alignment")
    if not schema_pair(resolution, CAPTURE_PROPERTIES["resolution"]):
        fail("capture resolution must be [width,height] within schema limits")
    for key in ("multiview_samples_per_phase", "contact_sheet_max_frames", "contact_sheet_columns"):
        if key in capture and not schema_number(capture[key], CAPTURE_PROPERTIES[key]):
            fail(f"capture {key} outside schema bounds")
    if "tile_size" in capture and not schema_pair(capture["tile_size"], CAPTURE_PROPERTIES["tile_size"]):
        fail("capture tile_size must be [width,height] within schema limits")

    actors = data["actors"]
    if not isinstance(actors, list) or not actors:
        fail("at least one actor is required")
    actor_ids = set()
    expected_dimension = "2d" if data["kind"] == "2d_scene" else "3d"
    for actor in actors:
        if not isinstance(actor, dict):
            fail("each actor must be an object")
        check_keys(actor, ACTOR_KEYS, set(ACTOR_SCHEMA["required"]), "actor")
        actor_id = actor["id"]
        if not isinstance(actor_id, str) or not re.fullmatch(ACTOR_PROPERTIES["id"]["pattern"], actor_id):
            fail(f"invalid actor id: {actor_id}")
        if actor_id in actor_ids:
            fail(f"duplicate actor id: {actor_id}")
        actor_ids.add(actor_id)
        if not isinstance(actor["node_path"], str) or not actor["node_path"]:
            fail(f"actor {actor_id} requires a non-empty node_path")
        if actor["dimension"] != expected_dimension:
            fail(f"actor {actor_id} dimension does not match asset kind")
        axis = actor["forward_axis"]
        axis_length = 2 if expected_dimension == "2d" else 3
        if (not isinstance(axis, list) or len(axis) != axis_length
                or not all(is_number(v) for v in axis)
                or sum(float(v) ** 2 for v in axis) <= 1e-8):
            fail(f"actor {actor_id} forward_axis must be a non-zero {axis_length}D vector")
        if "ground_y" in actor and not is_number(actor["ground_y"]):
            fail(f"actor {actor_id} ground_y must be numeric")
        if "ground_tolerance" in actor and (
                not schema_number(actor["ground_tolerance"], ACTOR_PROPERTIES["ground_tolerance"])):
            fail(f"actor {actor_id} ground_tolerance must be non-negative")
        tracked = actor.get("tracked_children", [])
        if (not isinstance(tracked, list) or not all(isinstance(item, str) and item for item in tracked)
                or len(tracked) != len(set(tracked))):
            fail(f"actor {actor_id} tracked_children must contain unique non-empty names")

        character = actor.get("character")
        if character is not None:
            if data["kind"] != "3d_scene" or actor["dimension"] != "3d":
                fail(f"actor {actor_id} character capture requires a 3d_scene actor")
            if not isinstance(character, dict):
                fail(f"actor {actor_id} character must be an object")
            check_keys(
                character, CHARACTER_KEYS,
                set(CHARACTER_SCHEMA["required"]),
                f"actor {actor_id} character",
            )
            for key in ("skeleton_path", "animation_player_path", "animation_tree_path"):
                if key in character:
                    value = character[key]
                    if (not isinstance(value, str) or not value
                            or value.startswith("/") or ".." in Path(value).parts):
                        fail(f"actor {actor_id} character {key} must be a relative NodePath inside the actor")
            if not character.get("animation_player_path") and not character.get("animation_tree_path"):
                fail(f"actor {actor_id} character requires animation_player_path or animation_tree_path")
            if "playback_property" in character:
                if not isinstance(character["playback_property"], str) or not character["playback_property"]:
                    fail(f"actor {actor_id} character playback_property must be a non-empty property path")
                if not character.get("animation_tree_path"):
                    fail(f"actor {actor_id} character playback_property requires animation_tree_path")
            bones = character["foot_bones"]
            if (not isinstance(bones, dict) or set(bones) != {"left", "right"}
                    or not all(isinstance(value, str) and value for value in bones.values())
                    or bones["left"] == bones["right"]):
                fail(f"actor {actor_id} character foot_bones must map distinct left and right bone names")
            if (not isinstance(character["motion_mode"], str)
                    or character["motion_mode"] not in CHARACTER_PROPERTIES["motion_mode"]["enum"]):
                fail(f"actor {actor_id} character motion_mode is unsupported")
            loop_states = character.get("loop_states", [])
            if (not isinstance(loop_states, list)
                    or not all(isinstance(value, str) and value for value in loop_states)
                    or len(loop_states) != len(set(loop_states))):
                fail(f"actor {actor_id} character loop_states must contain unique non-empty state names")
            if "jump_state" in character and (
                    not isinstance(character["jump_state"], str) or not character["jump_state"]):
                fail(f"actor {actor_id} character jump_state must be a non-empty state name")
            if "landing_policy" in character and (
                    not isinstance(character["landing_policy"], str)
                    or character["landing_policy"] not in CHARACTER_PROPERTIES["landing_policy"]["enum"]):
                fail(f"actor {actor_id} character landing_policy is unsupported")

    framing = capture.get("multiview", {})
    if not isinstance(framing, dict):
        fail("capture multiview must be an object")
    check_keys(framing, set(FRAMING_SCHEMA["properties"]), set(), "multiview")
    if framing and data["kind"] != "3d_scene":
        fail("multiview framing requires 3d_scene")
    if "actor_id" in framing and framing["actor_id"] not in actor_ids:
        fail("multiview actor_id must identify a configured actor")
    for key in ("distance", "height", "fov"):
        if key in framing and not schema_number(framing[key], FRAMING_SCHEMA["properties"][key]):
            fail(f"multiview {key} outside schema bounds")
    offset = framing.get("target_offset", [0, 0, 0])
    if not isinstance(offset, list) or len(offset) != 3 or not all(is_number(v) for v in offset):
        fail("multiview target_offset must be a finite 3D vector")

    phases = data["phases"]
    if not isinstance(phases, list) or not phases:
        fail("at least one phase is required")
    phase_ids, previous_end = set(), -1.0
    phase_dependencies = []
    for phase in phases:
        if not isinstance(phase, dict):
            fail("each phase must be an object")
        check_keys(phase, PHASE_KEYS, set(PHASE_SCHEMA["required"]), "phase")
        phase_id = phase["id"]
        if not isinstance(phase_id, str) or not re.fullmatch(PHASE_SCHEMA["properties"]["id"]["pattern"], phase_id):
            fail(f"invalid phase id: {phase_id}")
        if phase_id in phase_ids:
            fail(f"duplicate phase id: {phase_id}")
        phase_ids.add(phase_id)
        start, end = phase["start"], phase["end"]
        if not is_number(start) or not is_number(end):
            fail(f"phase {phase_id} start/end must be numeric")
        if start < previous_end - 1e-7 or start < 0 or end <= start or end > float(duration) + 1e-7:
            fail(f"invalid or overlapping phase interval: {phase_id} [{start},{end}]")
        previous_end = float(end)
        if not isinstance(phase["focus"], str) or not phase["focus"].strip():
            fail(f"phase {phase_id} requires a review focus")
        if "expected_clip" in phase and (not isinstance(phase["expected_clip"], str) or not phase["expected_clip"].strip()):
            fail(f"phase {phase_id} expected_clip must be a non-empty clip name")
        deps = phase.get("dependencies", [])
        if not isinstance(deps, list) or not all(isinstance(item, str) and item for item in deps):
            fail(f"phase {phase_id} dependencies must be an array of paths")
        phase_dependencies.extend(deps)

    modules = data["qa_modules"]
    if (not isinstance(modules, list) or not modules or len(modules) != len(set(modules))
            or set(modules) - MODULES):
        fail(f"unknown, duplicate or empty qa_modules: {modules}")
    if PROPERTIES["qa_modules"]["contains"]["const"] not in modules:
        fail("common QA module is mandatory")
    has_character_capture = any(isinstance(actor, dict) and "character" in actor for actor in actors)
    if ("3d-character" in modules) != has_character_capture:
        fail("3d-character QA module and actor character capture configuration must be selected together")

    dependencies = data["dependencies"]
    if not isinstance(dependencies, list) or not dependencies or not all(
            isinstance(item, str) and item for item in dependencies):
        fail("dependencies must list the scene/controller/source inputs")
    for relative in set(dependencies + phase_dependencies + [scene[6:]]):
        dependency = safe_project_file(project_root, relative)
        if not dependency.is_file():
            fail(f"missing dependency: {relative}")
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    try:
        data = validate(args.manifest.resolve())
    except Exception as exc:
        print(f"ASSET_CONTRACT_FAIL: {exc}", file=sys.stderr)
        return 2
    print(f"ASSET_CONTRACT_PASS | {data['asset_id']} | {data['kind']} | phases={len(data['phases'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
