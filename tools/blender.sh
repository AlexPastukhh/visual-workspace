#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BLENDER="$ROOT/.local-tools/blender-5.2.3-linux-x64/blender"
SYSTEM_LIBS="$ROOT/.local-tools/system-libs/usr/lib/x86_64-linux-gnu"
if [[ ! -x "$BLENDER" ]]; then
  echo "Blender is not installed at $BLENDER" >&2
  exit 2
fi
export LD_LIBRARY_PATH="$SYSTEM_LIBS${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export BLENDER_USER_CONFIG="$ROOT/.local-tools/blender-config"
export BLENDER_USER_SCRIPTS="$ROOT/.local-tools/blender-scripts"
mkdir -p "$BLENDER_USER_CONFIG" "$BLENDER_USER_SCRIPTS"
exec "$BLENDER" "$@"
