from __future__ import annotations
import copy
import json
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import validate_asset as contract
from new_asset import create, PROJECT
from run_visual_qa import read_brief, make_review_package, phase_keys

class AuditRegressionTests(unittest.TestCase):
    def setUp(self):
        self.path=PROJECT/"assets/planes-dual-pass/asset.qa.json"
        self.data=json.loads(self.path.read_text())

    def validate_variant(self,data):
        with tempfile.NamedTemporaryFile(mode="w",suffix=".json",dir=self.path.parent,delete=False) as f:
            json.dump(data,f); path=Path(f.name)
        try:
            return contract.validate(path)
        finally:
            path.unlink()

    def test_glb_rejected_as_2d_before_asset_directory_creation(self):
        name="bad-glb-"+uuid.uuid4().hex[:10]
        with self.assertRaisesRegex(ValueError,"requires --kind 3d"):
            create(name,"2d","assets/car-jump-turn-reverse/car.glb",[])
        self.assertFalse((PROJECT/"assets"/name).exists())

    def test_capture_bounds_are_read_from_schema(self):
        with patch.dict(contract.CAPTURE_PROPERTIES["fps"],maximum=12):
            with self.assertRaisesRegex(ValueError,"fps"):
                self.validate_variant(self.data)

    def test_capture_boundary_types_and_ranges(self):
        spec=contract.CAPTURE_PROPERTIES["fps"]
        for value in [spec["minimum"]-1,spec["maximum"]+1,True,24.5]:
            with self.subTest(value=value):
                data=copy.deepcopy(self.data); data["capture"]["fps"]=value
                with self.assertRaises(ValueError):
                    self.validate_variant(data)

    def test_schema_and_runtime_require_common_and_unique_modules(self):
        spec=contract.PROPERTIES["qa_modules"]
        self.assertTrue(spec["uniqueItems"])
        self.assertEqual(spec["contains"],{"const":"common"})
        for modules in [["2d-animation"],["common","common"]]:
            data=copy.deepcopy(self.data);data["qa_modules"]=modules
            with self.assertRaises(ValueError):
                self.validate_variant(data)

    def test_expected_clip_is_validated_and_part_of_capture_key(self):
        original=contract.validate(self.path)
        changed=copy.deepcopy(original)
        changed["phases"][0]["expected_clip"]="Other"
        self.validate_variant(changed)
        before=phase_keys(original,original["phases"][0],PROJECT,{})
        after=phase_keys(changed,changed["phases"][0],PROJECT,{})
        self.assertNotEqual(before[0],after[0])
        for value in ["", " ", False, 7]:
            changed["phases"][0]["expected_clip"]=value
            with self.assertRaisesRegex(ValueError,"expected_clip"):
                self.validate_variant(changed)

    def test_brief_status_does_not_claim_semantic_approval(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest=Path(directory)/"asset.qa.json"
            brief=Path(directory)/"brief.md"
            self.assertEqual(read_brief(manifest)[0],"missing")
            for content, expected in [
                ("# Only a title\n","empty"),
                ("# Draft\nDescribe the intended result and acceptance criteria before review.\n","draft"),
                ("# Work\n<!-- brief-status: draft -->\nSome unfinished text.\n","draft"),
                ("# Asset\nThe amber rotor turns once in two seconds; the tower stays upright.\n","provided")]:
                brief.write_text(content)
                self.assertEqual(read_brief(manifest)[0],expected)

    def test_missing_brief_blocks_acceptance_not_review_packaging(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); out=root/"review"; out.mkdir()
            manifest=copy.deepcopy(self.data)
            phase=manifest["phases"][0]["id"]
            (out/phase).mkdir()
            (out/phase/"metrics.json").write_text('{"samples":[]}')
            result=make_review_package(root/"asset.qa.json",manifest,out,[phase],[])
            self.assertEqual(result["brief"]["status"],"missing")
            self.assertEqual(result["final_acceptance"],"blocked_by_brief")
            self.assertIn("Final artistic acceptance is BLOCKED",(out/"review_prompt.md").read_text())

    def test_generated_clip_manifest_has_expectations_and_draft_brief(self):
        name="clip-guard-test-"+uuid.uuid4().hex[:10]
        directory=PROJECT/"assets"/name
        try:
            path=create(name,"2d","assets/pulse-beacon-2d/source/beacon.tscn",["Pulse"])
            data=contract.validate(path)
            self.assertEqual(data["phases"][0]["expected_clip"],"Pulse")
            self.assertEqual(read_brief(path)[0],"draft")
        finally:
            shutil.rmtree(directory,ignore_errors=True)
