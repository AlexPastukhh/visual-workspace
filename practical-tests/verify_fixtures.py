#!/usr/bin/env python3
"""Read-only integrity check for permanent practical PNG fixtures.

Discovers new cases automatically without revealing evaluator-only labels.
Allows additional visual fixtures and written authoring briefs.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = ROOT / "visual" / "cases"
ORIGINAL_COUNTS = {
    "clip-k7": 24, "clip-m4": 24, "clip-r2": 48,
    "clip-t9": 48, "clip-w8": 24,
}


def main() -> None:
    observed: dict[str, int] = {}
    for case in sorted(p for p in CASES.iterdir() if p.is_dir()):
        data = json.loads((case / "capture.json").read_text())
        assert data["schema_version"] == 1
        assert data["source_type"] == "numbered_png_sequence", case
        count = data["frame_count"]
        assert isinstance(count, int) and count > 0, case
        assert isinstance(data["fps"], (int, float)) and data["fps"] > 0, case
        assert data["frame_pattern"] == "frames/frame_%04d.png", case
        files = sorted((case / "frames").glob("frame_*.png"))
        assert len(files) == count, (case.name, len(files), count)
        assert (case / "brief.md").is_file(), case
        assert (case / "contact_sheet.png").is_file(), case
        for i, file in enumerate(files):
            assert file.name == f"frame_{i:04d}.png", file
            with file.open("rb") as handle:
                assert handle.read(8) == b"\x89PNG\r\n\x1a\n", file
        observed[case.name] = count
        print(f"FIXTURE_OK {case.name} {count} frames")

    for name, count in ORIGINAL_COUNTS.items():
        assert observed.get(name) == count, (name, observed.get(name), count)
    written = sorted((ROOT / "authoring").glob("A*.md"))
    assert len(written) >= 6
    for brief in written:
        assert "## Brief" in brief.read_text(), brief
    print(f"PRACTICAL_FIXTURES_PASS | visual={len(observed)} | authoring={len(written)}")


if __name__ == "__main__":
    main()
