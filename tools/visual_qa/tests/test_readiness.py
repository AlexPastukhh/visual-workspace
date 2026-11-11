from __future__ import annotations
import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
import run_visual_qa as runner
from new_asset import create, PROJECT
from validate_asset import validate

MANIFEST = PROJECT / "assets/planes-dual-pass/asset.qa.json"

class ReadinessTests(unittest.TestCase):
    def test_existing_output_report_survives_rejected_run(self):
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "run.json"
            report.write_bytes(b'{"previous_result": true}\n')
            previous = report.read_bytes()
            with patch.object(sys, "argv", ["qa", "--asset", str(MANIFEST), "--output-dir", directory]), \
                 patch.object(runner, "engine_identity", return_value={}), \
                 contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(runner.main(), 1)
            self.assertEqual(report.read_bytes(), previous)

    def test_framing_changes_invalidate_capture_not_only_sheets(self):
        path = PROJECT / "assets/car-jump-turn-reverse/asset.qa.json"
        data = validate(path)
        changed = copy.deepcopy(data)
        changed["capture"]["multiview"] = {"actor_id": "car", "distance": 12}
        before = runner.phase_keys(data, data["phases"][0], PROJECT, {})
        after = runner.phase_keys(changed, changed["phases"][0], PROJECT, {})
        self.assertNotEqual(before[0], after[0])
        self.assertEqual(before[1], after[1])

    def test_preparer_reuses_stage_and_preserves_existing_asset(self):
        name = "readiness-test-" + uuid.uuid4().hex[:10]
        directory = PROJECT / "assets" / name
        try:
            path = create(name, "2d", "assets/pulse-beacon-2d/source/beacon.tscn", ["Pulse"])
            data = validate(path)
            self.assertIn("qa/clip_sampler.gd", data["dependencies"])
            self.assertIn("qa/stage_2d.gd", data["dependencies"])
            before = path.read_bytes()
            with self.assertRaises(FileExistsError):
                create(name, "2d", "assets/pulse-beacon-2d/source/beacon.tscn", ["Pulse"])
            self.assertEqual(path.read_bytes(), before)
        finally:
            shutil.rmtree(directory, ignore_errors=True)

    def test_preparer_rejects_external_resource(self):
        with self.assertRaises(ValueError):
            create("bad-resource-test", "2d", "../project.godot", [])

    def test_preparer_rejects_clips_for_unanimated_texture(self):
        with self.assertRaises(ValueError):
            create("bad-texture-test", "2d", "assets/planes-dual-pass/source/upper-plane.svg", ["Fly"])

    def test_new_manifests_validate(self):
        for name in ("pulse-beacon-2d", "rotor-beacon-3d"):
            validate(PROJECT / "assets" / name / "asset.qa.json")
