# Asset-level Visual QA Runner

This runner audits one asset at a time. Game Animation Lab remains a separate regression runner for deeper controller and AnimationTree state-machine tests.

## Supported capture adapters

| Asset kind | Actor nodes | Evidence |
|---|---|---|
| `2d_scene` | `Node2D` | Whole-scene PNG sequence, per-actor position/velocity/facing/rotation, contact sheet |
| `3d_scene` | `Node3D` | Perspective PNG sequence, position/velocity/forward/yaw/facing alignment/height/grounded, optional synchronized Front / Side / Top / Perspective composites |
| `3d_scene` + actor `character` block | `Node3D` with `Skeleton3D` | Skeleton bone count, named left/right foot-bone positions in world and actor space, AnimationPlayer clip/time/length/loop mode, optional AnimationTree state/time |

The shared capture script provides 2D Scene, 3D Transform and contract-driven 3D Character evidence. The optional actor `character` block is required when selecting the `3d-character` QA module. It declares NodePaths relative to the actor, the skeleton, left/right foot bones, motion mode, expected loop states and jump/landing policy. Configure either `animation_player_path` or `animation_tree_path`; both may be supplied when the scene uses both.

Game Animation Lab still retains its specialized AnimationTree state-machine regression tests. The asset-level adapter complements that runner with reusable skeletal and foot evidence; it does not replace the specialized tests.


## Start a new asset with shared stages

Ordinary textures, 2D/3D content scenes and standard AnimationPlayer clips do not need
new capture code. Put the editable content in Asset Workbench, then prepare its review scene:

~~~bash
python3 tools/visual_qa/new_asset.py --id my-sprite --kind 2d --resource assets/my-sprite/source/sprite.svg
python3 tools/visual_qa/new_asset.py --id my-prop --kind 3d --resource assets/my-prop/source/model.glb --clip Open --clip Close
~~~

The command creates only preview.tscn, brief.md and asset.qa.json.
It accepts an existing asset directory containing source files but refuses to overwrite
any of those three files. Fill in the brief, verify the visible forward axis, select QA
modules and adjust actor paths/phases to the task. --seconds-per-phase defaults to 2.
A static asset may need a shorter inspection phase; keep enough samples for animation.

The maintained stages live in projects/asset-workbench/qa/:
stage_2d.gd, stage_3d.gd and clip_sampler.gd. The preparer references them rather than
copying scripts into every asset. Scenes provide a neutral background and 3D lighting/floor;
they also play in a normal Godot scene run. Examples:
assets/pulse-beacon-2d/ and assets/rotor-beacon-3d/.

A unique AnimationPlayer is discovered automatically; otherwise pass --player-path
relative to the content root. Original loop/one-shot/ping-pong policy is preserved.
No animation is repaired or renamed. Active AnimationTree controllers are rejected by
the simple clip sampler: use a task-specific scene adapter for those, procedural movement,
physics, root motion and transitions. Such task code is expected, not a failure of reuse.
The generic capture runner and review packaging stay unchanged.

The starter is intentionally scoped to Asset Workbench. Existing projects can use their
own scene implementing qa_set_time; the character fixture is an example. Add dynamic
resource dependencies with --dependency; literal res:// references in scenes, resources
and scripts are collected recursively. Verify runtime inputs when loading assets dynamically.

For a skeletal character, add the actor character block and 3d-character module as
documented below; names of skeletons/bones and controller semantics are task-specific.

## Framing and readable sheets

Optional capture.multiview configures the four-view capture without editing its script:

~~~json
{
  "actor_id": "subject",
  "target_offset": [0, 1, 0],
  "distance": 7,
  "height": 1.5,
  "fov": 42
}
~~~

The offset is in world axes relative to the actor position. Distance scales all four
camera offsets; height affects front/side/perspective views. Old manifests retain their
previous framing. Framing changes invalidate capture keys. Stage exports
camera_distance, target_offset and content_scale control the neutral main view.
These are initial settings, not a promise of automatic fitting for every model.

