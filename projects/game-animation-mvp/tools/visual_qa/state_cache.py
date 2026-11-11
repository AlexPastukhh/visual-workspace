"""Dependency fingerprints for per-state Visual QA artifact reuse.

All parsing is conservative: unsupported source formats fall back to whole-file hashes,
which may invalidate extra states but can never make stale captures look current.
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import zlib
from pathlib import Path


STATES = ("idle", "walk", "run", "jump")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_hash(value) -> str:
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def _hash_files(project_root: Path, workspace_root: Path, project_paths: list[str], workspace_paths: list[str]) -> dict:
    files = {}
    for relative in project_paths:
        path = project_root / relative
        if not path.is_file():
            return {"missing": relative}
        files[f"project/{relative}"] = sha256_file(path)
    for relative in workspace_paths:
        path = workspace_root / relative
        if not path.is_file():
            return {"missing": relative}
        files[f"workspace/{relative}"] = sha256_file(path)
    return files


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    if pa <= pb and pa <= pc:
        return a
    if pb <= pc:
        return b
    return c


def _decode_rgba8_png(path: Path) -> tuple[int, int, list[bytes]]:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("not PNG")
    offset = 8
    compressed = bytearray()
    width = height = bit_depth = color_type = interlace = None
    while offset + 8 <= len(data):
        length = struct.unpack_from(">I", data, offset)[0]
        kind = data[offset + 4:offset + 8]
        start = offset + 8
        chunk = data[start:start + length]
        offset = start + length + 4
        if kind == b"IHDR":
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", chunk)
            if compression != 0 or filtering != 0:
                raise ValueError("unsupported PNG compression/filter method")
        elif kind == b"IDAT":
            compressed.extend(chunk)
        elif kind == b"IEND":
            break
    if bit_depth != 8 or color_type != 6 or interlace != 0:
        raise ValueError("atlas PNG must be non-interlaced RGBA8")
    row_bytes = width * 4
    raw = zlib.decompress(bytes(compressed))
    if len(raw) != height * (row_bytes + 1):
        raise ValueError("unexpected PNG decompressed size")
    rows: list[bytes] = []
    previous = bytearray(row_bytes)
    cursor = 0
    for _y in range(height):
        filter_type = raw[cursor]
        cursor += 1
        row = bytearray(raw[cursor:cursor + row_bytes])
        cursor += row_bytes
        if filter_type == 1:
            for i in range(row_bytes):
                left = row[i - 4] if i >= 4 else 0
                row[i] = (row[i] + left) & 0xFF
        elif filter_type == 2:
            for i in range(row_bytes):
                row[i] = (row[i] + previous[i]) & 0xFF
        elif filter_type == 3:
            for i in range(row_bytes):
                left = row[i - 4] if i >= 4 else 0
                row[i] = (row[i] + ((left + previous[i]) // 2)) & 0xFF
        elif filter_type == 4:
            for i in range(row_bytes):
                left = row[i - 4] if i >= 4 else 0
                up = previous[i]
                upper_left = previous[i - 4] if i >= 4 else 0
                row[i] = (row[i] + _paeth(left, up, upper_left)) & 0xFF
        elif filter_type != 0:
            raise ValueError(f"unsupported PNG filter {filter_type}")
        rows.append(bytes(row))
        previous = row
    return width, height, rows


def _atlas_frames_by_state(script_path: Path) -> tuple[dict[str, list[int]], int]:
    text = script_path.read_text(encoding="utf-8")
    pattern = re.compile(
        r'_add_animation\(result,\s*"([a-zA-Z0-9_]+)"\s*,\s*\[([^\]]+)\]'
    )
    frames = {}
    for match in pattern.finditer(text):
        state = match.group(1).lower()
        frames[state] = [int(value.strip()) for value in match.group(2).split(",") if value.strip()]
    size_match = re.search(
        r'atlas_frame\.region\s*=\s*Rect2\(float\(index\)\s*\*\s*([0-9.]+)\s*,\s*0\.0\s*,\s*([0-9.]+)\s*,\s*([0-9.]+)\)',
        text,
    )
    if set(frames) != set(STATES) or size_match is None:
        raise ValueError("could not reconstruct the demo's hard-coded atlas regions")
    frame_step, frame_width, frame_height = (int(float(value)) for value in size_match.groups())
    if frame_step != frame_width or frame_width != frame_height:
        raise ValueError("unsupported atlas frame layout")
    return frames, frame_width


def atlas_state_hashes(atlas_path: Path, demo_script: Path) -> dict[str, str]:
    try:
        frames_by_state, frame_size = _atlas_frames_by_state(demo_script)
        width, height, rows = _decode_rgba8_png(atlas_path)
        result = {}
        for state, frame_indices in frames_by_state.items():
            digest = hashlib.sha256()
            for frame_index in frame_indices:
                x0 = frame_index * frame_size
                x1 = x0 + frame_size
                if x0 < 0 or x1 > width or frame_size > height:
                    raise ValueError("atlas frame region is outside the PNG")
                digest.update(struct.pack(">III", frame_index, frame_size, frame_size))
                for y in range(frame_size):
                    digest.update(rows[y][x0 * 4:x1 * 4])
            result[state] = digest.hexdigest()
        return result
    except Exception:
        # Unknown PNG layout or changed GDScript mapping: safe whole-atlas fallback.
        whole = sha256_file(atlas_path)
        return {state: whole for state in STATES}


def _read_glb(path: Path) -> tuple[dict, bytes]:
    data = path.read_bytes()
    if len(data) < 20 or data[:4] != b"glTF":
        raise ValueError("invalid GLB header")
    version, declared_length = struct.unpack_from("<II", data, 4)
    if version != 2 or declared_length != len(data):
        raise ValueError("unsupported GLB version or length")
    offset = 12
    document = None
    binary = None
    while offset + 8 <= len(data):
        length, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset:offset + length]
        if len(chunk) != length:
            raise ValueError("truncated GLB chunk")
        offset += length
        if chunk_type == 0x4E4F534A:
            document = json.loads(chunk.rstrip(b" \t\r\n\0").decode("utf-8"))
        elif chunk_type == 0x004E4942:
            binary = chunk
    if document is None or binary is None:
        raise ValueError("GLB must contain JSON and BIN chunks")
    buffers = document.get("buffers", [])
    if len(buffers) != 1 or "uri" in buffers[0]:
        raise ValueError("external or multiple GLB buffers are not supported")
    return document, binary


def _accessor_view_ids(accessor: dict) -> set[int]:
    result = set()
    if isinstance(accessor.get("bufferView"), int):
        result.add(accessor["bufferView"])
    sparse = accessor.get("sparse", {})
    for member in ("indices", "values"):
        view = sparse.get(member, {}).get("bufferView")
        if isinstance(view, int):
            result.add(view)
    return result


def glb_state_hashes(glb_path: Path) -> tuple[str, dict[str, str]]:
    """Return a shared model/rig hash and per-animation clip hashes."""
    whole_file_hash = sha256_file(glb_path)
    try:
        document, binary = _read_glb(glb_path)
        animations = document.get("animations", [])
        named = {str(item.get("name", "")).lower(): item for item in animations}
        if not all(state in named for state in STATES):
            raise ValueError("GLB does not contain all required named animation clips")

        animation_accessor_ids: set[int] = set()
        per_clip_accessors: dict[str, set[int]] = {}
        for state in STATES:
            ids = set()
            animation = named[state]
            for sampler in animation.get("samplers", []):
                ids.add(int(sampler["input"]))
                ids.add(int(sampler["output"]))
            per_clip_accessors[state] = ids
            animation_accessor_ids.update(ids)

        non_animation_accessor_ids: set[int] = set()
        for mesh in document.get("meshes", []):
            for primitive in mesh.get("primitives", []):
                non_animation_accessor_ids.update(primitive.get("attributes", {}).values())
                if isinstance(primitive.get("indices"), int):
                    non_animation_accessor_ids.add(primitive["indices"])
                for target in primitive.get("targets", []):
                    non_animation_accessor_ids.update(target.values())
        for skin in document.get("skins", []):
            if isinstance(skin.get("inverseBindMatrices"), int):
                non_animation_accessor_ids.add(skin["inverseBindMatrices"])

        non_animation_views: set[int] = set()
        for accessor_index in non_animation_accessor_ids:
            if accessor_index >= len(document.get("accessors", [])):
                raise ValueError("mesh references an invalid accessor")
            non_animation_views.update(_accessor_view_ids(document["accessors"][accessor_index]))
        for image in document.get("images", []):
            if isinstance(image.get("bufferView"), int):
                non_animation_views.add(image["bufferView"])

        animation_views: set[int] = set()
        for accessor_index in animation_accessor_ids:
            if accessor_index >= len(document.get("accessors", [])):
                raise ValueError("animation references an invalid accessor")
            animation_views.update(_accessor_view_ids(document["accessors"][accessor_index]))

        common_document = {
            key: value for key, value in document.items()
            if key not in {"animations", "buffers", "accessors", "bufferViews"}
        }
        common_accessors = []
        for index in sorted(non_animation_accessor_ids):
            accessor = dict(document["accessors"][index])
            common_accessors.append({"index": index, "accessor": accessor})
        common_views = []
        for index in sorted(non_animation_views):
            view = dict(document["bufferViews"][index])
            byte_offset = int(view.get("byteOffset", 0))
            byte_length = int(view["byteLength"])
            view.pop("byteOffset", None)
            common_views.append({
                "index": index, "view": view,
                "data_sha256": sha256_bytes(binary[byte_offset:byte_offset + byte_length]),
            })
        common_hash = canonical_hash({
            "document": common_document,
            "mesh_skin_accessors": common_accessors,
            "mesh_skin_views": common_views,
        })

        clip_hashes = {}
        for state in STATES:
            animation = named[state]
            accessors = []
            views = {}
            for index in sorted(per_clip_accessors[state]):
                accessor = dict(document["accessors"][index])
                accessors.append({"index": index, "accessor": accessor})
                for view_index in _accessor_view_ids(accessor):
                    view = dict(document["bufferViews"][view_index])
                    byte_offset = int(view.get("byteOffset", 0))
                    byte_length = int(view["byteLength"])
                    view.pop("byteOffset", None)
                    views[view_index] = {
                        "view": view,
                        "data_sha256": sha256_bytes(binary[byte_offset:byte_offset + byte_length]),
                    }
            clip_hashes[state] = canonical_hash({
                "animation": animation,
                "accessors": accessors,
                "views": [{"index": index, **views[index]} for index in sorted(views)],
            })
        return common_hash, clip_hashes
    except Exception:
        # Conservative fallback: any GLB change invalidates every 3D state.
        return whole_file_hash, {state: whole_file_hash for state in STATES}


def _profile_state_payload(profile: dict, dimension: str, state: str) -> dict:
    capture = profile["capture"]
    segments_key = f"{dimension}_segments"
    counts_key = f"{dimension}_samples_per_segment"
    payload = {
        "project_id": profile.get("project_id"),
        "scene": profile.get("scenes", {}).get(dimension),
        "duration_seconds": capture.get("duration_seconds"),
        "fixed_fps": capture.get("fixed_fps"),
        "segments": capture.get(segments_key, {}).get(state),
        "samples": capture.get(counts_key, {}).get(state),
        "config": profile.get(dimension, {}),
    }
    # sequence_index is a global chronological index across the complete
    # dimension schedule. A timing change in any state can shift the indices
    # (and contact-sheet metadata) of otherwise unchanged states, so the full
    # schedule is part of every state key within that dimension.
    payload["global_sampling_schedule"] = {
        "segments": capture.get(segments_key, {}),
        "samples": capture.get(counts_key, {}),
    }
    if dimension == "3d":
        payload["multiview_samples_per_state"] = capture.get("3d_multiview_samples_per_state")
    return payload


def compute_state_keys(
    project_root: Path,
    workspace_root: Path,
    profile: dict,
    engine_identity: dict,
) -> dict[tuple[str, str], dict[str, str]]:
    project_root = project_root.resolve()
    workspace_root = workspace_root.resolve()
    atlas_path = project_root / "assets/2d/robot_atlas.png"
    atlas_script = project_root / "scripts/demo_2d.gd"
    atlas_hashes = atlas_state_hashes(atlas_path, atlas_script)
    glb_path = project_root / "assets/3d/gamebot_animated.glb"
    glb_common_hash, glb_clip_hashes = glb_state_hashes(glb_path)

    result = {}
    # Cache implementation and orchestration code define the artifact schema
    # and reuse rules. Changing either invalidates prior state artifacts safely.
    common_project = [
        "project.godot",
        "tools/visual_qa/state_cache.py",
        "tools/visual_qa/run_visual_qa.py",
    ]
    common_workspace = ["tools/godot.sh", "tools/godot-xvfb.sh"]
    for dimension, states in (("2d", STATES), ("3d", STATES)):
        if dimension == "2d":
            demo_script = "scripts/demo_2d.gd"
            capture_script = "tools/visual_qa/capture_2d.gd"
            scene_path = str(profile["scenes"]["2d"]).removeprefix("res://")
            asset_import = "assets/2d/robot_atlas.png.import"
            dimension_paths = [demo_script, capture_script, scene_path, asset_import]
        else:
            demo_script = "scripts/demo_3d.gd"
            capture_script = "tools/visual_qa/capture_3d_multiview.gd"
            scene_path = str(profile["scenes"]["3d"]).removeprefix("res://")
            asset_import = "assets/3d/gamebot_animated.glb.import"
            dimension_paths = [demo_script, capture_script, scene_path, asset_import]

        common_files = _hash_files(
            project_root, workspace_root,
            common_project + dimension_paths, common_workspace,
        )
        if "missing" in common_files:
            raise FileNotFoundError(f"Cannot fingerprint missing dependency: {common_files['missing']}")
        common_hash = canonical_hash({
            "files": common_files,
            "engine": engine_identity,
        })
        for state in states:
            state_payload = _profile_state_payload(profile, dimension, state)
            if dimension == "2d":
                asset_hash = atlas_hashes[state]
                state_payload["atlas_region_sha256"] = asset_hash
            else:
                state_payload["model_rig_sha256"] = glb_common_hash
                state_payload["clip_sha256"] = glb_clip_hashes[state]
                # The 3D state machine cross-fades for 0.16 s; the first sample of
                # each state can still contain the previous state's outgoing pose.
                predecessor = {
                    "idle": "jump", "walk": "idle", "run": "walk", "jump": "run"
                }[state]
                state_payload["incoming_transition_clip_sha256"] = glb_clip_hashes[predecessor]
            capture_key = canonical_hash({
                "dimension": dimension,
                "state": state,
                "common": common_hash,
                "state_payload": state_payload,
                "asset_hash": asset_hash if dimension == "2d" else None,
            })
            sheet_settings = {
                "max_frames": profile["capture"].get("contact_sheet_max_frames", 24),
                "columns": profile["capture"].get("contact_sheet_columns", 6),
                "tile_width": profile["capture"].get("tile_width", 320),
                "tile_height": profile["capture"].get("tile_height", 180),
                "builder_sha256": sha256_file(project_root / "tools/visual_qa/build_contact_sheet.gd"),
            }
            sheet_key = canonical_hash({
                "capture_key": capture_key,
                "sheet_settings": sheet_settings,
            })
            result[(dimension, state)] = {
                "capture_key": capture_key,
                "sheet_key": sheet_key,
                "common_key": common_hash,
                "asset_key": asset_hash if dimension == "2d" else glb_clip_hashes[state],
            }
    return result
