from __future__ import annotations

import copy
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path

TOOLS_DIR = Path(__file__).resolve().parents[1]
REPO_ROOT = TOOLS_DIR.parents[1]
sys.path.insert(0, str(TOOLS_DIR))

from run_visual_qa import expected_samples, files_match, load_cache, sha256_file
from validate_asset import validate


class AssetContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest_path = (
            REPO_ROOT / "projects/asset-workbench/assets/planes-dual-pass/asset.qa.json"
        )
        self.data = json.loads(self.manifest_path.read_text(encoding="utf-8"))

    def validate_variant(self, data: dict) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", suffix=".json",
            dir=self.manifest_path.parent, delete=False,
        ) as handle:
            json.dump(data, handle)
            temp_path = Path(handle.name)
        try:
            validate(temp_path)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_both_pilot_manifests_are_valid(self) -> None:
        validate(self.manifest_path)
        validate(REPO_ROOT / "projects/asset-workbench/assets/car-jump-turn-reverse/asset.qa.json")

    def test_rejects_non_deterministic_clock(self) -> None:
        data = copy.deepcopy(self.data)
        data["capture"]["time_control"] = "wall_clock"
        with self.assertRaisesRegex(ValueError, "time_control"):
            self.validate_variant(data)

    def test_rejects_overlapping_phases(self) -> None:
        data = copy.deepcopy(self.data)
        data["phases"][1]["start"] = 2.5
        with self.assertRaisesRegex(ValueError, "overlapping"):
            self.validate_variant(data)

    def test_rejects_zero_forward_axis(self) -> None:
        data = copy.deepcopy(self.data)
        data["actors"][0]["forward_axis"] = [0.0, 0.0]
        with self.assertRaisesRegex(ValueError, "non-zero"):
            self.validate_variant(data)

    def character_manifest(self) -> dict:
        data = json.loads(
            (REPO_ROOT / "projects/asset-workbench/assets/car-jump-turn-reverse/asset.qa.json")
            .read_text(encoding="utf-8")
        )
        data["qa_modules"] = ["common", "3d-character"]
        data["actors"][0]["character"] = {
            "skeleton_path": "Model/Skeleton3D",
            "animation_player_path": "Model/AnimationPlayer",
            "foot_bones": {"left": "Foot.L", "right": "Foot.R"},
            "motion_mode": "forward",
            "loop_states": ["Idle", "Walk", "Run"],
            "jump_state": "Jump",
            "landing_policy": "hold_final_pose_until_phase_end",
        }
        return data

    def test_accepts_contract_driven_character_capture(self) -> None:
        self.validate_variant(self.character_manifest())

    def test_rejects_character_without_matching_qa_module(self) -> None:
        data = self.character_manifest()
        data["qa_modules"] = ["common", "3d-vehicle"]
        with self.assertRaisesRegex(ValueError, "selected together"):
            self.validate_variant(data)

    def test_rejects_invalid_character_foot_bones(self) -> None:
        data = self.character_manifest()
        data["actors"][0]["character"]["foot_bones"]["right"] = "Foot.L"
        with self.assertRaisesRegex(ValueError, "distinct left and right"):
            self.validate_variant(data)

    def test_accepts_animation_tree_only_character_capture(self) -> None:
        data = self.character_manifest()
        character = data["actors"][0]["character"]
        character.pop("animation_player_path")
        character["animation_tree_path"] = "AnimationTree"
        character["playback_property"] = "parameters/playback"
        self.validate_variant(data)

    def test_rejects_playback_property_without_animation_tree(self) -> None:
        data = self.character_manifest()
        data["actors"][0]["character"]["playback_property"] = "parameters/playback"
        with self.assertRaisesRegex(ValueError, "requires animation_tree_path"):
            self.validate_variant(data)

    def test_rejects_empty_playback_property(self) -> None:
        data = self.character_manifest()
        data["actors"][0]["character"]["animation_tree_path"] = "AnimationTree"
        data["actors"][0]["character"]["playback_property"] = ""
        with self.assertRaisesRegex(ValueError, "non-empty property path"):
            self.validate_variant(data)

    def test_rejects_character_node_path_escape(self) -> None:
        data = self.character_manifest()
        data["actors"][0]["character"]["skeleton_path"] = "../Skeleton3D"
        with self.assertRaisesRegex(ValueError, "relative NodePath"):
            self.validate_variant(data)

    def test_rejects_animation_tree_node_path_escape(self) -> None:
        data = self.character_manifest()
        data["actors"][0]["character"]["animation_tree_path"] = "../AnimationTree"
        with self.assertRaisesRegex(ValueError, "relative NodePath"):
            self.validate_variant(data)

    def test_rejects_dependency_path_escape(self) -> None:
        data = copy.deepcopy(self.data)
        data["dependencies"].append("../README.md")
        with self.assertRaisesRegex(ValueError, "stay inside"):
            self.validate_variant(data)


class RunnerHelperTests(unittest.TestCase):
    def test_expected_samples_respects_half_open_phase_interval(self) -> None:
        capture = {"fps": 24, "duration_seconds": 7.0}
        self.assertEqual(expected_samples({"start": 3.0, "end": 4.0}, capture), 24)
        self.assertEqual(expected_samples({"start": 0.0, "end": 3.0}, capture), 72)
        self.assertEqual(expected_samples({"start": 2.8, "end": 4.0}, capture), 28)

    def test_cache_file_integrity_detects_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "frame.bin"
            artifact.write_bytes(b"first")
            expected_hash = sha256_file(artifact)
            self.assertTrue(files_match(root, {"frame.bin": expected_hash}))
            artifact.write_bytes(b"changed")
            self.assertFalse(files_match(root, {"frame.bin": expected_hash}))

    def test_cache_reuse_checks_expected_multiview_coverage(self) -> None:
        def png_header(width: int, height: int) -> bytes:
            return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", width, height)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "frames").mkdir()
            (root / "multiview").mkdir()
            (root / "frames/frame_0000.png").write_bytes(png_header(320, 240))
            (root / "multiview/frame_0000.png").write_bytes(png_header(1280, 720))
            (root / "contact_sheet.png").write_bytes(png_header(320, 240))
            metrics = {
                "sample_count": 1,
                "samples": [{
                    "image": "frames/frame_0000.png",
                    "multiview_image": "multiview/frame_0000.png",
                }],
            }
            (root / "metrics.json").write_text(json.dumps(metrics), encoding="utf-8")
            capture_files = {
                relative: sha256_file(root / relative)
                for relative in ("metrics.json", "frames/frame_0000.png", "multiview/frame_0000.png")
            }
            sheet_files = {"contact_sheet.png": sha256_file(root / "contact_sheet.png")}
            record = {
                "schema_version": 1, "capture_key": "capture", "sheet_key": "sheet",
                "resolution": [320, 240], "capture_files": capture_files, "sheet_files": sheet_files,
            }
            (root / "cache-manifest.json").write_text(json.dumps(record), encoding="utf-8")
            loaded, sheets_valid = load_cache(root, "capture", "sheet", 1, "3d_scene", 1)
            self.assertIsNotNone(loaded)
            self.assertTrue(sheets_valid)
            rejected, _ = load_cache(root, "capture", "sheet", 1, "3d_scene", 3)
            self.assertIsNone(rejected)


if __name__ == "__main__":
    unittest.main()
