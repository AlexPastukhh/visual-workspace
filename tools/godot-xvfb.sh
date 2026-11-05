#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS="$ROOT/.local-tools"
STATE="$ROOT/.fortis-state/godot-xvfb"
SYSROOT="$TOOLS/system-libs"
XVFB="$TOOLS/bin/Xvfb"
XAUTH="$SYSROOT/usr/bin/xauth"
XKBCOMP="$SYSROOT/usr/bin/xkbcomp"
XKBCOMP_REAL="$(readlink -f "$XKBCOMP")"
export LD_LIBRARY_PATH="$SYSROOT/usr/lib/x86_64-linux-gnu:$SYSROOT/lib/x86_64-linux-gnu${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export PATH="$SYSROOT/usr/bin:$PATH"
export LIBGL_ALWAYS_SOFTWARE=1
export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
export GALLIUM_DRIVER=llvmpipe
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330
export __EGL_VENDOR_LIBRARY_FILENAMES="$SYSROOT/usr/share/glvnd/egl_vendor.d/50_mesa.json"
export XKB_CONFIG_ROOT="$SYSROOT/usr/share/X11/xkb"

# Each invocation gets its own auth file, temp dir and log; reserve a display across Worktrees.
mkdir -p "$STATE/runs" /tmp/fortis-xvfb-locks
if [[ ! -x "$XKBCOMP" ]]; then
  echo "xkbcomp is missing from the shared runtime: $XKBCOMP" >&2
  exit 2
fi
# This Xvfb build invokes xkbcomp from its compiled /tmp/ path.
if [[ -L /tmp/xkbcomp ]]; then
  if [[ "$(readlink /tmp/xkbcomp)" != "$XKBCOMP_REAL" ]]; then
    ln -sfn "$XKBCOMP_REAL" /tmp/xkbcomp
  fi
elif [[ -e /tmp/xkbcomp ]]; then
  echo "/tmp/xkbcomp exists and is not a symlink; refusing to replace it." >&2
  exit 2
else
  if ! ln -s "$XKBCOMP_REAL" /tmp/xkbcomp 2>/dev/null; then
    if [[ ! -L /tmp/xkbcomp || "$(readlink -f /tmp/xkbcomp)" != "$XKBCOMP_REAL" ]]; then
      echo "Could not install the Xvfb xkbcomp link at /tmp/xkbcomp." >&2
      exit 2
    fi
  fi
fi
RUN_DIR="$(mktemp -d "$STATE/runs/run.XXXXXX")"
LOCK_DIR=""
pid=""
cleanup() {
  if [[ -n "$pid" ]]; then
    kill "$pid" 2>/dev/null || true
    wait "$pid" 2>/dev/null || true
  fi
  [[ -n "$LOCK_DIR" ]] && rmdir "$LOCK_DIR" 2>/dev/null || true
  rm -rf "$RUN_DIR"
}
trap cleanup EXIT INT TERM
export TMPDIR="$RUN_DIR/tmp"
export FORTIS_TMPDIR="$RUN_DIR/tmp"
mkdir -p "$TMPDIR"
export XAUTHORITY="$RUN_DIR/Xauthority"
log="$RUN_DIR/xvfb.log"
cookie="$(python3 -c 'import secrets; print(secrets.token_hex(16))')"

DISPLAY_NUM=""
for attempt in $(seq 1 80); do
  candidate=$((100 + RANDOM % 900))
  candidate_lock="/tmp/fortis-xvfb-locks/$candidate.lock"
  if mkdir "$candidate_lock" 2>/dev/null; then
    port=$((6000 + candidate))
    if ! python3 -c 'import socket,sys; s=socket.socket(); s.settimeout(0.15); r=s.connect_ex(("127.0.0.1", int(sys.argv[1]))); s.close(); sys.exit(0 if r == 0 else 1)' "$port"; then
      DISPLAY_NUM="$candidate"
      LOCK_DIR="$candidate_lock"
      break
    fi
    rmdir "$candidate_lock"
  fi
done
if [[ -z "$DISPLAY_NUM" ]]; then
  echo "Could not reserve a free Xvfb display." >&2
  exit 4
fi

# The container's X11 socket directory is not root-owned; use authenticated TCP and connect over loopback.
export DISPLAY="127.0.0.1:$DISPLAY_NUM"
echo "XVFB_DISPLAY=$DISPLAY"
chmod 700 "$RUN_DIR"
: > "$XAUTHORITY"
chmod 600 "$XAUTHORITY"
"$XAUTH" -f "$XAUTHORITY" add "$DISPLAY" MIT-MAGIC-COOKIE-1 "$cookie"
"$XVFB" ":$DISPLAY_NUM" -screen 0 1280x720x24 +iglx -nolisten unix -listen tcp -pn \
  -auth "$XAUTHORITY" -xkbdir "$SYSROOT/usr/share/X11/xkb" \
  -fp "$SYSROOT/usr/share/fonts/X11/misc" >"$log" 2>&1 &
pid=$!

ready=0
for i in $(seq 1 40); do
  if ! kill -0 "$pid" 2>/dev/null; then cat "$log" >&2; exit 3; fi
  if python3 -c 'import socket,sys; s=socket.socket(); s.settimeout(0.15); r=s.connect_ex(("127.0.0.1", int(sys.argv[1]))); s.close(); sys.exit(0 if r == 0 else 1)' "$((6000 + DISPLAY_NUM))"; then
    ready=1
    break
  fi
  sleep 0.25
done
if [[ "$ready" -ne 1 ]]; then
  cat "$log" >&2
  echo "Xvfb did not open TCP display $DISPLAY." >&2
  exit 5
fi

"$ROOT/tools/godot.sh" --display-driver x11 --audio-driver Dummy "$@"
