# 3D Character QA

Apply to rigged characters, skeletal animation and locomotion.

## Review

- Facing versus velocity: confirm the model faces the intended direction. Strafe and backward motion are valid only when intended by the brief.
- Gait: legs alternate coherently; no limb freeze, mirrored gait error or sudden loss of motion.
- Feet: check contact, sliding, floating, floor penetration and left/right timing.
- Root and rig: body/root displacement agrees with bone motion; no unintended double movement.
- Poses: balance, center of gravity, anticipation, follow-through and readable silhouettes.
- Rig/mesh: no severe deformation, intersections, twisting or detached parts.
- Loops and transitions: no frozen final pose, popping or discontinuity where continuous motion is expected.

## Evidence

Use synchronized Front / Side / Top / Perspective views when they clarify the pose, plus chronological perspective frames. Include actor position/velocity, facing/yaw, animation state/time, grounded state and foot positions when available.

For the asset-level runner, configure the actor's optional `character` block in `asset.qa.json`: relative `skeleton_path`, `foot_bones.left/right`, `motion_mode`, and either `animation_player_path` or `animation_tree_path`. Add `loop_states`, `jump_state` and `landing_policy` when relevant. The validator requires this capture block whenever the `3d-character` module is selected. The capture records skeleton bone count, foot positions in world and actor space, AnimationPlayer clip/time/length/loop mode, and AnimationTree state/time when configured.

## GPT focus

Inspect feet and body over multiple consecutive frames. Do not claim foot sliding from one still. Use metrics to support, not replace, visual judgment.
