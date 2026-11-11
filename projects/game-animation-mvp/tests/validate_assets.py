#!/usr/bin/env python3
"""Validate generated 2D source assets and the exported skinned GLB."""
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
import json
import struct
import sys

ROOT = Path(__file__).resolve().parents[1]
A2 = ROOT / "assets" / "2d"
A3 = ROOT / "assets" / "3d"
EXPECTED = {"idle", "walk", "run", "jump"}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def png_size(path):
    data = path.read_bytes()
    require(data[:8] == b"\x89PNG\r\n\x1a\n", f"Invalid PNG signature: {path}")
    return struct.unpack(">II", data[16:24])


def validate_2d():
    manifest = json.loads((A2 / "robot_atlas.json").read_text(encoding="utf-8"))
    require(manifest["canvas"] == [512, 64], "Unexpected 2D atlas dimensions")
    require(manifest["frame_size"] == [64, 64], "Unexpected sprite frame dimensions")
    frames = manifest["frames"]
    require(len(frames) == 8, f"Expected 8 frames, got {len(frames)}")
    for frame in frames:
        name = frame["name"]
        require(png_size(A2 / f"{name}.png") == (64, 64), f"Invalid frame: {name}")
    require(png_size(A2 / "robot_atlas.png") == (512, 64), "Invalid atlas PNG")
    require((A2 / "robot_atlas.png.import").is_file(), "Godot atlas import metadata missing")
    require(set(manifest["animations"]) == EXPECTED, "2D animation names mismatch")
    ora = A2 / "robot_animation_source.ora"
    with ZipFile(ora) as archive:
        names = archive.namelist()
        require(names[0] == "mimetype", "ORA mimetype must be the first archive entry")
        require(archive.read("mimetype") == b"image/openraster", "Invalid ORA mimetype")
        stack = ET.fromstring(archive.read("stack.xml"))
        layers = stack.findall(".//layer")
        require(len(layers) == 8, f"Expected 8 editable ORA layers, got {len(layers)}")
        for layer in layers:
            require(layer.attrib["src"] in names, f"Missing ORA layer image: {layer.attrib['src']}")
    print("ASSET_2D_PASS | 8 frames | 4 animations | editable ORA")


def validate_glb():
    path = A3 / "gamebot_animated.glb"
    require((A3 / "gamebot_animated.glb.import").is_file(), "Godot GLB import metadata missing")
    data = path.read_bytes()
    require(len(data) >= 20, "GLB is too small")
    magic, version, total = struct.unpack_from("<4sII", data, 0)
    require(magic == b"glTF" and version == 2, "Invalid GLB header/version")
    require(total == len(data), "GLB declared length does not match file length")
    offset = 12
    document = None
    while offset < len(data):
        chunk_length, chunk_type = struct.unpack_from("<II", data, offset)
        offset += 8
        chunk = data[offset:offset + chunk_length]
        require(len(chunk) == chunk_length, "Truncated GLB chunk")
        offset += chunk_length
        if chunk_type == 0x4E4F534A:
            document = json.loads(chunk.decode("utf-8").rstrip(" \0"))
    require(document is not None, "GLB JSON chunk missing")
    animations = {item["name"]: item for item in document.get("animations", [])}
    require(set(animations) == {"Idle", "Walk", "Run", "Jump"}, f"3D clips mismatch: {sorted(animations)}")
    for name, animation in animations.items():
        require(len(animation.get("channels", [])) >= 10, f"{name} has too few animation channels")
        require(len(animation.get("samplers", [])) > 0, f"{name} has no samplers")
    skins = document.get("skins", [])
    require(bool(skins) and len(skins[0].get("joints", [])) >= 10, "GLB skin/skeleton missing or incomplete")
    require(bool(document.get("meshes")), "GLB mesh missing")
    require(bool(document["meshes"][0].get("primitives")), "GLB mesh primitives missing")
    print("ASSET_3D_PASS | mesh | skin joints=%d | clips=%s" % (
        len(skins[0]["joints"]), ",".join(sorted(animations))
    ))


def main():
    for path, minimum in [
        (A3 / "source" / "gamebot_rigged.blend", 50000),
        (A3 / "robot_preview.png", 10000),
    ]:
        require(path.is_file() and path.stat().st_size >= minimum, f"Missing or undersized asset: {path}")
    validate_2d()
    validate_glb()
    print("ASSET_VALIDATION_PASS")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ASSET_VALIDATION_FAIL: {exc}", file=sys.stderr)
        raise
