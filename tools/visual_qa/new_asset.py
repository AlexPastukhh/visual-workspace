#!/usr/bin/env python3
"""Prepare one asset in Asset Workbench using the shared neutral preview stages."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path
from validate_asset import MAX_DURATION, PROPERTIES

ROOT = Path(__file__).resolve().parents[2]
PROJECT = ROOT / "projects/asset-workbench"

def resource_dependencies(relative: str, seen: set[str] | None = None) -> set[str]:
    seen = set() if seen is None else seen
    if relative in seen:
        return seen
    path = (PROJECT / relative).resolve()
    path.relative_to(PROJECT.resolve())
    if not path.is_file():
        raise ValueError(f"resource or dependency does not exist: {relative}")
    seen.add(relative)
    if path.suffix in {".tscn", ".tres", ".gd"}:
        for dependency in re.findall('res://([^"\'\\s]+)', path.read_text()):
            if (PROJECT / dependency).is_file():
                resource_dependencies(dependency, seen)
    return seen

def create(asset_id: str, kind: str, resource: str, clips: list[str],
           seconds: float = 2.0, player_path: str = "", extra: list[str] | None = None) -> Path:
    if not re.fullmatch(PROPERTIES["asset_id"]["pattern"], asset_id):
        raise ValueError("asset ID must be lowercase kebab-case")
    if kind not in {"2d", "3d"}:
        raise ValueError("kind must be 2d or 3d")
    if not 0 < seconds <= MAX_DURATION or seconds * max(1, len(clips)) > MAX_DURATION:
        raise ValueError(f"phase duration and total duration must be within {MAX_DURATION} seconds")
    if any(not clip for clip in clips) or len(set(clips)) != len(clips):
        raise ValueError("clip names must be unique and non-empty")
    relative = resource.removeprefix("res://")
    deps = resource_dependencies(relative)
    path = (PROJECT / relative).resolve()
    relative = path.relative_to(PROJECT).as_posix()
    texture = path.suffix.lower() in {".svg", ".png", ".webp", ".jpg"}
    if (texture and kind != "2d") or (not texture and path.suffix not in {".tscn", ".glb"}):
        raise ValueError("use a 2D texture, .tscn scene or self-contained 3D .glb")
    if kind == "2d" and path.suffix.lower() == ".glb":
        raise ValueError("a .glb resource requires --kind 3d")
    if texture and clips:
        raise ValueError("texture clips require an animated content scene")
    stage = f"qa/stage_{kind}.gd"
    deps.update(resource_dependencies(stage))
    for dependency in extra or []:
        deps.update(resource_dependencies(dependency.removeprefix("res://")))
    asset = PROJECT / "assets" / asset_id
    for name in ("preview.tscn", "asset.qa.json", "brief.md"):
        if (asset / name).exists():
            raise FileExistsError(f"refusing to overwrite asset file: {asset / name}")
    local_scene = f"assets/{asset_id}/preview.tscn"
    phases = [
        {"id": f"clip_{i:02d}" if clips else "inspect",
         "start": i * seconds, "end": (i + 1) * seconds,
         **({"expected_clip": clip} if clips else {}),
         "focus": f"Review {clip}: appearance, timing, continuity and loop policy." if clips
                  else "Review silhouette, materials and framing."}
        for i, clip in enumerate(clips or [""])
    ]
    capture = {"fps": 24, "time_control": "qa_set_time",
               "duration_seconds": seconds * len(phases), "resolution": [1280, 720],
               "contact_sheet_max_frames": 24, "contact_sheet_columns": 6,
               "tile_size": [320, 180], "multiview_samples_per_phase": 3 if kind == "3d" else 0}
    if kind == "3d":
        capture["multiview"] = {"actor_id": "subject", "target_offset": [0, 1, 0],
                                "distance": 7, "height": 1.5, "fov": 42}
    manifest = {
        "schema_version": 1, "asset_id": asset_id, "kind": f"{kind}_scene",
        "project_root": "../..", "scene": "res://" + local_scene, "capture": capture,
        "actors": [{"id": "subject", "node_path": "Subject", "dimension": kind,
                    "forward_axis": [1, 0] if kind == "2d" else [0, 0, 1]}],
        "phases": phases, "qa_modules": ["common"] + (["2d-animation"] if kind == "2d" and clips else []),
        "dependencies": sorted(deps | {local_scene, "project.godot"}),
    }
    scene = (
        '[gd_scene load_steps=3 format=3]\n\n'
        f'[ext_resource type="Script" path="res://{stage}" id="1"]\n'
        f'[ext_resource type="{"Texture2D" if texture else "PackedScene"}" path="res://{relative}" id="2"]\n\n'
        f'[node name="AssetPreview" type="{"Node2D" if kind == "2d" else "Node3D"}"]\n'
        'script = ExtResource("1")\n'
        f'{"texture" if texture else "content_scene"} = ExtResource("2")\n'
        'clips = Array[String](' + json.dumps(clips) + ')\n'
        f'animation_player_path = NodePath({json.dumps(player_path)})\n'
        f'seconds_per_phase = {seconds}\n'
    )
    # All validation precedes the only directory creation. Existing assets are untouched.
    asset.mkdir(exist_ok=True)
    (asset / "preview.tscn").write_text(scene)
    (asset / "asset.qa.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (asset / "brief.md").write_text(
        f"# {asset_id}\n\n<!-- brief-status: draft -->\nDescribe the intended result and acceptance criteria before review.\n"
        "\nVerify the visible forward direction; the default axis is only a starting value.\n"
    )
    return asset / "asset.qa.json"

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", required=True)
    parser.add_argument("--kind", required=True, choices=["2d", "3d"])
    parser.add_argument("--resource", required=True, help="Resource path inside Asset Workbench")
    parser.add_argument("--clip", action="append", default=[])
    parser.add_argument("--seconds-per-phase", type=float, default=2.0)
    parser.add_argument("--player-path", default="", help="Path relative to content; inferred only if unique")
    parser.add_argument("--dependency", action="append", default=[], help="Additional dynamic resource input")
    args = parser.parse_args()
    try:
        path = create(args.id, args.kind, args.resource, args.clip,
                      args.seconds_per_phase, args.player_path, args.dependency)
        print(f"ASSET_PREPARED | {path}")
        return 0
    except (ValueError, OSError) as exc:
        print(f"ASSET_PREPARE_FAIL: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    raise SystemExit(main())
