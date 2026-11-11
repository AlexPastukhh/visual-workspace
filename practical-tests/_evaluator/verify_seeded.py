#!/usr/bin/env python3
"""EVALUATOR ONLY: validate the original fault-injection controls.

Never run or read this from the test-taking chat.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CASES = ROOT / "visual" / "cases"
KEY = json.loads((ROOT / "_evaluator" / "answer-key.json").read_text())
PAIRS = [
    ("clip-k7", "clip-m4", 12),
    ("clip-r2", "clip-t9", 12),
]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    for reference, modified, expected_index in PAIRS:
        assert KEY["cases"][reference]["expected"] == "no_known_defect", reference
        assert KEY["cases"][modified]["expected"] == "defect", modified
        assert KEY["cases"][modified]["local_frame"] == expected_index, modified
        r = CASES / reference / "frames"
        m = CASES / modified / "frames"
        ref_files = sorted(r.glob("frame_*.png"))
        mod_files = sorted(m.glob("frame_*.png"))
        assert len(ref_files) == len(mod_files)
        changed = [
            i for i, (a, b) in enumerate(zip(ref_files, mod_files))
            if digest(a) != digest(b)
        ]
        assert changed == [expected_index], (reference, modified, changed)
        print(f"EVALUATOR_SEEDED_OK | reference={reference} | modified={modified}")
    print("EVALUATOR_SEEDED_FIXTURES_PASS")


if __name__ == "__main__":
    main()
