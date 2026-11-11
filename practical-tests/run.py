#!/usr/bin/env python3
"""Create, inspect and explicitly clean isolated Visual Workspace practical test runs."""
from __future__ import annotations

import argparse
import json
import re
import secrets
import shutil
from datetime import datetime, timezone
from pathlib import Path

SUITE = Path(__file__).resolve().parent
WORKFILES = Path("/workspace/repo/Workfiles/visual-workspace-practical-tests")
RUNS = WORKFILES / "runs"
VISUAL = SUITE / "visual" / "cases"
AUTHORING = SUITE / "authoring"
SENTINEL = ".visual-workspace-practical-run.json"
RUN_ID = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]{5,79}$")


def catalog(directory: Path, extension: str = "") -> list[str]:
    return sorted(path.name if not extension else path.stem
                  for path in directory.iterdir()
                  if path.is_dir() if not extension) if not extension else sorted(
        path.stem for path in directory.glob("*" + extension) if path.is_file()
    )


def get_run(run_id: str) -> Path:
    if not RUN_ID.fullmatch(run_id):
        raise ValueError("run ID must match the safe identifier pattern")
    path = RUNS / run_id
    if path.is_symlink() or path.resolve(strict=False) != RUNS.resolve() / run_id:
        raise ValueError("unsafe run directory")
    return path


def new_run(visual: list[str], orders: list[str]) -> Path:
    if not visual and not orders:
        raise ValueError("select at least one --visual or --order")
    if len(set(visual)) != len(visual) or len(set(orders)) != len(orders):
        raise ValueError("duplicate visual cases or authoring orders are not allowed")
    for case in visual:
        if case not in catalog(VISUAL):
            raise ValueError("unknown visual case: " + case)
    for order in orders:
        if order not in catalog(AUTHORING, ".md"):
            raise ValueError("unknown authoring order: " + order)
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-" + secrets.token_hex(4)
    RUNS.mkdir(parents=True, exist_ok=True)
    run = get_run(run_id)
    run.mkdir(mode=0o700, exist_ok=False)
    (run / "input" / "visual").mkdir(parents=True)
    (run / "input" / "authoring").mkdir(parents=True)
    (run / "output").mkdir()
    for case in visual:
        shutil.copytree(VISUAL / case, run / "input" / "visual" / case)
        (run / "output" / "visual" / case).mkdir(parents=True)
    for order in orders:
        shutil.copyfile(AUTHORING / (order + ".md"), run / "input" / "authoring" / (order + ".md"))
        identifier = order.split("-", 1)[0]
        (run / "output" / identifier).mkdir(parents=True, exist_ok=False)
    info = {
        "schema_version": 1, "run_id": run_id,
        "suite": "visual-workspace/practical-tests",
        "visual_cases": visual, "authoring_orders": orders,
        "repo_suite": str(SUITE), "workfiles_root": str(WORKFILES),
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "not_reviewed"
    }
    (run / SENTINEL).write_text(json.dumps(info, indent=2) + "\n")
    (run / "INSTRUCTIONS.md").write_text(
        "# Practical test run\n\n"
        "Read the prepared input/visual/<case>/brief.md and/or input/authoring/*.md.\n"
        "For visual cases read actual PNG content, not paths, and use chronological frames,\n"
        "sheet and full-resolution samples. Record your report in output/visual/<case>/review.md.\n"
        "For authoring, place *all* newly created sources, projects, frames and reviews in\n"
        "the designated output/Axx/ directory. The repository is a read-only reference.\n"
        "Use the original worktree launchers to run Godot/Blender on the project in Workfiles.\n"
        "Document the requested result, selected UC, commands, timings, technical checks,\n"
        "real image evidence, weaknesses and uncertainty. No hidden expected verdicts are\n"
        "included in this run. Do not open practical-tests/_evaluator or previous reviews.\n"
        "No changes to repository examples, shared tools or other runs.\n"
    )
    return run


def inspect_run(run_id: str) -> dict:
    run = get_run(run_id)
    sentinel = run / SENTINEL
    if not sentinel.is_file() or sentinel.is_symlink():
        raise ValueError("missing or unsafe run sentinel")
    info = json.loads(sentinel.read_text())
    if info.get("run_id") != run_id or info.get("suite") != "visual-workspace/practical-tests":
        raise ValueError("run sentinel does not match")
    return info


def cleanup_run(run_id: str, confirmation: str) -> None:
    if confirmation != run_id:
        raise ValueError("cleanup requires --confirm with the exact run ID")
    info = inspect_run(run_id)
    run = get_run(info["run_id"])
    if run.is_symlink() or not run.is_dir():
        raise ValueError("unsafe cleanup target")
    # Only this named run is deletable. Never glob, prune older runs or touch fixtures.
    shutil.rmtree(run)
    print("WORKFILES_TEST_RUN_CLEANED | " + str(run))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="list available fixture IDs and authoring tasks")
    new = commands.add_parser("new", help="new isolated Workfiles run")
    new.add_argument("--visual", action="append", default=[])
    new.add_argument("--order", action="append", default=[])
    check = commands.add_parser("check", help="inspect run outputs; no acceptance verdict")
    check.add_argument("run_id")
    clean = commands.add_parser("cleanup", help="explicitly delete one named Workfiles run")
    clean.add_argument("run_id")
    clean.add_argument("--confirm", required=True, help="must equal the run_id")
    args = parser.parse_args()
    if args.command == "list":
        print("VISUAL_CASES:", ", ".join(catalog(VISUAL)))
        print("AUTHORING_ORDERS:", ", ".join(catalog(AUTHORING, ".md")))
    elif args.command == "new":
        run = new_run(args.visual, args.order)
        print("WORKFILES_TEST_RUN_CREATED | " + str(run))
        print("START_HERE | " + str(run / "INSTRUCTIONS.md"))
    elif args.command == "check":
        info = inspect_run(args.run_id)
        run = get_run(args.run_id)
        for case in info["visual_cases"]:
            folder = run / "input" / "visual" / case
            metadata = json.loads((folder / "capture.json").read_text())
            actual = len(list((folder / "frames").glob("frame_*.png")))
            report = (run / "output" / "visual" / case / "review.md").is_file()
            print(f"VISUAL | {case} | frames={actual}/{metadata['frame_count']} | review_submitted={report}")
        for order in info["authoring_orders"]:
            identifier = order.split("-", 1)[0]
            files = sum(p.is_file() for p in (run / "output" / identifier).rglob("*"))
            print(f"AUTHORING | {order} | output_files={files} | needs_independent_review=true")
        print("CHECK_COMPLETE | This is an inventory, not an artistic PASS.")
    elif args.command == "cleanup":
        cleanup_run(args.run_id, args.confirm)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, json.JSONDecodeError) as error:
        raise SystemExit("PRACTICAL_TEST_ERROR: " + str(error))
