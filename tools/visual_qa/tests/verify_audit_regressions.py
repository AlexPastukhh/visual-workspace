#!/usr/bin/env python3
"""Real capture checks for clip-window drift, interval freedom, caching and brief status."""
import copy
import json
import shutil
import subprocess
import time
import uuid
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
from new_asset import create, PROJECT
ROOT=HERE.parents[1]

def main():
    run_id=uuid.uuid4().hex[:10]
    out=PROJECT/".fortis-state/audit-regressions"/run_id
    out.mkdir(parents=True)
    name="audit-clips-"+run_id
    asset=PROJECT/"assets"/name
    asset.mkdir()
    fixture=(PROJECT/"assets/pulse-beacon-2d/source/beacon.tscn").read_text()
    fixture=fixture.replace('{"Pulse": SubResource("pulse")}','{"Pulse": SubResource("pulse"), "Other": SubResource("pulse")}')
    (asset/"source.tscn").write_text(fixture)
    cases=[]
    def run_case(label,data,success,force=True):
        path=asset/(label+".qa.json");path.write_text(json.dumps(data))
        destination=out/label
        command=["python3",str(HERE/"run_visual_qa.py"),"--asset",str(path),"--output-dir",str(destination)]
        if force: command+=["--force-rebuild"]
        start=time.monotonic()
        result=subprocess.run(command,cwd=ROOT,text=True,capture_output=True,timeout=180)
        (out/(label+".log")).write_text(result.stdout+result.stderr)
        report=json.loads((destination/"run.json").read_text())
        assert (result.returncode==0)==success,(label,result.stdout,result.stderr,report)
        if not success:
            assert "ASSET_CAPTURE_CLIP_MISMATCH" in (destination/"runtime-capture.log").read_text()
        cases.append({"case":label,"expected_success":success,"elapsed":round(time.monotonic()-start,3)})
        print("PASS",label,flush=True)
        return destination,report
    try:
        path=create(name,"2d",f"assets/{name}/source.tscn",["Pulse","Other"],seconds=0.25)
        data=json.loads(path.read_text())
        good, report=run_case("matching-draft",data,True)
        assert report["brief_status"]=="draft" and report["final_acceptance"]=="blocked_by_brief"
        for phase in data["phases"]:
            samples=json.loads((good/phase["id"]/"metrics.json").read_text())["samples"]
            assert all(s["animation_clip"]==phase["expected_clip"] for s in samples)
        drift=copy.deepcopy(data)
        drift["phases"][0]["end"]=0.125
        drift["phases"][1]["start"]=0.125
        run_case("drift-fails",drift,False)
        partial=copy.deepcopy(data)
        partial["phases"]=[
            {"id":"first_slice","start":0,"end":0.083333333333,"expected_clip":"Pulse","focus":"First slice"},
            {"id":"second_slice","start":0.125,"end":0.25,"expected_clip":"Pulse","focus":"Another slice of the same clip"},
            {"id":"other_slice","start":0.375,"end":0.5,"expected_clip":"Other","focus":"Partial second clip"}]
        run_case("partial-windows-pass",partial,True)
        changed=copy.deepcopy(data)
        changed["phases"][0]["expected_clip"]="Other"
        _,bad=run_case("changed-expectation-not-cached",changed,False,force=False)
        assert bad["cache"][0]["capture"]=="captured"
        (asset/"brief.md").write_text("# Test intent\nTwo named clips run in sequence; each QA window must contain its expected clip.\n")
        _,ready=run_case("brief-update-reuses-capture",data,True,force=False)
        assert ready["brief_status"]=="provided" and ready["final_acceptance"]=="pending_visual_review"
        assert not ready["steps"] and all(x["capture"]=="reused" for x in ready["cache"])
        print("AUDIT_CAPTURE_REGRESSIONS_PASS",out,flush=True)
    finally:
        (out/"cases.json").write_text(json.dumps(cases,indent=2))
        shutil.rmtree(asset,ignore_errors=True)

if __name__=="__main__":
    main()
