#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SYSROOT="$ROOT/.local-tools/system-libs"
XVFB="$ROOT/.local-tools/bin/Xvfb"
XAUTH="$SYSROOT/usr/bin/xauth"
export LD_LIBRARY_PATH="$SYSROOT/usr/lib/x86_64-linux-gnu:$SYSROOT/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH="$SYSROOT/usr/bin:$PATH"
export LIBGL_ALWAYS_SOFTWARE=1
export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
export GALLIUM_DRIVER=llvmpipe
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330
export __EGL_VENDOR_LIBRARY_FILENAMES="$SYSROOT/usr/share/glvnd/egl_vendor.d/50_mesa.json"
export __GLX_VENDOR_LIBRARY_NAME=mesa
export XKB_CONFIG_ROOT=/tmp/xkb
export DISPLAY="${DISPLAY:-127.0.0.1:97}"
export XAUTHORITY="$ROOT/.local-tools/xvfb-auth"
mkdir -p "$ROOT/.local-tools/xvfb-logs" "$ROOT/.local-tools/mesa-cache"
: > "$XAUTHORITY"
chmod 600 "$XAUTHORITY"
cookie="$(python3 -c 'import secrets; print(secrets.token_hex(16))')"
"$XAUTH" -f "$XAUTHORITY" add "$DISPLAY" MIT-MAGIC-COOKIE-1 "$cookie"
log="$ROOT/.local-tools/xvfb-logs/xvfb.log"
"$XVFB" ":${DISPLAY##*:}" -screen 0 1280x720x24 +iglx -nolisten unix -listen tcp -pn -auth "$XAUTHORITY" -fp "$SYSROOT/usr/share/fonts/X11/misc" >"$log" 2>&1 &
pid=$!
cleanup() { kill "$pid" 2>/dev/null || true; wait "$pid" 2>/dev/null || true; rm -f "$XAUTHORITY"; }
trap cleanup EXIT INT TERM
for i in $(seq 1 40); do
  if ! kill -0 "$pid" 2>/dev/null; then cat "$log" >&2; exit 3; fi
  sleep 0.25
  if [[ $i -ge 3 ]]; then break; fi
done
set +e
"$ROOT/tools/godot.sh" --display-driver x11 "$@"
status=$?
set -e
exit "$status"
