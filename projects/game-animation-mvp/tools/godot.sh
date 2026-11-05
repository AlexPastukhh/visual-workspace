#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARENT_LAUNCHER="$ROOT/../../tools/godot.sh"
if [[ -x "$PARENT_LAUNCHER" ]]; then
  exec "$PARENT_LAUNCHER" "$@"
fi
if printenv GODOT_BIN >/dev/null 2>&1; then
  GODOT="$(printenv GODOT_BIN)"
elif command -v godot >/dev/null 2>&1; then
  GODOT="$(command -v godot)"
else
  echo "Godot 4.7.2 not found. Install it or set GODOT_BIN=/path/to/godot." >&2
  exit 2
fi
exec "$GODOT" "$@"