Sheets include each selected frame's original sequence index and timestamp below its
tile; JSON retains the exact mapping. Full-resolution PNG sequences remain untouched.

## Deterministic scene contract

A supported scene must implement:

~~~gdscript
func qa_set_time(seconds: float) -> void:
    # Set the complete scene state for this exact time.
    pass

func qa_reset() -> void:
    qa_set_time(0.0)
~~~

The runner sets `Engine.time_scale = 0` and calls `qa_set_time` for each sample before rendering. This prevents render cost from advancing simulation faster than the timestamp. The scene must set transforms/animation state directly from the requested time; it must not depend on accumulating wall-clock deltas.

The manifest records `capture.time_control: "qa_set_time"`. The runner rejects scenes without this method rather than producing misleading timestamps. At every discontinuity between selected intervals, capture samples the immediately preceding time to seed velocity. Full and partial runs therefore use the same one-frame velocity interval.

## Playback timing and QA windows

Preview playback slots live in preview.tscn (clips and seconds_per_phase); QA windows live
in asset.qa.json. They have different meanings and need not have equal durations.
The preparer adds expected_clip to each generated clip phase. Capture compares it with
the actual AnimationPlayer assignment through qa_current_clip() at every sampled time;
a mismatch fails with phase/time/expected/actual evidence. The expectation is part of
the capture cache key and the actual clip is recorded in metrics/review metadata.

Keep expected_clip when adjusting or splitting a generated clip's QA window. Multiple
windows may inspect the same clip; a window crossing into another clip must be split or
have its meaning corrected. To alter actual playback timing, edit the preview schedule
and then choose the intended QA windows. Static/custom phases may omit the clip assertion.
A custom scene using expected_clip must expose qa_current_clip() with the real active clip.

## Define and validate an asset

Each asset has:

- `brief.md`: intended appearance, behaviour, timing and acceptance criteria.
- `asset.qa.json`: project, scene, actor NodePaths, phases, capture settings, selected QA modules and dependency files.
- Editable source files and runtime exports.

JSON Schema defines shared structural constraints for editors and tooling. The complete
runtime check is validate_asset.py: it reads the shared keys, patterns, enums and capture
limits from that schema, then checks repository paths and cross-field semantics (phase
overlap, dimension, non-zero forward vector, character bindings). Schema-only validation
does not establish runtime validity. Keep structural constraints in the schema; extend
semantic checks and regression tests in Python without maintaining a second constraint list.

~~~bash
python3 tools/visual_qa/validate_asset.py --manifest projects/asset-workbench/assets/planes-dual-pass/asset.qa.json
python3 tools/visual_qa/validate_asset.py --manifest projects/asset-workbench/assets/car-jump-turn-reverse/asset.qa.json
python3 tools/visual_qa/validate_asset.py --manifest projects/game-animation-mvp/assets/qa-character/asset.qa.json
~~~

The contract-driven character example is `projects/game-animation-mvp/assets/qa-character/`. Its actor `character` block is the reference for skeleton, foot-bone and animation evidence configuration.

## Brief and acceptance status

Technical draft captures may run with a missing, empty or unfinished brief. Reports and
review prompts expose brief_status and mark final_acceptance as blocked_by_brief in those
cases. Replace the generated placeholder and remove its draft marker when describing the
actual result. A provided brief changes the status to pending_visual_review, not approval:
GPT must still judge whether its intent/criteria are sufficient and inspect the images.
Brief-only edits rebuild the review package while reusing valid capture artifacts.

## Run

Run commands from the Visual Workspace repository root:

~~~bash
python3 tools/visual_qa/run_visual_qa.py --asset projects/asset-workbench/assets/planes-dual-pass/asset.qa.json
python3 tools/visual_qa/run_visual_qa.py --asset projects/asset-workbench/assets/car-jump-turn-reverse/asset.qa.json --phase turn_180
python3 tools/visual_qa/run_visual_qa.py --asset projects/asset-workbench/assets/car-jump-turn-reverse/asset.qa.json --force-rebuild
python3 tools/visual_qa/run_visual_qa.py --asset projects/game-animation-mvp/assets/qa-character/asset.qa.json
~~~

The runner imports Godot resources first (`--import`), then renders deterministic scene samples in Godot and builds contact sheets. This samples clip poses/explicit scene state; it does not test free-running controller transitions or physics. A phase-only run captures only the requested phase; the deterministic scene adapter makes it unnecessary to render earlier phases.

## Outputs and cache

Runtime results are written to the project's ignored `.fortis-state/visual-qa/<asset-id>/run-<timestamp>/` directory. Each phase contains:

- `frames/frame_XXXX.png`: the complete, chronological runtime sequence for that phase.
- `metrics.json`: timestamp, actor transforms and derived velocity/facing metrics for each frame; character actors also include skeleton count, named foot-bone world/actor positions and configured animation-player/tree state.
- `contact_sheet.png` and `contact_sheet.json`: overview plus selected frame metadata.
- For 3D phases with multiview enabled, `multiview/frame_XXXX.png` and its own contact sheet.

The run root contains `review_manifest.json`, `review_prompt.md`, `summary.md`, `run.json` and per-step logs.

Cache entries are isolated by asset and phase under `.fortis-state/visual-qa/asset-cache/`. Capture fingerprints include manifest phase settings, dependency SHA-256 hashes, Godot version/binary/wrappers and capture-script hash. Contact-sheet layout/build settings have a separate key. Cached files are hash-checked before reuse. A changed dependency invalidates only the affected phase; a changed contact-sheet layout rebuilds review artifacts without re-running Godot.

Use `--force-rebuild` for a clean capture. Output directories are unique and are never overwritten. Cache writes are skipped if the repository's Git status changes during the run.

## Tests and visual review

~~~bash
python3 -m unittest discover -s tools/visual_qa/tests -v
# Clean checkout: import GLB/SVG resources before direct Godot readiness test.
./tools/godot.sh --headless --path projects/asset-workbench --import
./tools/godot.sh --headless --path projects/asset-workbench --script "$PWD/tools/visual_qa/tests/runtime_readiness.gd"
# After full QA runs for planes-dual-pass and rotor-beacon-3d:
python3 tools/visual_qa/tests/verify_capture_regressions.py
# Clip expectation, partial-window, cache and draft/final-acceptance regressions:
python3 tools/visual_qa/tests/verify_audit_regressions.py
~~~

A technical PASS means the configured runtime bundle is complete; it is not an artistic verdict. Review the brief and selected modules in `qa/INDEX.md`, inspect the contact sheets, then inspect individual PNGs around important events. GPT must receive actual image content through Fortis Repo's `read_multiple_files` and `image(item)` flow, not merely file paths or JSON. See [tools/README.md](../README.md) for the verified transfer procedure.

## Boundaries and cache interpretation

A technical bundle PASS means evidence is complete, not that the asset satisfies its brief.
Use [Common QA](../../qa/modules/common.md) for direction acceptance. The car regression
checks visible bumper landmarks independently from configured forward metadata.

A shared GLB/script change conservatively invalidates every phase depending on that file.
Per-clip semantic invalidation and a generic transition dependency graph are not implemented
in this runner. Smaller phase-local input files can provide finer reuse when useful.
Specialized Game Animation Lab retains its own state/transition cache and runtime tests.

Generic character clip metadata resolves simple state-machine names matching clip names.
Blend spaces, renamed/nested states and arbitrary AnimationTree graphs require additional
task-specific evidence. Foot-sliding and separation thresholds remain optional future work.

For an independent blind visual audit, give a fresh reviewer the brief and image package
without the defect key. Existing technical tests and a review by the author are not that audit.
