#!/usr/bin/env python3
"""Capture regressions for discontinuous intervals and configurable framing."""
import hashlib
import json
import subprocess
import uuid
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT / "projects/asset-workbench"
RUNNER = ROOT / "tools/visual_qa/run_visual_qa.py"

def latest_full(asset, phases):
    for p in sorted((PROJECT / ".fortis-state/visual-qa" / asset).glob("run-*/run.json"), reverse=True):
        d = json.loads(p.read_text())
        if d.get("all_steps_passed") and len(d.get("phases", [])) == phases:
            return p.parent
    raise RuntimeError("Run full QA before this regression: " + asset)

def capture(data, name, workspace):
    data["project_root"] = "../.."
    data["asset_id"] = "readiness-" + name
    manifest = workspace / (name + ".qa.json")
    manifest.write_text(json.dumps(data))
    output = workspace / (name + "-" + uuid.uuid4().hex[:8])
    subprocess.run(["python3", str(RUNNER), "--asset", str(manifest),
                    "--output-dir", str(output), "--force-rebuild"], cwd=ROOT, check=True)
    return output

def main():
    workspace = PROJECT / ".fortis-state/readiness-regressions"
    workspace.mkdir(parents=True, exist_ok=True)
    plane_run = latest_full("planes-dual-pass", 3)
    plane = json.loads((PROJECT / "assets/planes-dual-pass/asset.qa.json").read_text())
    plane["phases"] = [
        {"id": "before_gap", "start": 2.95, "end": 2.96, "focus": "Regression at frame 71"},
        {"id": "after_gap", "start": 4.0, "end": 4.01, "focus": "Regression at frame 96"}]
    gap = capture(plane, "interval-gap", workspace)
    for phase, original in [("before_gap", "outbound"), ("after_gap", "return")]:
        sample = json.loads((gap / phase / "metrics.json").read_text())["samples"][0]
        reference = json.loads((plane_run / original / "metrics.json").read_text())["samples"]
        match = next(s for s in reference if s["sequence_index"] == sample["sequence_index"])
        assert sample["actors"] == match["actors"], (phase, sample, match)
    print("PASS | disconnected intervals match full-run metrics", flush=True)
    rotor_run = latest_full("rotor-beacon-3d", 1)
    rotor = json.loads((PROJECT / "assets/rotor-beacon-3d/asset.qa.json").read_text())
    rotor["phases"][0]["end"] = 1 / 24
    rotor["capture"]["multiview_samples_per_phase"] = 1
    rotor["capture"]["multiview"].update(distance=4, target_offset=[0, 1.6, 0])
    zoom = capture(rotor, "framing", workspace)
    first = json.loads((rotor_run / "clip_00/metrics.json").read_text())["samples"][0]
    a = (rotor_run / "clip_00" / first["multiview_image"]).read_bytes()
    b = (zoom / "clip_00/multiview/frame_0000.png").read_bytes()
    assert hashlib.sha256(a).digest() != hashlib.sha256(b).digest(), "framing ignored"
    print("PASS | framing changes actual four-view image", flush=True)
    print("READINESS_CAPTURE_REGRESSIONS_PASS", flush=True)

if __name__ == "__main__":
    main()
