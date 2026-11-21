# Evaluator-only instructions — not for the test-taking chat

The key in answer-key.json is **not copied** to Workfiles runs by run.py.
The evaluator-only `verify_seeded.py` checks that the intended original
fault injections remain exact without revealing those case labels through
the public fixture verifier. Run this integrity check only as the
owner/evaluator **outside** the test-taking chat.
Within a shared repository it is not access-controlled secrecy: an agent
given arbitrary repo read permissions can open it. For truly blind tests,
the owner must prevent the evaluated agent from reading this directory and
withhold the correct labels until its output is final.

## Interpreting evidence across chats

Preserve the `cold`, `batch`, `production` or `confirmation` mode
for each reported result. Several case scores from **one chat** are
correlated observations, not independent model trials. Bootstrap and
warm-context durations should not be pooled as if the same conditions
held. A single V03/V04 pass confirms only the specific smoke test.
Do not infer a reliable success percentage from the current tiny fixture
set, and do not reveal the key before a test chat submits its final result.

When prompt text, source images, brief, sampling policy or the workflow
changes, record its version/HEAD and separate it from earlier results.
Keep existing examples immutable for before/after comparisons, and add
new previously unseen cases to detect overfitting to a fixed key.
Track time-to-first-preview and total end-to-end time separately, and
cite external timings where possible rather than relying on the tested
chat's unsupported claims.

## Timing and acceptance across complexity levels

All **new graded prompts** require [actual UTC timestamps](../TIMING.md)
T0..T5 recorded by the test-taking chat from tool-returned clock values,
not guessed human estimates. After the run, copy the
[scorecard template](scorecard-template.md) **into Workfiles** and fill it as
an independent evaluator, preserving the raw marks and any unknowns.

Compare **total T5−T0** (bootstrap, tools, reasoning, QA, reporting)
only for comparable prompts/fixtures/environments. Also report bootstrap
T1−T0, first image or actual Godot preview T3−T0, substantive work
T4−T2, and per-case review durations. The interval before T0 and after
T5 is not included; compare actual UI send-to-finish timing separately
if available. An attractive model-reported number without raw timestamps
is not a measured performance result.

For review tests V05 (2D pair), V08 (mixed pair), V06 (3D trio), V07
(five-case stress), compare both aggregate quality and each case's
individual verdict. They differ in scope, so do **not** rank models or
workflow versions solely by absolute runtime across different tiers.
For production C01/C02 test static basics, C03/C04 animation, C05
full gameplay; require one written order per normal test. C06 is an
optional multi-order workload and should not inflate the default test.

A speed improvement with degraded temporal coverage, fewer real Godot
previews, or a skipped requirement is **not** a valid optimization.
Record failures and rework without altering a fixed benchmark prompt.

## Visual detection scoring (per case)

**Роль оценщика — сравнивать результат испытуемого с evaluator-only key,
а не проводить собственный повторный поиск дефектов по PNG/анимации.**
Первый unit слепого SV01/SV02 проверяется только на корректность процесса
и замороженные индивидуальные ответы. После завершения всех частей
сопоставляй их с `answer-key.json`, при необходимости проверив целостность
seeded fixtures через `verify_seeded.py`. Ключ содержит известные
контрольные метки, а не гарантирует отсутствие любых художественных
особенностей; спор с эталоном отмечай отдельно, не переписывай key.
Для новых VT11/VT12 точный порядок —
[протокол проверки обнаружения](../actions/DEFECT-SCORING.md).

- 2 points: correct fault/no-fault verdict. No-defect controls count.
- 1 point: accurate temporal localization for a defective case (local frame
  index and/or time, within a relevant short interval); for a control, correct
  explicit assessment that examined frames reveal no material defect.
- 1 point: observations grounded in actual images and brief, distinguishing
  visible evidence from speculation/metrics.
- Minus 1 per material invented defect, floor at 0. A high-confidence false
  accusation on a normal case is a regression; no fabricated certainty.
