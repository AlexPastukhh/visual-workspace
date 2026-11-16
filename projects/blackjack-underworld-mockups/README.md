# Blackjack Underworld — UI Sketches

Three manually authored Godot UI mockups for the first playable prototype.

- `scenes/roster.tscn` — select 3–4 people from the roster.
- `scenes/blackjack.tscn` — autonomous human Blackjack; people stay in one horizontal row.
- `scenes/underworld.tscn` — the same table after the cards transfer to the spirit's hand.

All visible elements are drawn with native Godot canvas primitives and text.
No AI image generation, external images, generated portraits, or downloaded assets are used.

## Run

From the Visual Workspace root:

```bash
./tools/godot-xvfb.sh --path projects/blackjack-underworld-mockups
```

Open the project in Godot and change the main scene to inspect another state,
or launch a specific scene with `--scene res://scenes/blackjack.tscn`.
