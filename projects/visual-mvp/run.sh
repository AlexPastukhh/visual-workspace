#!/usr/bin/env bash
set -euo pipefail
cd /work
app="${1:-}"; version="${2:-v1}"
case "$app:$version" in
  2d:v1|2d:v2)
    python3 scripts/prepare_ora.py "$version"
    xvfb-run -a krita "output/2d/scene_${version}.ora" --export --export-filename "output/2d/scene_${version}.kra"
    xvfb-run -a krita "output/2d/scene_${version}.kra" --export --export-filename "output/2d/preview_${version}.png"
    test -s "output/2d/scene_${version}.kra" && test -s "output/2d/preview_${version}.png"
    ;;
  3d:v1)
    blender --background --factory-startup --python-exit-code 9 --python scripts/blender_scene.py -- create /work/output/3d
    test -s output/3d/scene_v1.blend && test -s output/3d/preview_v1.png
    ;;
  3d:v2)
    test -s output/3d/scene_v1.blend
    blender --background output/3d/scene_v1.blend --python-exit-code 9 --python scripts/blender_scene.py -- revise /work/output/3d
    test -s output/3d/scene_v2.blend && test -s output/3d/preview_v2.png
    ;;
  *) echo 'Usage: bash run.sh {2d|3d} {v1|v2}' >&2; exit 2;;
esac
printf 'RUN_OK %s %s\n' "$app" "$version"