- Track confusion matrix: TP/TN/FP/FN and localization separately. Avoid
  percentage conclusions from a single small sample or self-review.

## Authoring acceptance (per independent requested unit)

- 25% brief compliance: specified form, 2D/3D, proportions, colors/style,
  formats, sizes and named action requirements actually match.
- 20% editable source, export and Godot import: required real resources
  exist, project opens without missing dependencies.
- 20% animation/game behaviour: requested clips and loop policy work;
  where requested, actual user input and state transitions are exercised.
  Mark this block N/A and redistribute to other blocks for static orders.
- 25% visual evidence and self-critique: real game-size PNGs were received,
  relevant phases/views/loop boundaries were examined, observed shortcomings
  were addressed or explicitly disclosed.
- 10% efficiency/reproducibility: first preview and total time, chosen
  targeted tests, separate output units, repeat commands and no repo writes.
- An absent required editable source or game integration cannot be compensated
  by attractive screenshots. A technical PASS is not visual acceptance.
- For A06 grade crystal and column separately, then verify non-overlap.
  For A05 verify gate collision, out-of-range E, opening, exiting and reset.

## Evidence record template

Run ID / new chat ID (nonsecret), task/case, start/end timestamps, touched
paths, actual image paths inspected, observed issues with local frames/times,
objective test markers, final verdict, remaining uncertainty, first-capture
seconds, cached-repeat seconds. Compare with the key only after submitting
the tested model's output. Do not modify the test key based on reviewer guesses.

## Fixture provenance

Visual controls were copied from existing Visual Workspace captures and
two faults were seeded as a single abrupt frame replacement. The historical
walk-freeze example is from an earlier intentionally failing QA snapshot.
These are practical controls, **not** certified gold-standard production art.
The default selected set is balanced by dimension (2D normal/fault; 3D normal/
transient fault plus historical walk failure). Reviewers may have false alarms
about noncritical stylistic issues: require evidence and task relevance.

## Multi-message scenario overlay — SC01–SC05 (after each stage)
These are **additional gates** on the existing production/brief rubric, not a new evaluator service or a replacement for original C01–C06 scores. Original prompts A01–A05 and V01–V09 remain immutable; treat scenario steps as a **single correlated longitudinal chat run**, not three independent cold runs.
- **Stage 01 / baseline:** grade original A0x constraints, original editable source/export, real Godot capture and QA, and documented `EXECUTED` v1 Issue receipt/readback. The scenario alone authorizes a public test Issue; historical Workfiles-only C prompts still do not.
- **Stage 02 / changed requirement:** independently verify the *specified* change against v1 source/images and the owner's exact new message. Explicit replacements (color, shape, dimension, animation duration, mechanic) supersede only those fields of A0x. Require new source commit SHA, appropriate Godot/Blender QA, same issueNumber/baseRunId/assetId, `revision=2`, unique runId/requestId, one verified comment, old v1 unchanged and visible.
- **Stage 03 / second change:** verify cumulative requirements, preservation of the accepted v2 change and unaffected original criteria. Require third distinct source commit SHA, `revision=3`, one new comment after verified v2, no duplicate/new Issue, preserved v1 and v2, independent QA and owner browser inspection. An intentionally requested change is **not** a defect correction.
- **Motion and gameplay:** for SC03/SC04 validate actual changed timing/sweep/loop and source clips, not PNG storyboard alone. For SC05 verify actual sequential input, out-of-range and short-hold refusal, gate collision, exit and restart. PNG/Issue is a preview, not `GAMEPLAY_ACCEPTED`.
- **Evidence gates:** links + receipts + full source SHA of each revision, local PNG SHA256 and actual inspected full-size frames, stage timing and real owner messages. Public Markdown media readback does not establish remote byte equality; owner must open attachment. Label `V1_OWNER_FEEDBACK_PENDING` or `V2_NEXT_CHANGE_PENDING` when the next real user instruction has not arrived; never manufacture owner feedback.
- **Safety:** any revoked live policy, wrong original Issue, missing durable reservation, failed QA or `UNCERTAIN` write blocks progress and forbids blind retries/fallback new Issue. A technically successful comment does not compensate for a failed asset/game requirement. `ISSUE_REVIEWED`, `SOURCE_MERGED` and `GAMEPLAY_ACCEPTED` remain separate.
- **Verdict:** assess each stage PASS/PARTIAL/FAIL/BLOCKED independently; whole scenario PASS only if all three stage evidence gates pass and the owner actually confirms the v3 image. Record a separate first-preview and active-stage duration plus human wait; do not compare 3-message elapsed wall-time directly to single-message Cxx baselines.
Use the [scorecard template](scorecard-template.md) copied to evaluator-owned Workfiles, not written into repository. Do not provide these expectations or grades to the test-taking chat.

