# Humanoid capture adapter fixture

This is a technical regression fixture for the asset-level 3D Character capture adapter. It reuses the existing GameBot GLB and is not a new production character asset.

## Intended sequence

1. Idle from 0–2 s.
2. Forward Walk from 2–4 s.
3. Forward Run from 4–6 s.
4. One Jump from 6–8 s, with takeoff, apex, landing and a held final pose after the one-shot clip completes.

The actor moves along its configured local forward axis. There is no boundary wrap or intentional strafe in this fixture.

## Capture requirements

- Real Godot runtime frames at 24 FPS.
- Perspective frames plus synchronized Front / Side / Top / Perspective views.
- Skeleton bone count and both foot-bone world/actor-space positions.
- AnimationPlayer clip name, playback position, length and loop mode.
- AnimationTree state-machine current state and playback position.
- Motion mode, loop-state expectations, jump state and landing policy in the captured character record.

## Review intent

Verify that the asset-level runner can collect character evidence from a manifest without project-specific capture code. Judge loop continuity, gait distinction, foot motion and jump completion from the images and metrics; do not infer artistic quality from a technical PASS.
