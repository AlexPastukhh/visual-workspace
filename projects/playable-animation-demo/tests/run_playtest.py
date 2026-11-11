#!/usr/bin/env python3
"""Play the standalone game through native Godot input events and retain visual evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
ROOT = PROJECT.parents[1]
DRIVER = PROJECT / "tests/input_driver.gd"
SCENARIO = PROJECT / "tests/scenario.json"

def run(command, log, timeout=300):
    with log.open("w") as stream:
        result = subprocess.run([str(x) for x in command], cwd=ROOT, stdout=stream,
                                stderr=subprocess.STDOUT, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"exit {result.returncode}: {log}")
    text = log.read_text()
    if "SCRIPT ERROR:" in text or "\nERROR:" in text:
        raise RuntimeError(f"Godot error despite successful process exit: {log}")

def portable_project(output):
    target = output / "portable-project"
    target.mkdir()
    for name in ["project.godot", "game.tscn", "scripts", "assets"]:
        source = PROJECT / name
        if source.is_dir():
            shutil.copytree(source, target / name,
                            ignore=shutil.ignore_patterns("*.import", "*.uid"))
        else:
            shutil.copy2(source, target / name)
    # No capture/test/runtime-state files are copied into the playable project.
    for script in (target / "scripts").glob("*.gd"):
        for forbidden in ["qa_set_time", ".fortis-state", "res://tests/", "/workspace/"]:
            if forbidden in script.read_text():
                raise RuntimeError(f"gameplay dependency leaked into {script}: {forbidden}")
    return target

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quick", action="store_true", help="Sequential input/physics tests without images")
    parser.add_argument("--portable", action="store_true", help="Also test a clean isolated runtime copy")
    args = parser.parse_args()
    output = PROJECT / ".fortis-state/playtests" / datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True)
    started = time.monotonic()
    input_files = [PROJECT / "project.godot", PROJECT / "game.tscn", DRIVER, SCENARIO]
    input_files += list((PROJECT / "scripts").glob("*.gd")) + list((PROJECT / "assets").glob("*"))
    input_files = [p for p in input_files if p.is_file() and p.suffix != ".import"]
    before = {str(p.relative_to(PROJECT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in input_files}
    steps = json.loads(SCENARIO.read_text())
    try:
        run([ROOT/"tools/godot.sh", "--headless", "--path", PROJECT, "--import"], output/"import.log")
        wrapper = ROOT / ("tools/godot.sh" if args.quick else "tools/godot-xvfb.sh")
        command = [wrapper]
        if args.quick: command += ["--headless"]
        command += ["--fixed-fps", "24", "--disable-vsync", "--path", PROJECT,
                    "--script", DRIVER, "--", "--scenario", SCENARIO, "--output", output]
        if args.quick: command += ["--no-images"]
        run(command, output/"playthrough.log")
        result = json.loads((output/"result.json").read_text())
        metrics = json.loads((output/"metrics.json").read_text())
        assert result["passed"], result
        assert result["steps"] == len(steps), result
        assert result["frames"] == sum(s["frames"] for s in steps), result
        assert len(metrics["samples"]) == result["frames"]
        if not args.quick:
            for i, sample in enumerate(metrics["samples"]):
                assert sample["sequence_index"] == i
                assert abs(sample["timestamp_seconds"] - i/24) < 0.00001
                assert (output/sample["image"]).is_file()
            jobs=[{"input_dir":str(output/"frames"),"output":str(output/"contact_sheet.png"),
                   "prefix":"frame_","max_frames":36,"columns":6,"tile_width":320,"tile_height":180,
                   "fps":24,"metrics":str(output/"metrics.json"),"selected_dir":str(output/"selected")}]
            (output/"sheet-jobs.json").write_text(json.dumps(jobs))
            run([ROOT/"tools/godot.sh","--headless","--path",PROJECT,"--script",
                 ROOT/"tools/visual_qa/build_contact_sheet.gd","--","--jobs-json",output/"sheet-jobs.json"],
                output/"contact-sheet.log")
        portability = None
        if args.portable:
            target=portable_project(output)
            run([ROOT/"tools/godot.sh","--headless","--path",target,"--import"],output/"portable-import.log")
            portable_output=output/"portable-evidence"
            run([ROOT/"tools/godot.sh","--headless","--fixed-fps","24","--path",target,
                 "--script",DRIVER,"--","--scenario",SCENARIO,"--output",portable_output,"--no-images"],
                output/"portable-playthrough.log")
            portability=json.loads((portable_output/"result.json").read_text())
            assert portability["passed"]
        after = {str(p.relative_to(PROJECT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in input_files}
        assert before == after, "Inputs changed during playtest"
        report={"passed":True,"frames":result["frames"],"seconds_simulated":result["frames"]/24,
                "steps":result["steps"],"capture":not args.quick,"portable":portability,
                "elapsed_seconds":round(time.monotonic()-started,3),"inputs":before}
        (output/"run.json").write_text(json.dumps(report,indent=2))
        (output/"review_prompt.md").write_text(
            "Review real gameplay frames against brief.md. Check input-driven walk/run/jump, "
            "landing, closed-gate collisions, switch opening, exit and restart in both modes. "
            "Use steps.json for each input and frame range. Inspect full PNGs after the overview. "
            "Separate visual findings from assertions; no artistic verdict follows from PASS.\n")
        print("GAME_PLAYTEST_PASS", json.dumps(report | {"inputs":len(before),"output":str(output)}))
    except Exception as exc:
        (output/"run.json").write_text(json.dumps({"passed":False,"error":str(exc)}))
        print("GAME_PLAYTEST_FAIL",str(exc),"output="+str(output))
        raise

if __name__=="__main__":
    main()
