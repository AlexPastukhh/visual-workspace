# Practical acceptance tests — Visual Workspace

This folder is the **permanent test kit in the repository**, not a place for
test runs, generated game projects, reports or temporary captures. It exercises
the [visual use cases](../docs/use-cases/README.md) and the existing written
[brief → implementation → evidence → review](../WORKFLOW.md) contract.
For each independent creation order, the **task's written brief** is the
acceptance reference. Asset-level briefs/manifests in the existing projects
remain their own source of truth; this kit does not replace them.

The original V01–V09 and C01–C06 benchmark prompts remain **immutable**:
visual blind tests and standard C-creation tests do not publish fixtures or
GitHub Issues by default. The historical VR01 prompt exercises one versioned
owner review. New [scenario tests SC01–SC05](scenarios/README.md) reuse the
existing A01–A05 briefs, but add **three separate user messages in one new
chat**: create/publish v1, owner change/publish v2 in the same Issue, then
owner change/publish v3 in the same Issue. These are different test IDs and
cannot be counted as completed historical C01–C05 runs.

## Primary method: send a ready-made prompt to a new chat

Open a **fresh chat with Fortis Repo**, copy the complete text of ONE file
from [prompts/](prompts/) and send it as your ordinary user request.
All delivered prompts use the canonical accepted main at
`/workspace/repo/Repos/visual-workspace/`; they do not rely on the
preserved `initial-visual-workspace` task tree. No
`run.py` command, pre-created run, agent launcher or test framework is
required. The new chat follows the workspace README/bootstrap, independently
reads the existing brief/fixtures, performs the task and saves **all output**
in its own unique Workfiles run directory. It must not edit the repository.

| Ready-to-send prompt | What it checks |
| --- | --- |
| [V01 — review five animations](prompts/V01-review-all.md) | Historical larger visual review prompt (untimed) |
| [V02 — review one animation](prompts/V02-review-one.md) | Historical single visual review prompt (untimed) |
| [V03 — one 2D animation, separate chat](prompts/V03-review-2d.md) | Historical independent cold test (no measured timing) |
| [V04 — one 3D animation, separate chat](prompts/V04-review-3d.md) | Historical independent cold test (no measured timing) |
| [V05 — 2D pair, basic](prompts/V05-review-2d-pair.md) | Two 2D cases, separate evidence, measured full time |
| [V06 — 3D trio, intermediate](prompts/V06-review-3d-trio.md) | Three 3D cases with varied movement, measured full time |
| [V08 — mixed pair, everyday default](prompts/V08-review-mixed-pair.md) | One 2D + one 3D, independent verdicts, measured |
| [V09 — mixed pair, optimized reporting](prompts/V09-review-mixed-pair-reporting.md) | Same input/quality as V08; separate time spent drafting, writing, checking reports |
| [V07 — mixed five, extended](prompts/V07-review-mixed-five.md) | Broad 2D/3D stress test, five verdicts, measured |
| [C01 — create 2D asset](prompts/C01-create-2d-asset.md) | Written brief → editable 2D art → Godot preview |
| [C02 — create 3D asset](prompts/C02-create-3d-asset.md) | Written brief → Blender model → Godot preview |
| [C03 — create 2D animation](prompts/C03-create-2d-animation.md) | Original 2D art, clips, loops, visual review |
| [C04 — create 3D animation](prompts/C04-create-3d-animation.md) | Original 3D rig/animation, import, review |
| [C05 — make a playable game](prompts/C05-create-playable-game.md) | Asset + animation + controller, gameplay and input testing |
| [C06 — two independent orders](prompts/C06-create-multiple-orders.md) | *Optional* multi-order stress test; not the default production order |
| [VR01 v1 — versioned GitHub owner review](prompts/VR01-versioned-review-v1.md) | One fresh chat; original asset v1 → real owner feedback → v2 same-Issue, typed ALLOW, browser proof; only with explicit owner authorization |
| [SC01–SC05 — multi-message versioned production scenarios](scenarios/README.md) | Reuse A01–A05; create v1, then two real owner change messages and v2/v3 comments in the original Issue |
| [SV01–SV03 — sequential visual QA scenarios](review-scenarios/README.md) | Two primary grouped read-only defect-review scenarios; third optional 2D→3D context switch |

