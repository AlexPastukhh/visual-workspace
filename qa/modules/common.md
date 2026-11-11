# Common Visual QA

Apply to every asset. Compare the actual Godot playback with the asset brief; the brief defines intent.

## Review

- **Readability:** is the silhouette/action understandable at intended gameplay scale and camera distance?
- **Direction and intent:** does the motion do what the brief says, including facing versus travel direction? Identify the visible front from geometry or landmarks; alignment calculated from a configured axis is not independent proof that the model faces that way.
- **Timing and spacing:** are acceleration, deceleration, holds and phase durations intentional?
- **Continuity:** are there freezes, unexplained pauses, pops, jitter, abrupt scale/position changes or broken transitions?
- **Motion design:** are arcs, balance, anticipation and follow-through appropriate to this action?
- **Visual integrity:** clipping, intersections, deformation, cropping, flicker or inconsistent scale?
- **Composition:** do framing, contrast and background help the action remain readable?

## Evidence

Use real Godot runtime PNGs in chronological order, contact sheets for overview, timestamps and relevant transforms/metrics. A contact sheet is not a substitute for individual frames. Add targeted frames only where evidence is ambiguous.

## GPT review prompt

Review the attached images as a time-ordered sequence of actual Godot playback. Compare them with the brief. State what works well, what does not, and which improvement has the best value relative to its cost. Ground every finding in frame indices/timestamps and visible evidence. Separate observation, metric-backed fact and hypothesis. Do not infer a defect from missing context; say what minimum extra evidence is needed. Technical PASS is not an artistic verdict.

Return PASS / PASS WITH CONCERNS / FAIL, strengths, prioritized findings, uncertainties and the most valuable next improvement.
