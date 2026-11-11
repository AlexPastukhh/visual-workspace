# Visual QA tools

This is the supported capture and evidence-packaging workflow for **Game Animation Lab**. It is project-specific: scene paths, node properties, skeleton bone names and runtime state schedule are defined in the profile.json file.

The runner is read-only with respect to source assets and runtime controllers. It writes generated frames, metrics, logs and reports only under the selected .fortis-state output directory.

## Run the complete workflow

Run from projects/game-animation-mvp:

~~~bash
python3 tools/visual_qa/run_visual_qa.py
~~~

Optional arguments:

~~~bash
python3 tools/visual_qa/run_visual_qa.py \
  --profile tools/visual_qa/profile.json \
  --output-dir .fortis-state/visual-qa/manual-run \
  --timeout 300
~~~

The default is a full-coverage incremental run: all four 2D and all four 3D states remain in the review package, but a state is recaptured only when its dependency fingerprint is stale. Unchanged state frames, metrics and contact sheets are restored from the local cache.

- --force-rebuild ignores every state/contact-sheet cache and reruns structural/smoke tests, all 2D and 3D captures, all contact sheets, packaging and bundle verification. A successful rebuild refreshes the cache.
- --force-tests bypasses only the broader structural/smoke-test cache; it does not force runtime recapture.
- The cache is stored under .fortis-state/visual-qa/state-cache/; it is local generated state and is not committed to Git.

The output directory must not already exist. Without --output-dir, the runner creates a timestamped folder under .fortis-state/visual-qa/.

Both runtime captures use the profile's fixed_fps value (24 by default) so sample schedules are repeatable. The verifier reconstructs each configured schedule and rejects timestamp drift greater than max_schedule_drift_frames (2 by default). The 2D capture waits for the render frame, pauses the scene while saving the image, and then resumes; the 3D capture freezes the SceneTree for synchronized multiview rendering.

A successful tool run means capture, packaging and bundle validation completed. It does **not** mean the assets passed visual QA. Deterministic findings may be present while the runner itself exits successfully.
## Standard capture profile

The default profile captures a 12-second 2D/3D demo:

| Channel | States | Samples |
|---|---|---:|
| 2D runtime | Idle 24, Walk 30, Run 45, Jump 24 | 123 |
| 3D perspective | 24 per state | 96 |
| 3D synchronized multiview | 12 per state | 48 composites |

Idle is sampled in two intervals: before movement and again after Jump. This makes the return to Idle visible.

The 3D multiview composite contains Front, Side, Top and Perspective views of one frozen pose. The four SubViewports share the same World3D; their cameras are positioned before one render update. The capture records the AnimationTree playback position before and after rendering. A change during capture is reported as a critical synchronization finding.

The profile also defines the model's local forward axis, foot bone names, expected loop modes, whether facing/velocity alignment is a requirement, Jump's auto-demo landing policy and contact-sheet layout. This demo intentionally strafes with a fixed model facing, so alignment is recorded as evidence but is not a pass/fail rule. Jump may hold its completed final pose until the configured demo segment ends; the verifier checks the runtime state against the profile schedule. Change these values only when the scene or asset contract changes.
## Runner stages

1. Existing structural and runtime smoke tests. A successful result is reused only when the project inputs, imported Godot resources, Godot launcher and engine version have the same fingerprint; missing import artifacts or any input change forces the tests to run again.
2. 2D runtime capture with sprite frame/count/loop mode, frame progress, state, position, velocity and grounded state.
3. 3D runtime capture with AnimationTree node/time/length/loop mode, actor position/velocity, grounded state, model yaw/facing, movement direction and foot transforms.
4. Contact-sheet generation for 2D, 3D perspective and 3D multiview. All 12 sheets are built in one Godot process; each sheet, timestamp manifest and selected-frame set is retained.
5. Review package creation: review_manifest.json and review_prompt.md.
6. Bundle validation and deterministic findings.

## Incremental state cache

The runner caches each state independently: 2D Idle / Walk / Run / Jump and 3D Idle / Walk / Run / Jump. A cache entry contains the captured PNGs, state metrics, contact sheets, selected-frame PNGs and their checksums. On every run, the runner validates the cache manifest, file hashes, expected sample counts, image dimensions and multiview counts before reuse. Missing, corrupt, unsupported or unverifiable entries are recaptured; the cache never substitutes a path-only reference for the actual PNGs.

Dependency invalidation is deliberately conservative:

- A changed 2D atlas cell invalidates only the animations that use that cell. Changes to the 2D sampling timeline invalidate all 2D states because sequence indices are global and chronological. Changes to the 2D scene, controller, capture script, import settings, project render settings or engine also invalidate all 2D states.
- The GLB is fingerprinted as shared model/rig data plus individual animation-clip data. A clip-only edit invalidates that clip and the next 3D state whose incoming 0.16-second cross-fade can depend on it. Changes to the 3D sampling timeline invalidate all 3D states because sequence indices are global and chronological. Shared mesh, skeleton, scene, controller, capture script, import settings, camera configuration or engine changes also invalidate all 3D states. If the GLB layout cannot be parsed safely, the runner falls back to hashing the whole GLB and invalidates all 3D states.
- Contact-sheet settings or the contact-sheet builder can invalidate sheets without recapturing runtime frames.
- The complete metrics bundle is reassembled and verify_bundle.py runs on every invocation. Review manifests and prompts are also regenerated for the current output directory.