**Cold-chat execution matrix:** [CLEAN-CHAT-MATRIX-20261119.md](CLEAN-CHAT-MATRIX-20261119.md) distinguishes prepared prompts from NOT RUN independent tests. **Scenario matrix:** [SCENARIO-MATRIX-20261120.md](SCENARIO-MATRIX-20261120.md) tracks SC01–SC05 separately; they are all initially NOT RUN. VR01 uses real public GitHub side effects only after explicit owner authorization and cannot be executed autonomously in this chat.

**Recommended default:** send **V08** for a fast cross-dimension review
(two cases and one bootstrap) or **V05** / **V06** for focused 2D / 3D
regressions. Use V07 only for wider, slower acceptance. For production,
send **one written order per new chat**: C01/C02 = simple static object,
C03/C04 = medium animated asset, C05 = difficult playable integration.
C06 remains an exceptional multi-order capability test. Do not bundle
unrelated production orders just to amortize bootstrap.

**Reporting performance comparison:** the original V08 remains immutable.
V09 checks the *same two inputs* (`clip-m4`, `clip-r2`) with the same
full-resolution image coverage, per-case verdicts and four report outputs,
but keeps reports compact and measures T4→T5 in three subphases.
Run **V09 in a new chat** for the next measurement. Compare outcome quality,
actual frame coverage, T0→T5, T4→T5 and the extra R1/R2 marks; count
differences in prompt, model/config, cache/network/tool conditions.
The previous mixed-pair run reported **549.912 seconds** T0→T5 and
**282.707 seconds** T4→T5. That interval includes tool waiting; it is
*not evidence* that writing text alone required 282.707 seconds.
Its self-described "V08-like" invocation is a useful historical baseline,
not a controlled identical-prompt replicate. A faster run with missed
frames/incorrect verdicts is a regression, not an optimization.

**Every new recommended prompt measures time**, from the first clock
reading *before workspace README* through final verified output, using
the [timing protocol](TIMING.md). New production C01–C06 prompts also
include this timing requirement. V03 and V04 originally ran against a
**different README path** in the preserved historical worktree; their
original reports have no comparable measured wall-time. This delivered
copy points at the canonical accepted main README, so the original reports
are historical quality smoke tests, **not byte-identical prompt reruns**.

After the chat finishes, inspect its Workfiles outputs and assess them
against each written brief. For all visual cases, compare with the evaluator-only
answer key **only after** submission. Do not give the tested chat the key,
an old review or a verdict. These prompts are normal user requests,
not a special instruction format or automated agent execution.

## Sequential visual defect review scenarios — SV01–SV03

Two **primary** scenarios cover the existing five visual clips without combining unrelated work: [SV01 2D turnaround pair](review-scenarios/SV01/01-review-k7.md) and [SV02 3D jump/Walk group](review-scenarios/SV02/01-review-jumps.md). The [optional SV03 2D→3D switch](review-scenarios/SV03/01-review-2d.md) probes context switching using previously seen fixture IDs; it **does not** add new cases or independent observations of the model. [Scenario instructions](review-scenarios/README.md) and [execution matrix](REVIEW-SCENARIO-MATRIX-20261120.md) have exact two-message sequences.

Each SVxx starts in a new Fortis Repo chat, receives message 01, submits an independent review and timing, then receives message 02 **in the same chat**. The tested chat must not read later prompts, evaluator-only keys, old reports, or upcoming cases before the owner sends each part. Every clip gets a separate PASS/FAIL/UNCERTAIN and exact full-resolution frame evidence; conclusions in one part cannot stand in for analysis of another.

All SVxx visual cases and main repository stay read-only, with one Workfiles report folder per scenario. No task worktree, GitHub Issue, media publication or owner review. The historical V01–V09 prompts remain immutable; these scenarios are **additional** longitudinal tests, and cases within a chat are correlated. To test independently again, repeat the same fixed scenario in another fresh chat.

## Independent work-unit evaluation and unplanned repair steps

