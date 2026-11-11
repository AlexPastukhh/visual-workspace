#!/usr/bin/env bash
set -euo pipefail

ROOT="$(git rev-parse --show-toplevel)"
COMMON_DIR="$(git -C "$ROOT" rev-parse --path-format=absolute --git-common-dir)"
PRIMARY_ROOT="$(cd "$COMMON_DIR/.." && pwd)"
SOURCE="$PRIMARY_ROOT/.local-tools"
DEST="$ROOT/.local-tools"

if [[ "$ROOT" == "$PRIMARY_ROOT" ]]; then
  echo "This is the primary clone; shared tools already live here."
  exit 0
fi
if [[ ! -d "$SOURCE" ]]; then
  echo "Shared tools directory not found: $SOURCE" >&2
  exit 2
fi
if [[ -L "$DEST" ]]; then
  if [[ "$(readlink -f "$DEST")" == "$(readlink -f "$SOURCE")" ]]; then
    echo "Shared tools link is already correct: $DEST -> $SOURCE"
    exit 0
  fi
  echo "Refusing to replace an existing .local-tools symlink: $DEST" >&2
  exit 3
fi
if [[ -e "$DEST" ]]; then
  echo "Refusing to replace existing Worktree path: $DEST" >&2
  exit 3
fi

ln -s "$SOURCE" "$DEST"
echo "Linked shared tools: $DEST -> $SOURCE"
