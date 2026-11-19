# Visual Workspace — asset production workflow

This is the authoritative process for new and existing 2D/3D assets, animations and game integration.
Select the requested goal or composition in the [use-case registry](docs/use-cases/README.md);
this document owns the shared process rather than separate procedures for each goal.
An external video-only review uses UC-VIS-006; multiple independent deliverables
and parallel agents use UC-VIS-007 with exclusive output ownership.
Infrastructure and Git/worktree rules remain in the repository and Fortis documentation.
When a result is ready for the **owner to review**, use the single
[UC-VIS-009: versioned media review and GitHub handoff](https://github.com/AlexPastukhh/visual-workspace/blob/main/docs/use-cases/media-github-review.md#uc-vis-009).
It owns issue/revision links, owner approval, reproducible source provenance and retention;
this document owns production and technical QA. Do not publish every internal draft.
Live model (verified 2026-11-19): one Issue per logical asset/order; v1
creates it and v2+ use append-only comments in that same Issue. Both typed
PNG operations are scoped ALLOW for `visual-workspace` (public repository).
Before each GitHub write refresh live capabilities; use `prepare_visual_revision`
and the immutable payload digest, source SHA and original Issue reservation.
Never create a fallback second Issue for a same-asset revision or replay an
UNCERTAIN write. Require owner browser verification of linked PNG and keep
`ISSUE_REVIEWED`, `SOURCE_MERGED` and `GAMEPLAY_ACCEPTED` distinct.
See [UC-VIS-009](docs/use-cases/media-github-review.md#uc-vis-009).

The goal is a good asset matching the task, with a short path to useful visual feedback
and efficient corrections. A successful tool run is evidence, not the definition of success.
Task-specific programming is normal; reuse the parts that are already solved.

## 1. Start with the task and the existing workspace

Read [QA Registry](qa/INDEX.md), [tool index](tools/README.md), and the relevant project's README.
Read Common and only the specialist QA modules selected for this task. Consult detailed tool
instructions when choosing or invoking that tool; do not load every old report or checklist.

Find the closest existing asset, source generator, controller, preview stage and QA setup.
Inspect what is reusable and what is intentionally specific to that example. Do not treat
the simple demo art or its known shortcuts as the quality target for a new commission.

Before implementation, state briefly:
- the intended result and the important quality requirements;
- which existing source/tool/stage/QA route will be reused;
- what task-specific work is needed and why;
- what the first visual check will establish.

### Announce the task parameters

For each new asset/animation task, show the user a compact parameter table before authoring
or an expensive capture. Include the relevant fields below; mark irrelevant fields N/A
instead of inventing values or forcing a long questionnaire.

| Parameter group | Values to declare when relevant |
|---|---|
| Target and delivery | Engine/project, target platform if known, expected use and what will be delivered |
| Formats | Editable source format, runtime/export format, preview/QA output format |
| Asset dimensions | 2D canvas/sprite-frame pixels, pivot/transparency; 3D units/scale and texture sizes or budgets |
| Animation | Clip names, durations, loop/one-shot, source frame/key sampling where relevant, in-place/root motion |
| Runtime constraints | Intended game size/camera, controller/rig compatibility, target runtime frame rate if required |
| QA capture | Resolution, capture FPS, selected phases/time intervals, derived frame count, views and relevant metrics |

For each declared value, identify its origin: user requirement, existing project constraint,
inference from the task, or proposed/default choice. Explain choices that affect quality,
compatibility or iteration cost. A parameter absent from the prompt is not automatically
unrestricted. Ask only if a consequential requirement cannot be safely inferred; otherwise
announce a reasonable provisional choice and proceed.

Distinguish file extension/format from image resolution. Also distinguish source animation
frame timing, QA capture FPS and runtime rendering/physics rates: they are not interchangeable.
A 24 FPS capture is not a requirement that a sprite animation or game itself run at 24 FPS.
Different useful sizes (source sprite, game viewport, QA frame, texture atlas) must be named.

Before capture/export, check the displayed values against the actual source/project settings
and manifest. Treat generated defaults as proposals, not approved task requirements.
Do not silently change a declared quality/compatibility parameter to make work faster.
When a relevant parameter changes, announce old → new, the reason and expected effect;
preserve explicit user constraints unless the user changes them. Routine internal constants
and temporary paths do not need announcements. For follow-up edits, show changed values and
carry forward the established ones rather than repeating the entire table.

This table is a user-visible view of the current settings, not a second configuration file.
Keep desired delivery constraints in brief.md; keep capture values only in asset.qa.json;
keep authoring/runtime settings in their native source/project files.

This can be a short progress update, not another mandatory planning document.
Clarify missing information only when it materially changes the result or blocks work.
Otherwise make a reasonable assumption and record durable intent in the asset brief.

## 2. Select the smallest suitable route

| Task | Reuse first | Task-specific work that may remain |
|---|---|---|
| Change an existing asset | Its source, scene, manifest and last useful review | Requested source/animation changes; update affected requirements |
| Static 2D/3D asset | Neutral workbench stage and asset preparer | Art/model, scale, framing, visible front and intended game-size review |
| Ordinary AnimationPlayer clips | Shared stage and clip sampler | Actual clips, phase durations, actor paths and acceptance criteria |
| Sprite-frame animation | Existing atlas/SpriteFrames pipeline as a reference | New art, frame timing and appropriate runtime content scene |
| Procedural or multi-actor motion | Closest scene/controller as reference; common asset capture | Trajectory, timing and actor behaviour, including qa_set_time when appropriate |
| Rigged character / controller | Generic skeletal evidence; existing character setup and controller tests where relevant | Bone/state bindings, gait/root motion and task-specific controller logic |
| Physics or complex AnimationTree behaviour | Relevant project runtime and existing sequential playback/tests | Inputs and sequential simulation/transition evidence, plus isolated visual capture where useful |

Commands, supported formats, example paths and limits belong in the [tool index](tools/README.md)
and [asset runner documentation](tools/visual_qa/README.md), not in another tool catalog here.
The preparer currently targets Asset Workbench; do not move an established project into it
merely to use a template. An existing compatible scene/manifest should be reused directly.

A custom movement script is legitimate asset work. A new capture script, runner, registry
or generic framework needs a demonstrated gap in the existing capabilities.
Extend the smallest existing component only if doing so is simpler or more valuable than
a local adapter. Do not generalize speculative future behaviour before the first result.

## 3. Define quality and prepare only what is needed

Each independently reviewed asset owns:
- brief.md: desired appearance/style, purpose, relevant scale/camera, action/timing and
  observable acceptance criteria; include supplied references when available;
- asset.qa.json: technical scene/actor/phase/capture bindings and input dependencies;
- editable source and required runtime exports.

Keep the brief short enough to use during review. Resolve artistic intent rather than
filling a large form. Do not duplicate QA capture configuration in the brief; delivery constraints belong there.
Verify the visible front, scale and paths instead of trusting template defaults.
The schema defines shared structure; the tool validator also checks runtime semantics. See the [contract and acceptance rules](tools/visual_qa/README.md#define-and-validate-an-asset).

Choose the authoring tool for the desired result: existing editable source first, then
the available 2D tools/Python or Blender as appropriate. Do not force every asset into
procedural primitives, an existing demo style or an unavailable application.

Prioritize silhouette/readability, proportions/style, coherent motion and visual integrity.
Polish materials, detail and secondary motion once those fundamentals work. Judge at the
intended game size/camera, not only in an enlarged standalone preview.

## 4. Get an early visual result before expensive completion

Build a small representative version and integrate it into Godot early. Check import,
orientation, scale, framing and the hardest visual/behavioural assumption before completing
all detail or every clip. Reuse the stage, capture and review tools already selected.

Use the smallest interval/views that answer this first question. This is a diagnostic
iteration, not final coverage. Avoid a full workspace rebuild or a long all-asset audit.
When owner feedback is needed at this checkpoint, publish a **selected, QA-checked**
preview through [UC-VIS-009](https://github.com/AlexPastukhh/visual-workspace/blob/main/docs/use-cases/media-github-review.md#uc-vis-009),
not raw transient cache paths. Keep the editable source and the review `run_id` distinct.
For an unchanged existing asset, inspect valid cached evidence before recapturing it.

Keep the editable-source → export → Godot integration path working during iteration.
If an early image exposes a source flaw, correct the source; do not hide it through
capture settings or silently alter imported animations to manufacture a PASS.

## 5. Choose evidence to match the acceptance question

| Question | Evidence to obtain |
|---|---|
| Static appearance, material, silhouette | Suitable views, game-size framing and individual PNGs; no long sequence of identical frames |
| Clip or procedural movement | Chronological frames at suitable FPS, contact sheet, phase/event timestamps |
| Loop or one-shot ending | Boundary frames and actual playback that demonstrates repeat/hold/completion as required |
| Several actors | Whole-scene sequence plus relevant per-actor evidence |
| Skeletal deformation or foot contact | Useful synchronized views and consecutive detailed frames, with bone/foot evidence when configured |
| Controller transition, root motion or collision | Actual sequential runtime behaviour and relevant existing tests; pose seeking alone is insufficient |

Use the [QA modules](qa/INDEX.md) for detailed review questions.
Deterministic qa_set_time capture gives reproducible poses/scene states and is appropriate
for many isolated asset reviews. It does not prove free-running physics or state transitions.
Test the actual target integration as well when that behaviour is an acceptance requirement.

### Evidence required for game-ready delivery

1. Agree the target game/controller and the [declared task parameters](#announce-the-task-parameters).
   Define clips, looping, transitions/interruption and in-place versus root motion as needed.
2. Create editable source; export actual game resources (2D frames/atlas or 3D model/rig/clips).
   Keep source, runtime resources and preview/test infrastructure separate.
3. Bind gameplay inputs/events to animation states and exit conditions in the real controller.
   Configure import/loop settings explicitly; movement, collisions and animation must agree.
4. Exercise sequential gameplay through relevant keys/buttons/events: start, transition,
   interrupt, finish/land and return to idle. Include meaningful invalid/boundary inputs.
   Pose seeking alone cannot prove these behaviours.
5. Review actual game-size frames against the brief and selected [QA modules](qa/INDEX.md);
   fix the source/integration and recheck affected behaviour.
6. Verify the delivered resources in a clean target project without QA stages, temporary
   files or author-specific paths. Check an exported build when required by the task.

Reuse the proven [Animation Relay input/visual test and agent loop](projects/playable-animation-demo/README.md#repeatable-input-e2e);
adapt its scenario to the game. Commands and protocol live only in that project's README.
If no target game is available, report the representative game tested and remaining limits.
Final claims must distinguish asset preview, playable integration and exported build.

Keep the chosen capture FPS and complete selected intervals. Improve speed through cache
reuse, affected-phase capture and avoiding irrelevant views/tests, not by silently reducing
temporal coverage. Static assets need only enough samples/views to inspect them.
A starter manifest is an initial configuration, not mandatory two-second coverage for everything.

## 6. Review images, then spend the next iteration where it matters

For standalone video/frame-sequence review (UC-VIS-006), first establish
source FPS, time origin and coverage. A contact sheet is a time overview, not
proof of smooth motion between its tiles. Keep the full ordered frames; inspect
short consecutive runs around impacts, landings, loops, changes of direction,
transitions and any suspicious jump. If a defect could last only 1–2 source
frames, sample those source frames rather than claiming a sparse overview
excludes it. For 3D use additional useful angles where available. Distinguish
what is directly visible from intended behaviour that requires a brief,
controller telemetry or an independent gameplay test.

GPT must receive actual PNG image content using the verified procedure in
[tools/README.md](tools/README.md#передача-png-в-визуальный-контекст-gpt-через-fortis-repo).
Start with an overview sheet, then selected chronological full-resolution frames and
important boundaries. Retain the full sequence; inspect more frames/views when uncertainty
or a suspected defect calls for them. Paths, metrics and contact sheets alone are insufficient
for claims about fine temporal or deformation quality.

Compare evidence with the brief and selected QA modules. Cite frame/time/actor for findings.
Separate visible observations, metric-backed facts and hypotheses. Check the actual visible
front independently of a configured axis. Technical PASS is not artistic acceptance.

Choose the next correction by effect on the requested result and effort:
1. Fix acceptance failures, broken motion, wrong direction, cropping and major visual defects.
2. Fix the largest remaining perceptual weakness: shape/style, timing, deformation or material.
3. Add polish when it provides a meaningful improvement for this task.

Do not stop at a technically valid but visibly weak result. Do not keep iterating on
speculative or imperceptible improvements after acceptance is met.
If uncertain, obtain the smallest additional evidence that resolves the uncertainty.

## 7. Recheck efficiently and finish the asset

During iteration, capture only affected asset phases and useful dependent behaviour.
Use the default cache; force rebuild only to diagnose cache/capture correctness or when
a clean run is specifically needed. A shared input may correctly invalidate several phases.
Do not rebuild unrelated assets, reinstall runtimes or recreate source files without cause.

Run tests according to the change:
- asset-only art/timing edits: relevant import/playback checks and visual review;
- a controller/export/rig change: relevant existing runtime/structural checks;
- shared tool changes: targeted regressions and representative affected fixtures.
Do not write a new test framework or rerun the entire regression library for every art edit.

Before completion, run the full intended path for the selected asset with cache reuse allowed.
Check required phases and event boundaries, relevant target integration, and before/after
evidence for fixes. A phase-only run cannot establish full-asset acceptance.

Draft capture is allowed, but a missing/template brief blocks final artistic acceptance.
A provided brief still requires judging its adequacy and the actual images.

Complete when the brief's acceptance criteria are met, meaningful visible defects are fixed,
relevant technical checks pass, and no unresolved uncertainty undermines the result.
Disclose remaining compromises relative to the task. A full workspace benchmark or independent
blind audit is a separate validation activity, not a compulsory gate for every asset.

For an owner-facing review, apply [UC-VIS-009](https://github.com/AlexPastukhh/visual-workspace/blob/main/docs/use-cases/media-github-review.md#uc-vis-009):
provide the **verified GitHub Issue URL**, revision and change summary, QA scope and
source commit/archive identity; distinguish `PREVIEW_ONLY` from delivery of actual
video/3D originals. Preserve older owner-shown revisions as evidence, and continue
editing the source in Docker/Git, not the Issue attachment. For game acceptance,
owner PR/merge and guarded Windows Mirror Pull precede the owner's Godot run.
Report the result in the user's terms: what was created/improved, how it matches the task,
what was visually checked and any material limitation. Test/frame counts are supporting
evidence, not the main outcome. Where speed matters, distinguish first capture from cached
iteration; cache timing alone is not the cost of creating a new asset.

## 8. Improve the workflow without accumulating unnecessary machinery

After a finished task, make a brief Knowledge Review:
- Nothing to promote: keep one-off observations with the asset.
- Extend existing: add a useful, verified review rule or technique to its current home.
- Create reusable component: only for a distinct, useful capability with a concrete reuse case.

One valuable discovery can justify an improvement; task complexity alone cannot.
If setup, rendering, reading redundant context or repeated manual work dominated the task,
identify the actual bottleneck. Improve that part when the saved work and quality justify
the maintenance cost. Do not assume that more automation or fewer scripts is always better.
Use real task outcomes to refine the process; simple fixture PASS results are not proof of
optimal production quality or speed.

| Information | Authoritative home |
|---|---|
| Which goal and nested use cases to select | docs/use-cases/README.md |
| How the agent works | This WORKFLOW.md; AGENTS.md only routes to the registry and owners |
| Available checks and their meaning | qa/INDEX.md and selected QA modules |
| Tool interfaces, examples and limitations | tools/README.md and the owning tool documentation |
| Desired asset result | Its brief.md |
| Technical QA bindings | Its asset.qa.json and the shared schema |
| Project setup | Its README |
| Runtime evidence, reviews and cache | Project-local ignored .fortis-state/ |

Apply DRY to code, configuration and documentation: reuse existing components, keep each
rule/value in one authoritative place, and link to it. Extend a shared component when
behaviour is genuinely shared; keep task-specific behaviour local.

Link to the authoritative home instead of copying rules. No parallel recipe catalog, worker, heavy dependency or instruction layer is required
unless a real task justifies it.