Use [the independent evaluator unit gates](_evaluator/unit-gates/README.md) **after each** submitted scenario part, not only the end. A different chat reviews raw source/images/QA/receipts. If it finds an objectively material defect, the owner pauses the planned next message and sends a separate corrective instruction in the **original runner chat**. Re-evaluate that intervention and preserve its extra source SHA, same-Issue revision, first-pass FAIL and rework time. The original immutable prompts remain unchanged; SV blind-review interventions must not leak expected defect labels.

## Multi-message owner change scenarios

Use the [SC01–SC05 index](scenarios/README.md) for the exact sequence and
[2026-11-20 matrix](SCENARIO-MATRIX-20261120.md). One scenario **starts** in a
fresh chat; the owner then sends step 02 and step 03 as **new messages in that
same chat**, only after reviewing the previous GitHub PNG. The version change is
a legitimate new design request, not necessarily a defect fix. The agent must
preserve the continuing task and revised requirements, edit the **same source**,
perform relevant QA and publish v2/v3 as separate comments on the original
Fortis-created Issue. The one permitted exception to A01–A05 Workfiles-only
output is committed **editable source** in a registered task worktree for
reproducible revision SHA; QA and reports stay in isolated Workfiles.

The original C01–C06 prompts remain strictly Workfiles-only and do not grant
GitHub publication. The new SCxx.01 prompts explicitly authorize their own
public PNG v1 Issue; later user messages authorize the corresponding changes.
Check live Gateway policies before **each** write. Never treat PNG preview as
proof of animation playback, 3D source delivery or actual gameplay acceptance.
All 15 SCxx prompt texts are immutable once accepted. For retesting with changed
instructions, create a new SC ID/version rather than edit the historical run.

## Testing strategy: independence versus time

Use **two complementary modes** rather than one chat per asset forever.

| Mode | Chat allocation | What can be concluded |
| --- | --- | --- |
| **Cold / independent** | One selected prompt in a **fresh chat**, no prior hints or feedback. V03/V04 are completed historical baselines; use V08 or a focused prompt for new timed tests. | Bootstrap, tools and this task can be assessed independently. One successful run is a smoke test, **not** a reliability estimate. |
| **Batch / regression** | One fresh chat processes several **different** cases in one prompt, with separate verdicts and **no feedback between cases**. V05 = two 2D; V06 = three 3D; V08 = mixed pair; V07 = five-case stress. | Per-case correctness and screening speed. Cases **within the same chat are correlated**; do not count them as independent replicates. |
| **Production / composition** | One fresh chat performs **one** written order: C01/C02 basic static, C03/C04 animated, C05 full game. C06 is optional special batch capability, not normal production. | The real production workflow; judge each requested deliverable and the combined integration. |
| **Confirmation** | If a result is surprising/failed, repeat **the same unchanged prompt** with another fresh chat; for higher confidence use several fresh runs. | Whether the failure is reproducible, rather than an artifact of a long conversation or one attempt. |

