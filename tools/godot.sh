#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SYSROOT="$ROOT/.local-tools/system-libs"
if printenv GODOT_BIN >/dev/null 2>&1; then
  GODOT="$(printenv GODOT_BIN)"
else
  GODOT="$ROOT/.local-tools/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64"
fi
if [[ ! -x "$GODOT" ]]; then echo "Godot is not installed at $GODOT" >&2; exit 2; fi
export LD_LIBRARY_PATH="$SYSROOT/usr/lib/x86_64-linux-gnu:$SYSROOT/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export FONTCONFIG_FILE="$ROOT/.local-tools/fonts.conf"
export FONTCONFIG_PATH="$SYSROOT/etc/fonts"
export LIBGL_DRIVERS_PATH="$SYSROOT/usr/lib/x86_64-linux-gnu/dri"
export MESA_SHADER_CACHE_DIR="$ROOT/.local-tools/mesa-cache"
export XDG_CONFIG_HOME="$ROOT/.local-tools/godot-home/config"
export XDG_CACHE_HOME="$ROOT/.local-tools/godot-home/cache"
export XDG_DATA_HOME="$ROOT/.local-tools/godot-home/data"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME" "$MESA_SHADER_CACHE_DIR" "$ROOT/.local-tools/godot-home/fontconfig-cache"
exec "$GODOT" "$@"
