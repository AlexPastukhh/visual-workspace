# 2D Animation QA

Apply to animated sprites and 2D scene motion.

## Review

- Frame order and timing communicate the intended action; no accidental duplicate, missing or held-too-long frames.
- Pivot, baseline, scale and silhouette remain stable unless a change is intentional.
- No cropping, jitter, sudden sprite flips or inconsistent spacing between animation frames.
- Facing direction agrees with the intended travel direction, including after turns.
- Motion reads at the actual in-game size, not only when enlarged.
- Loops repeat cleanly when required; one-shot actions reach their intended final pose.
- Check source frames/atlas separately from the actual Godot playback when both are available.

## Evidence

Use the complete runtime frame sequence at the configured FPS, a contact sheet, frame/timestamp metadata and per-actor position/facing metrics. For multi-actor scenes, also apply Multi-Actor Motion.

## GPT focus

Inspect the sequence, not just the sheet. Look for frame holds, temporal pops, direction changes, pivot drift and loss of silhouette readability. Identify exact frames/timestamps.
