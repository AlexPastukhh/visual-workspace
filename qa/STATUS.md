# Visual QA implementation status

Updated: 2026-11-06

## Workflow entry and task decisions

AGENTS.md now routes asset tasks to the single WORKFLOW.md. The workflow explicitly selects
existing capabilities before implementation, obtains an early visual result, adapts evidence
to the task, prioritizes high-value corrections and defines completion and reuse-promotion
criteria. The tool index links authoring, stages, procedural examples and specialist QA.
These instructions improve task decisions; fixture/cache timings below are not benchmarks
of production asset quality or total creation time.

## Ready for ordinary asset tasks

The shared runner captures one asset or phase, PNG sequences, actor metrics, contact sheets
with frame/time captions, and configurable synchronized 3D views. Shared neutral stages and
the new_asset.py preparer cover textures, 2D/3D content scenes and ordinary AnimationPlayer
clips without per-asset capture code. See the authoritative tool commands and limitations in
[Visual QA Runner](../tools/visual_qa/README.md).

A task may still need procedural behaviour, a controller adapter, explicit actor/bone paths,
framing and phase configuration. That work is acceptable. The infrastructure must be reused;
zero task-specific programming is not the completion criterion.

## Correctness fixes verified

- Vehicle forward metadata now agrees with the actual exported geometry (+Z).
  Actor yaw and wheel rotation were corrected together. Runtime assertions use the real
  FrontBumper and RearBumper positions and world-space travel, rather than trusting metadata.
  New FRONT images show the hood/front splitter, not the rear spoiler.
- Every discontinuity between captured intervals seeds the preceding sample.
  A fresh two-interval capture matches the corresponding full-run actor metrics exactly.
- Rejecting an existing output directory preserves its original run.json.
- Framing settings are validated and included in capture fingerprints. A capture test
  confirmed that changed settings alter the actual multiview PNG.
- Clip sampler preserves looping/one-shot policy. Ordinary previews also animate in normal
  Godot runtime. It refuses active AnimationTree controllers rather than silently overriding them.

## Latest clean full evidence

| Asset | Runtime frames | Full capture directory |
|---|---:|---|
| pulse-beacon-2d | 48 | projects/asset-workbench/.fortis-state/visual-qa/pulse-beacon-2d/run-20261106T033945Z |
| rotor-beacon-3d | 48 | projects/asset-workbench/.fortis-state/visual-qa/rotor-beacon-3d/run-20261106T034154Z |
| planes-dual-pass | 168 | projects/asset-workbench/.fortis-state/visual-qa/planes-dual-pass/run-20261106T033550Z |
| car-jump-turn-reverse | 156 | projects/asset-workbench/.fortis-state/visual-qa/car-jump-turn-reverse/run-20261106T033346Z |
| gamebot-humanoid | 192 | projects/game-animation-mvp/.fortis-state/visual-qa/gamebot-humanoid/run-20261106T033643Z |

Total: 612 primary runtime frames plus configured synchronized multiview composites.
New 2D and 3D assets contain editable content scenes and generated preview configuration;
no asset-specific capture script was added.

The 3D beacon's first visual review found a gap below the rotor. Its editable content was
corrected with a hub, then only that asset was recaptured and visually rechecked.
Reviews of the two starter assets and the corrected car are stored with their full captures.

## Verification

- Asset-level unit tests: 30/30 passed.
- Godot runtime readiness checks: 15 assertions passed (visible forward/reverse, wheel roll,
  clip movement/loop/one-shot/ping-pong, static 2D/3D content, shared stage camera and ordinary preview playback).
- Fresh gap/framing capture regressions: READINESS_CAPTURE_REGRESSIONS_PASS.
- Game Animation Lab run_tests.sh: ALL_TESTS_PASS.
- All five full-asset repeat runs reused every phase and contact sheet, with no Godot steps:
  0.674 / 0.523 / 0.761 / 1.124 / 1.102 seconds for the assets in the table order.
- Generic humanoid capture still covers all four phases with skeleton/foot/animation evidence.

## Task settings and playable integration

Parameter announcements and game-ready acceptance have one home in
[WORKFLOW.md](../WORKFLOW.md#evidence-required-for-game-ready-delivery).
The verified playable example, commands, observations and evidence locations are documented in
[Animation Relay](../projects/playable-animation-demo/README.md#verified-result-and-scope).
Game-ready claims remain limited to the target/runtime/build actually tested.

## Audit corrections

Clip assertions/cache invalidation, early format rejection, schema-sourced shared constraints
and brief acceptance status are verified. Interface details have one home in the
[runner documentation](../tools/visual_qa/README.md).
Validation: 30 unit tests and five capture regressions passed; representative fresh 2D,
3D and character captures plus 15 Godot readiness assertions also passed.
Evidence: projects/asset-workbench/.fortis-state/audit-regressions/b439ab2abb/.
The accidental literal newline escapes in WORKFLOW.md are removed.

## Boundaries and remaining work

- Deterministic pose sampling does not validate production physics, root motion or free-running
  controller transitions. Use task-specific runtime tests where those behaviours matter.
- Complex AnimationTree graphs require task-specific evidence; the current generic metadata
  fallback supports simple state names matching animation clip names.
- Shared-file changes conservatively invalidate all dependent phases. Semantic per-clip GLB
  invalidation and a generic transition dependency graph are not part of this runner.
- Automatic foot-sliding/separation thresholds and automatic camera fitting are optional
  improvements, not prerequisites for the current asset workflow.
- A fresh-reviewer blind audit of deliberately faulty variants has not been completed.
  Do not describe the author's technical/visual regression checks as a blind audit.

## Repository state

Implementation and results are saved in the existing worktree. No commit or push was made.
Generated evidence remains in ignored project-local .fortis-state directories.
