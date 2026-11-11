# Visual feedback PoC (historical)

Isolated experiment proving: editable source -> raster PNG -> Fortis Repo image return -> ChatGPT visual inspection. It does not modify Game Animation Lab.

## Tested

- Pixel-art and vector SVG sources with raster PNG output.
- OBJ mesh with MTL materials.
- House preview projected from OBJ faces; it is not a Blender or Godot render.
- A preview defect was found, corrected, and re-inspected.

## Reproduce

Run from the repository root:

```bash
cd experiments/fortis-visual-poc
python3 generate.py
npm ci
node - <<'JS'
const fs = require('node:fs');
const { Resvg } = require('@resvg/resvg-js');
['sprite', 'vector', 'house_preview'].forEach(name =>
  fs.writeFileSync(`${name}.png`,
    new Resvg(fs.readFileSync(`${name}.svg`, 'utf8')).render().asPng()));
JS
```

## Scope

This PoC validates image return and visual feedback, not animation, rigging, engine import, or production mesh quality. Current app workflows are documented in [Blender runtime](../../tools/BLENDER_RUNTIME.md) and [Game Animation Lab](../../projects/game-animation-mvp/README.md).
