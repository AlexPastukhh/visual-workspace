#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PYTHON_BIN=python3
if printenv BLENDER_BIN >/dev/null 2>&1; then
  BLENDER_BIN="$(printenv BLENDER_BIN)"
else
  BLENDER_BIN="$ROOT/../../.local-tools/blender-5.2.3-linux-x64/blender"
  if [[ -x "$BLENDER_BIN" ]]; then
    SYSROOT="$ROOT/../../.local-tools/system-libs"
    BLENDER_LIB="$ROOT/../../.local-tools/blender-5.2.3-linux-x64/lib"
    if [[ -d "$SYSROOT/usr/lib/x86_64-linux-gnu" ]]; then
      export LD_LIBRARY_PATH="$SYSROOT/usr/lib/x86_64-linux-gnu:$SYSROOT/lib/x86_64-linux-gnu:$BLENDER_LIB"
    fi
  else
    BLENDER_BIN="$(command -v blender || true)"
  fi
fi
if [[ -z "$BLENDER_BIN" || ! -x "$BLENDER_BIN" ]]; then
  echo "Blender 5.2.x not found. Set BLENDER_BIN=/path/to/blender or install Blender." >&2
  exit 2
fi
"$PYTHON_BIN" "$ROOT/tools/make_2d_assets.py"
"$BLENDER_BIN" -b --python-exit-code 1 --python "$ROOT/tools/make_3d_robot.py"
rm -f "$ROOT/assets/3d/source/gamebot_rigged.blend1"
mkdir -p "$ROOT/tests/results"
IMPORT_LOG="$ROOT/tests/results/build-godot-import.log"
"$ROOT/tools/godot.sh" --headless --editor --path "$ROOT" --import --quit 2>&1 | tee "$IMPORT_LOG"
if grep -Eq 'ERROR:|SCRIPT ERROR|Parse Error|Blender path is invalid' "$IMPORT_LOG"; then
  echo "Godot asset import reported an error; see tests/results/build-godot-import.log" >&2
  exit 1
fi
"$PYTHON_BIN" "$ROOT/tests/validate_assets.py"
