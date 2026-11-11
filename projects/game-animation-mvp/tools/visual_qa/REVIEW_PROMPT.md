# Visual QA review prompt

You are reviewing game-animation assets from a real Godot runtime capture. Treat the attached images as a chronological sequence, not as unrelated stills. The accompanying review manifest maps every image to its sequence index, timestamp, expected state, actual state and capture channel.

## Review rules

- Inspect the contact sheets first for broad patterns, then inspect the individual frames in chronological order.
- Do not infer correctness from passing technical tests or from deterministic findings alone.
- Compare the observed result with the project brief and expected behavior. If the brief is missing, state which conclusions cannot be made.
- Separate direct visual observations, metric-backed technical evidence and hypotheses.
- Do not invent defects. Distinguish intentional strafing/backward movement from an orientation bug when the brief supports it.
- Cite exact sequence indices and timestamps for every issue.
- If evidence is insufficient, request only the smallest additional frame interval or camera view needed.
- Note successful aspects as well as defects.

## Common checks

1. Is the action and silhouette readable at the intended gameplay scale?
2. Does the movement match the intended direction and gameplay purpose?
3. Do poses progress continuously, without freezes, stutters or unexplained holds?
4. Are timing, spacing, arcs, balance and transitions intentional?
5. Are there visual artifacts, popping, scale changes, intersections or clipping?
6. Do loops repeat continuously where looping is expected?
## 2D-specific checks

- Frame order, pivot/baseline and character scale remain stable.
- Frames do not jitter, crop body parts or hold too long unintentionally.
- Idle, Walk and Run are distinct where the brief requires distinct motion.
- Jump timing matches the physical airborne interval. A completed non-looping one-shot may hold its final pose; in this auto-demo, the Jump state is intentionally held until the configured Jump segment ends. Check that the animation reaches its final pose and that the controller leaves Jump when the next scheduled state begins.
- Inspect the source atlas and runtime captures as separate evidence when both are provided.

## 3D-specific checks

- Use Front, Side, Top and Perspective views as synchronized views of the same pose.
- Compare model facing with movement velocity only when the profile requires forward-facing locomotion. This demo intentionally moves sideways with a fixed model facing, so a zero facing/velocity dot product is not itself a defect.
- Check foot contact, sliding, floating, floor penetration and left/right gait timing.
- Check root movement against the skeleton and feet.
- Look for mesh deformation, intersections and abrupt changes across transitions.
- Treat clip loop mode, current animation time, grounded state and foot transforms as supporting evidence, not as a replacement for the images.

## Final response

Return a verdict: **PASS / PASS WITH CONCERNS / FAIL**.

Then provide:
1. What works well.
2. Findings ordered by severity, each with evidence and timestamps.
3. What remains uncertain and what minimal evidence would resolve it.
4. The single most valuable next improvement, including its expected benefit and cost.

Do not change assets or runtime code during the review. This is an independent audit of the supplied evidence.