**Do not give results, scores, corrections or the evaluator key to a test-taking
chat before its last answer.** The key lives in the same repository and can
be read by an agent with unrestricted repository access; instructions are
**not a security boundary**. For strictly held-out grading, keep the key
outside the tested agent's accessible storage. Publishing a test run to
GitHub is also **not** implied by a practical-test prompt; owner-directed
showcase delivery belongs to [UC-VIS-009](../docs/use-cases/media-github-review.md#uc-vis-009). Several prompts sent sequentially to one chat
are allowed for exploratory work, but it becomes a *continuation* and is not
a new cold run. If the goal is a comparable batch, prefer one explicit
multi-case prompt from the start and save separate reports. An additional
chat is required when independence matters; a new Workfiles folder alone
does not reset the conversation.

### Minimal practical cycle

1. We already have independent quality baselines V03 (2D) and V04 (3D),
   **but no total duration data for them**. For the next timed baseline,
   run V08 in a clean chat: two different dimensions, one bootstrap.
   Use V05 or V06 in separate fresh chats when 2D/3D coverage matters.
2. For frequent fixes, choose one relevant **2–3 case** prompt with
   varied input and independent per-case conclusions, without revealing
   its expected labels to the tested chat.
   Reserve V07 (five cases) for occasional broad regression/acceptance;
   do not routinely rerun every expensive creation task.
3. If an observation is false, missing or inconsistent, examine the actual
   submitted image evidence, and confirm with one or more fresh chats
   **without changing the prompt or revealing the defect**.
4. When changing capture strategy/FPS/frame selection, compare at fixed
   briefs and fixtures. Record exactly which frames each chat *actually*
   received; equal contact sheets do not mean equal temporal coverage.
   Do not conclude that a sparse frame sample proves absence of a
   single-frame fault.
5. Periodically run **one production order per chat** at the relevant
   complexity: C01/C02 for fast source/export smoke, C03/C04 to exercise
   animation and visual QA, C05 for milestone end-to-end gameplay.
   Run C06 only to explicitly test simultaneous commissions.
   Keep authored deliverables and their visual reviews in Workfiles.

### Compare the same thing, measure both quality and speed

For **every** chat/run record: prompt ID/version, exact case IDs or order ID,
workspace Git HEAD **and dirty-worktree state**, model/configuration if known,
which PNG frames were really inspected, findings with timestamps, technical
checks and output path. New prompts must save `timing.md` with observed
UTC **T0–T5** from the [protocol](TIMING.md), covering bootstrap,
brief/plan, first real image/preview, review/tests and final reporting.
For multi-case visual QA also record per-case start/end; for authoring
record first real Godot preview and full completion separately. These
tool-reported timestamps measure T0–T5, **not** user UI send-to-delivery
latency, and can be affected by waiting or cold caches. Model guesses
or cache-only timings cannot replace an independently clocked total.

Score each 2D/3D **visual case** against its written brief, including a
no-defect verdict, localization and false positives, and keep the per-chat
grouping. Score each **created unit** separately against its written
acceptance criteria, editable source, Godot import, actual visual evidence
and gameplay where requested. Compare only runs with comparable prompts,
inputs, visual evidence and environment; label batch and cold results
separately. See the [evaluator rubric](_evaluator/README.md).

### When new tests are added

- Reuse this folder: each new visual case gets a **unique immutable case ID**,
  `brief.md`, `capture.json`, full PNGs and a contact sheet. Validate a
  presumed-good control with real image review; when seeding a fault,
  confirm it appears on the images, and document the secret key only under
  `_evaluator/`. A normal-looking clip is not automatically perfect.
- New creation orders get their own numbered `authoring/*.md` **written
  brief**, with independent acceptance criteria and output ownership.
  Use a ready-to-send `prompts/*.md` only for a new **user-level task**;
  do not write a special launcher for each case.
- Do **not overwrite** old fixture images, briefs or prompt text used for
  comparison. Give changed/new tests a new ID or version, and retain which
  suite version each earlier Workfiles run used. Add new cases to a future
  batch prompt **without editing the existing benchmark prompt**.
- Keep reusable fixtures/prompts in this repository, all run outputs in
  Workfiles. Independent human/AI assessment stays outside the test chat.
  No additional orchestration service is required for this workflow.

## Fixed kit versus disposable runs

- **Permanent, in this repository:** `practical-tests/visual/cases/`
  contains anonymous PNG animation fixtures with individual `brief.md`,
  `capture.json` and overview `contact_sheet.png`; `authoring/`
  contains six independent creation briefs and ready-to-send natural-language
  prompts in `prompts/`; `run.py` is an optional run-folder helper.
- **Evaluator only:** `_evaluator/answer-key.json` contains known controls.
  Do not open it when completing a blind review.
- **Disposable, outside the repo:** each run belongs under
  `/workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<run-id>/`.
  Input copies, created 2D/3D assets, Godot projects, evidence, scores and
  reports live **only** inside that run directory.
- Never put a new task's output into `practical-tests/`, `projects/` or
  project-local `.fortis-state/`. Existing Godot/Blender launchers may create
  their pre-existing ignored runtime settings; do not modify project sources.
  Authors work with independent standalone projects in Workfiles.

## Optional helper for preparing and cleaning run folders

The natural-language prompts above are the normal test interface. If the
owner wants to pre-create a Workfiles folder, the optional `run.py` helper
copies inputs into it. These commands are **not** required for a new chat
to fulfill any prompt. From the existing linked task worktree:

~~~bash
python3 practical-tests/run.py list
python3 practical-tests/run.py new --visual clip-k7 --visual clip-t9
python3 practical-tests/run.py new --order A03-2d-animation
python3 practical-tests/run.py new --order A05-playable-composite --order A06-multi-order
~~~

The command prints the exact Workfiles run path and `INSTRUCTIONS.md`.
When using this optional helper, give the fresh chat the assigned Workfiles
run path along with the prompt. Without it, the chat creates its own unique
run folder as instructed by the prompt. In both cases keep the defect key,
old visual reviews and case labels from leaking to the reviewer.
For a truly independent comparison, use another chat and evaluate its
submission *after* it has finished. Do not let the reviewer self-grade.

For a copied run read `input/visual/<case>/brief.md`; for a direct
prompt, read `practical-tests/visual/cases/<case>/brief.md`. Check `capture.json`,
then inspect the actual images from `frames/` and `contact_sheet.png` via
the [Fortis image-transfer flow](../tools/README.md#передача-png-в-визуальный-контекст-gpt-через-fortis-repo).
Full sequences are preserved: sparse sheets alone cannot rule out
single-frame defects. Record `output/visual/<case>/review.md` with verdict,
local frame/time, observations, uncertainties and requested further evidence.
Do not consult `_evaluator/` from the new chat.

For authoring runs, read each `input/authoring/*.md` if copied, or the
original `practical-tests/authoring/*.md` named in the prompt; use the appropriate
[UC-VIS-001–005,007](../docs/use-cases/README.md) and the full
[production and review workflow](../WORKFLOW.md). Original editable source,
export, complete standalone Godot project, real runtime images, tested
controller behaviour and brief-aligned acceptance are required only when
the individual order specifies them. Do not substitute an existing demo for
new work. For A06, the two independent outputs must be assessed separately.

The repository's existing `tools/godot.sh`, `tools/godot-xvfb.sh` and
`tools/blender.sh` may target projects/assets under Workfiles; the worktree
itself stays read-only for the authoring test. Contact sheets can be built
from numbered Workfiles PNG sequences by the existing tool described in
[tools/README.md](../tools/README.md#external-video-and-frame-sequences).
The generic manifest runner restricts projects to the repository; do not
pretend it supports Workfiles projects. Use actual Godot runtime capture
and project-specific input tests in the isolated project when required.

## Optional check / deliberate cleanup for helper-created runs

The commands below work only for folders prepared by `run.py` (they have
its own run sentinel). A fresh chat following a ready-made prompt normally
creates its Workfiles folder itself; inspect that exact folder after the chat
finishes and clean it up only by an explicitly reviewed, path-scoped action.
Do not assume `run.py cleanup` can delete such manually created runs.

~~~bash
python3 practical-tests/run.py check <run-id>
python3 practical-tests/run.py cleanup <run-id> --confirm <run-id>
~~~

`check` inventories input frame counts and submitted artifacts; it **does not**
grade visual quality. Clean-up of a helper-created run requires an exact run ID and sentinel; only
that single run under Workfiles is deleted. No automatic expiry or deletion of
another chat's run, no prune glob, and no deletion of source test fixtures.
Preserve evidence before deleting a run if the comparison is still needed.

## Existing acceptance and unresolved boundaries

**Visual:** 5 prepared 2D/3D PNG animation cases with distinct written
briefs. The expected labels, whether defects were injected and their
localization belong **only in the evaluator-only files**. No sample here
is claimed to be certified production-quality artwork.

**Creation:** A01 static 2D; A02 static 3D; A03 animated 2D; A04 animated
3D; A05 full asset → animation → playable mini-game; A06 multiple independent
2D/3D orders. Written requirements allow objective checks of intended result,
file format/size, clip policy and game behaviour. Qualitative artistic
evaluation still requires actual images and a reviewer.

Compare results with the **held-out evaluator key and rubric**
(`_evaluator/`) only after the reviewer submits. Report misses, false
positives, localization, acceptance failures, actual runtime tests,
time-to-first-preview and rerun time. No stable reliability score is claimed
until independent new-chat runs are collected. The key is separated by
procedure, not enforced by file access controls within the shared repo.