## Sequential defect-review scenarios SV01–SV03

Evaluate each **completed two-message scenario as ONE correlated chat-run**, never two cold runs. SV01 includes two 2D turnaround clips; SV02 includes two 3D jump clips and one 3D Walk clip; SV03 is an **optional** cross-dimension 2D→3D follow-up using case IDs overlapping the two primary scenarios. The optional run tests context switching, not additional unique fixtures.

Require that message 01 submitted its **own** independent per-case report(s) **before** message 02 appeared, and preserve those conclusions without post-hoc rewriting. For message 02 confirm it used its newly assigned brief/capture, actually opened original full-size frames, and formed a separate PASS/FAIL/UNCERTAIN rather than borrowing the previous result. No assumption that a group must contain a failing clip; do not leak hidden labels in prompts or evaluator feedback.

After the **final submission only**, apply the existing evaluator key per case for TP/TN/FP/FN, frame/time localization and invented defects. Group by chat as well as by case. SV03 repeats m4/r2, so duplicate evaluations do not increase fixture diversity or independent model sample counts. Preserve actual first-part T0–T5 and second-part S2.0–S2.5 with owner wait reported separately. Visual QA remains read-only and must not create GitHub Issues/PRs. The original V01–V09 results remain historical and must not be relabeled as SV runs.

## Evidence-first tool provenance for unit gates

Новый evaluator получает точный runId, находит `reports/units/<unitId>/submission.md`, проверяет настоящие исходники и QA и только потом читает самооценку. Все подготовленные пары [SC](../scenarios/README.md) и [SV](../review-scenarios/README.md) находятся рядом с исполнительскими промптами. Для внеплановых исправлений — [создание двух сообщений одновременно](unit-gates/author-unplanned-pair.md).

Для SC принятый результат **обязательно** создан и изменён инструментами Visual Workspace/Fortis Repo; image_gen/генератор AI-картинок для рабочего ассета, экспортного PNG или QA-свидетельств нарушает acceptance независимо от эстетики. Отмечать как существенную проблему CHANGES_REQUIRED даже при красивом PNG. Проверяй журнал инструментария, если доступен; отсутствие такого лога не доказывает, что image_gen не использовался. Для SV оригинальные fixture PNG неизменны, любые AI-generated подмены запрещены. Для исторических C/V/VR есть [tool-safe версии](../prompts-tool-safe/), оригиналы не меняются.

## Independent gates for each submitted work unit

The reusable [unit-gate protocol](unit-gates/README.md), [independent reviewer prompt](unit-gates/independent-review-prompt.md), [decision record](unit-gates/decision-template.md), and [intervention ledger](unit-gates/intervention-ledger-template.md) formalize an **evaluation after every completed scenario work unit in a distinct chat**. Preserve the runner's initial Workfiles and first-pass result. Unplanned repairs are additional units; actual same-Issue GitHub revision numbers can shift relative to filenames of planned v2/v3 prompts.

For SV blind tests, do not reveal the hidden answer key to the runner before the full scenario completes. Coached re-review counts as recovery, never as first-pass independent detection.
