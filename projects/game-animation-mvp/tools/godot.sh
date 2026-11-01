#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if printenv GODOT_BIN >/dev/null 2>&1; then
  GODOT="$(printenv GODOT_BIN)"
  exec "$GODOT" "$@"
fi
if command -v godot >/dev/null 2>&1; then
  exec "$(command -v godot)" "$@"
fi
PARENT_LAUNCHER="$ROOT/../../tools/godot.sh"
if [[ -x "$PARENT_LAUNCHER" ]]; then
  exec "$PARENT_LAUNCHER" "$@"
fi
echo "Godot 4.7.2 not found. Install it or set GODOT_BIN=/path/to/godot." >&2
exit 2
