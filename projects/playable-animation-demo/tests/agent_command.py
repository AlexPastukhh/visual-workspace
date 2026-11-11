#!/usr/bin/env python3
"""Submit one observation/action step to the running input_driver --agent-dir session."""
import argparse
import json
import time
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("session",type=Path)
parser.add_argument("--frames",type=int,default=24)
parser.add_argument("--keys",nargs="*",default=[])
parser.add_argument("--click")
parser.add_argument("--expect",default="{}")
parser.add_argument("--quit",action="store_true")
parser.add_argument("--timeout",type=float,default=60)
args=parser.parse_args()
state_path=args.session/"state.json"
if not state_path.is_file(): raise SystemExit("Session is not ready")
state=json.loads(state_path.read_text())
path=args.session/"command.json"
if path.exists() and json.loads(path.read_text()).get("id",0)>state["id"]:
    raise SystemExit("A previous command is still pending")
command={"id":state["id"]+1,"frames":args.frames,"keys":args.keys,
         "expect":json.loads(args.expect),"label":"agent-controlled step"}
if args.click: command["click"]=args.click
if args.quit: command["quit"]=True
temp=path.with_suffix(".tmp")
temp.write_text(json.dumps(command))
temp.replace(path)
if args.quit:
    print(json.dumps({"quit_submitted":command["id"]}))
else:
    until=time.monotonic()+args.timeout
    while time.monotonic()<until:
        reply=json.loads(state_path.read_text())
        if reply["id"]==command["id"]:
            print(json.dumps({"id":reply["id"],"observation":reply["observation"],"image":reply["result"]["image"],"passed":reply["result"]["passed"],"failures":reply["result"]["failures"]}))
            if not reply["result"]["passed"]: raise SystemExit(1)
            break
        time.sleep(0.1)
    else:
        raise SystemExit("Timed out; inspect driver log before retrying")
