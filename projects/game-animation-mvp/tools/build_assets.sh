#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKSPACE_ROOT="$(cd "$ROOT/../.." && pwd)"
PYTHON_BIN=python3
BLENDER_LAUNCHER="$WORKSPACE_ROOT/tools/blender.sh"
if [[ ! -x "$BLENDER_LAUNCHER" ]]; then
  echo "Shared Blender launcher not found: $BLENDER_LAUNCHER" >&2
  exit 2
fi
"$PYTHON_BIN" "$ROOT/tools/make_2d_assets.py"
"$BLENDER_LAUNCHER" -b --python-exit-code 1 --python "$ROOT/tools/make_3d_robot.py"
rm -f "$ROOT/assets/3d/source/gamebot_rigged.blend1"
mkdir -p "$ROOT/tests/results"
IMPORT_LOG="$ROOT/tests/results/build-godot-import.log"
"$ROOT/tools/godot.sh" --headless --editor --path "$ROOT" --import --quit 2>&1 | tee "$IMPORT_LOG"
if grep -Eq 'ERROR:|SCRIPT ERROR|Parse Error|Blender path is invalid' "$IMPORT_LOG"; then
  echo "Godot asset import reported an error; see tests/results/build-godot-import.log" >&2
  exit 1
fi
"$PYTHON_BIN" "$ROOT/tests/validate_assets.py"
