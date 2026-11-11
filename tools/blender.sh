#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOLS="$ROOT/.local-tools"
STATE="$ROOT/.fortis-state/blender"
if printenv BLENDER_BIN >/dev/null 2>&1; then
  BLENDER="$(printenv BLENDER_BIN)"
elif [[ -x "$TOOLS/blender-5.2.3-linux-x64/blender" ]]; then
  BLENDER="$TOOLS/blender-5.2.3-linux-x64/blender"
else
  BLENDER="$(command -v blender || true)"
fi
SYSTEM_LIBS="$TOOLS/system-libs/usr/lib/x86_64-linux-gnu"
if [[ ! -x "$BLENDER" ]]; then
  echo "Blender is not installed at $BLENDER" >&2
  exit 2
fi

# The binary and libraries are shared; mutable user state belongs to this Worktree.
export LD_LIBRARY_PATH="$SYSTEM_LIBS${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export BLENDER_USER_CONFIG="$STATE/config"
export BLENDER_USER_SCRIPTS="$STATE/scripts"
export BLENDER_USER_DATAFILES="$STATE/datafiles"
export BLENDER_USER_EXTENSIONS="$STATE/extensions"
export HOME="$STATE/home"
export XDG_CONFIG_HOME="$STATE/xdg/config"
export XDG_CACHE_HOME="$STATE/xdg/cache"
export XDG_DATA_HOME="$STATE/xdg/data"
export XDG_STATE_HOME="$STATE/xdg/state"
export XDG_RUNTIME_DIR="$STATE/xdg/runtime"
export TMPDIR="$STATE/tmp"
mkdir -p "$BLENDER_USER_CONFIG" "$BLENDER_USER_SCRIPTS" \
  "$BLENDER_USER_DATAFILES" "$BLENDER_USER_EXTENSIONS" "$HOME" \
  "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME" \
  "$XDG_STATE_HOME" "$XDG_RUNTIME_DIR" "$TMPDIR"
chmod 700 "$XDG_RUNTIME_DIR"
exec "$BLENDER" "$@"
