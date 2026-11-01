#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="$ROOT"
RESULTS="$ROOT/tests/results"
mkdir -p "$RESULTS"
GODOT="$ROOT/tools/godot.sh"
if [[ ! -x "$GODOT" ]]; then
  echo "Godot launcher not found: $GODOT" >&2
  exit 2
fi
"$GODOT" --headless --editor --path "$PROJECT" --import --quit 2>&1 | tee "$RESULTS/godot-import.log"
if grep -Eq 'ERROR:|SCRIPT ERROR|Parse Error|Blender path is invalid' "$RESULTS/godot-import.log"; then
  echo "Godot asset import reported an error; see tests/results/godot-import.log" >&2
  exit 1
fi
python3 "$ROOT/tests/validate_assets.py" 2>&1 | tee "$RESULTS/assets-validation.log"
"$GODOT" --headless --path "$PROJECT" -- --demo-2d --test 2>&1 | tee "$RESULTS/godot-2d.log"
"$GODOT" --headless --path "$PROJECT" -- --demo-3d --test 2>&1 | tee "$RESULTS/godot-3d.log"
echo "ALL_TESTS_PASS"