A changed state is captured by itself while preserving its original global sequence indices and timestamps. The capture script advances the real demo to the selected state window; it does not shorten the sample count or reduce the 3D perspective/multiview coverage. The 3D successor state is also invalidated when needed to recheck the incoming cross-fade. A full run therefore means full project coverage, not necessarily a full re-render.

State cache entries are committed only after capture, contact sheets, review packaging and bundle validation all succeed and the Git working tree status remains unchanged. A failed or interrupted run does not publish its partial cache entries. Existing entries remain available until a successful replacement is committed.

## Repeat-run performance

The broader structural/smoke-test result is cached separately in ignored .fortis-state/visual-qa/test-cache.json. Any project input or imported-resource change invalidates this broad test result, so a one-clip edit may rerun the smoke tests even though only the affected animation states are recaptured. Runtime captures and contact sheets use the finer per-state cache described above.

Contact sheets are generated by one headless Godot invocation rather than twelve separate launches. This changes process startup overhead only; it does not change the number, selection, dimensions, or contents of the sheets or selected source frames.

## Output layout

~~~text
run-*/
  2d/
    metrics.json
    idle/ walk/ run/ jump/
      <state>_NNNN.png
      contact_sheet.png
      contact_sheet.json
      selected/
  3d/
    metrics.json
    perspective/
      idle/ walk/ run/ jump/
    multiview/
      idle/ walk/ run/ jump/
  findings.json
  summary.md
  review_manifest.json
  review_prompt.md
  run.json
  *.log
~~~

Each contact-sheet manifest maps selected tiles to the original sequence index and timestamp. review_manifest.json lists all 12 contact sheets and three chronological image groups: 2d, 3d-perspective and 3d-multiview. Every frame entry includes its absolute path, sequence index, timestamp, expected state and observed state.
## Deterministic checks

Current findings include:

- 2D Run reuses Walk atlas frames by design in this MVP. This is reported only when the profile explicitly requires an independent Run cycle.
- 2D animation loop mode differs from the profile, or an expected looping animation stops during its scheduled segment.
- 2D Jump stops before reaching its final pose while airborne, or has not reached and held its final frame by the end of the scheduled Jump segment. The auto-demo may retain the completed Jump state until that segment ends.
- 2D / 3D controller state or the active sprite/AnimationTree clip differs from the state reconstructed from the profile schedule; the recorded expected state is also checked against that schedule.
- 3D animation loop mode differs from the profile (Idle / Walk / Run are linear loops; Jump is one-shot; High severity).
- Jump's final pose/state behavior is interpreted according to the configured auto-demo landing policy; the state must still leave Jump when the next scheduled state begins.
- 3D facing alignment is checked only when forward-facing locomotion is explicitly required by the profile. The current demo uses fixed-facing strafing.
- AnimationTree playback advances during the supposedly frozen multiview capture.

Findings include severity and supporting metric evidence. They are technical signals, not an artistic verdict. For non-looping 2D Jump clips, holding the last frame after playback completes is not treated as a freeze; stopping before the final frame is. The verifier also requires the one-shot to have completed by the end of its scheduled segment. A valid 2D capture must include sprite_frame_count for every sample so these checks cannot silently degrade. Foot transforms are recorded, but calibrated automatic foot-sliding classification is not yet implemented; inspect the images and metrics directly.
## Transfer images to GPT through Fortis Repo

Read the manifest, then send the contact sheets first. Use the read_multiple_files result's content_items and pass each image item through image(item):

~~~js
const result = await tools.mcp__Fortis_Repo__read_multiple_files({ paths });
const images = (result.content_items ?? []).filter(item => item.type === "image");
text({ requested: paths.length, received: images.length });
for (const item of images) image(item);
~~~

For individual frames, use one group from review_manifest.json and read small chronological batches of four images. Check that received equals requested for each batch. Keep the corresponding frame metadata from the manifest beside the images. Do not dump image Base64 through text(result).

Use review_prompt.md as the independent review instruction. Add the asset brief and intended movement; the reviewer must not treat the deterministic findings as a complete list of defects.
## Scope and limitations

- This runner is tuned to scenes/demo_2d.tscn and scenes/demo_3d.tscn; it is not a universal Godot scene auditor.
- verify_bundle.py currently knows the Game Animation Lab atlas path and expected state contract.
- Facing alignment depends on the configured front_local_axis. Verify the axis against the model before trusting the dot product.
- Foot positions are recorded in world space and actor-local space. Visual foot sliding, floating, floor penetration and artistic quality still require GPT review.
- The runner never repairs assets or changes controller code. It only captures evidence and reports deterministic signals.
- If a state schedule changes, update both segment windows and sample counts in profile.json; the bundle verifier checks the expected sample totals.
- Runtime PNGs, reports and logs belong in ignored .fortis-state/, not in Git.
