#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS="$ROOT/.local-tools"
STATE="$ROOT/.fortis-state/godot"
SYSROOT="$TOOLS/system-libs"
if printenv GODOT_BIN >/dev/null 2>&1; then
  GODOT="$(printenv GODOT_BIN)"
elif [[ -x "$TOOLS/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64" ]]; then
  GODOT="$TOOLS/godot-4.7.2/Godot_v4.7.2-stable_linux.x86_64"
else
  GODOT="$(command -v godot || true)"
fi
if [[ ! -x "$GODOT" ]]; then echo "Godot is not installed at $GODOT" >&2; exit 2; fi

# Share the engine/runtime, but isolate settings, shader/font caches and temp files per Worktree.
export LD_LIBRARY_PATH="$SYSROOT/usr/lib/x86_64-linux-gnu:$SYSROOT/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export FONTCONFIG_FILE="$STATE/fonts.conf"
export XKB_CONFIG_ROOT="$SYSROOT/usr/share/X11/xkb"
export FONTCONFIG_PATH="$SYSROOT/etc/fonts"
export LIBGL_DRIVERS_PATH="$SYSROOT/usr/lib/x86_64-linux-gnu/dri"
export MESA_SHADER_CACHE_DIR="$STATE/mesa-cache"
export HOME="$STATE/home"
export XDG_CONFIG_HOME="$STATE/xdg/config"
export XDG_CACHE_HOME="$STATE/xdg/cache"
export XDG_DATA_HOME="$STATE/xdg/data"
export XDG_STATE_HOME="$STATE/xdg/state"
export XDG_RUNTIME_DIR="$STATE/xdg/runtime"
GODOT_TMPDIR="${FORTIS_TMPDIR:-$STATE/tmp}"
export TMPDIR="$GODOT_TMPDIR"
unset FORTIS_TMPDIR
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME" \
  "$XDG_STATE_HOME" "$XDG_RUNTIME_DIR" "$MESA_SHADER_CACHE_DIR" \
  "$STATE/fontconfig-cache" "$HOME" "$TMPDIR"
chmod 700 "$XDG_RUNTIME_DIR"

# Use the shared fonts, but keep Fontconfig's generated cache in this Worktree.
cat > "$FONTCONFIG_FILE" <<EOF
<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig>
  <dir>$SYSROOT/usr/share/fonts</dir>
  <cachedir>$STATE/fontconfig-cache</cachedir>
  <config></config>
</fontconfig>
EOF
exec "$GODOT" "$@"
