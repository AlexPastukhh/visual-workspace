# Timing protocol — reproducible wall-clock measurement

Use this protocol for **every new practical test**, both read-only visual QA
and production (2D, 3D, animation, game integration). It measures elapsed
**wall-clock time of an actual chat run**, not CPU/Godot runtime alone.

## How to measure without a test launcher

A fresh chat has no reliable built-in timer spanning reasoning and tool calls.
At the milestones below, read **the container's UTC clock** using Fortis Repo,
for example a short shell command:

```sh
date -u +"%Y-%m-%dT%H:%M:%S.%NZ"
```

Copy the *returned timestamps* (never estimates or invented timings) to
`timing.md` in the run's own Workfiles folder. Do this **before opening**
the workspace README for T0 and immediately after the relevant milestone.
There is no need to run a project-local benchmark script or prepare folders
before the prompt. If the clock is unavailable, record `unavailable` and
explain; do not substitute confident-looking estimates.

| Mark | Visual review (existing images) | Authoring (new 2D/3D/game) |
| --- | --- | --- |
| **T0** | First accessible clock read, before README/bootstrap. | Same. |
| **T1** | Workspace bootstrap and necessary workflow/QA reading complete. | Same. |
| **T2** | All assigned briefs/metadata reviewed, review plan ready. | Requested written brief and initial implementation plan ready. |
| **T3** | First *actual* full-resolution PNG visually inspected (not its path/JSON alone). | First real Godot/runtime game-size preview visually inspected (not a source-file mockup). |
| **T4** | All assigned case images inspected and per-case verdicts formulated. | Required production, in-game checks, final visual review and targeted tests completed. |
| **T5** | Final reports and timing record saved and verified, immediately before final reply. | Same. |

**Total measured:** T5 − T0, including bootstrap, tool wait, viewing, reasoning,
development, rendering, validation and documentation. Do not measure only
script runtime, cached capture or time spent opening PNGs and call it total.

**Phase breakdown:** bootstrap T1−T0; brief/plan T2−T1; first useful
visual feedback T3−T0; substantive work T4−T2; final reporting T5−T4.
These phases overlap in the intended sense of a cumulative milestone:
do not sum the cumulative T3−T0 with phase durations.

For a **multi-case review**, also record the time when visual inspection of
each case starts and when its assessment is complete; these per-case intervals
may not add up to the total because shared preparation, tool calls and report
writing are outside them. Name the case, count of original PNGs actually
opened, and any reason for missing evidence. Prefer scanning all original
frames for tests of rare one-frame glitches; a sparse contact sheet does not
establish smoothness.

For authoring, optionally record first export, first import and final
gameplay test as additional marks. The first preview **must be real Godot
output**; don't replace it with a generated illustration. Repeated/cached
preview times, if checked, are supplementary and separately labeled.

## Minimum timing.md in Workfiles

Write a small table with `T0..T5`, exact UTC timestamps, observed event,
calculated durations in seconds, **total T5−T0**, and a short note on
whether time was measured using tool-returned timestamps. For multi-case
reviews list per-case start/end and input frame coverage. Also include
prompt ID, assigned case/order IDs, workspace HEAD and dirty status as
observable, and evidence paths. Avoid extensive telemetry or custom runners
that themselves dominate the task.

## Optional diagnostic for report-heavy runs (V09)

T4→T5 may mix **reasoning/composing**, **file write/tool latency** and
**verification**. Do **not** diagnose its bottleneck merely from the total
or assume every second was spent typing text. V09 adds two **observed**
UTC marks without changing T0–T5:

- **R1:** all case reports, short summary and timing content are drafted
  but no final report file write has begun. T4→R1 is composition.
- **R2:** the initial four report files have been saved. R1→R2 includes
  storage/tool wait and any corrections before first completed write.
- **T5:** the saved files have been checked. R2→T5 is readback and any
  corrections, including tool waits.

Record exact UTC timestamps, compute T4→R1, R1→R2, R2→T5,
and check their sum against T4→T5. Use minimal necessary calls:
save each compact report once, favor one grouped readback, and preserve
frame-by-frame evidence, written-brief compliance and independent verdicts.
Do **not** repeatedly regenerate the same detailed narrative.
If the final T5 value is appended after T5, explicitly disclose this
small unmeasured tail as in the general protocol. These extra marks
are optional for production and other visual prompts.

## Interpretation / limitations

- The interval before the first clock call and the period after T5,
  including UI delivery, are **not** in T5−T0. For exact user-perceived
  end-to-end latency, the owner must also use external chat send/finish
  timestamps where available.
- Human waiting/approvals, network stalls and reused warm caches affect
  wall-clock time; disclose material conditions. Use consistent tools,
  model/configuration, and inputs before comparing runs.
- Do not trade away required temporal frame coverage, brief compliance or
  source/preview quality for a shorter measured runtime.
- A correct artistic PASS and a good runtime are **separate outcomes**;
  summarize the bottleneck (bootstrap, images, rendering, tool calls,
  retries, QA, game tests) only when supported by observed timings.
- Legacy V03/V04 runs completed before this protocol have quality
  results, but **no comparable total timing**. Never retroactively infer
  their duration from prose or timestamps embedded in a path.

## Extension: mandatory Issue delivery for selected baseline Actions

Для **VT01.crystal, VT02, VT03, VT04** в принятой версии промптов
GitHub Issue с owner PNG-превью является обязательным последним
этапом **того же теста**, а не отдельным тестом. В отличие от ранней
Workfiles-only версии, **T5 ставится после публикации, typed Gateway
readback, duplicate check и сохранения финального отчёта**; следовательно
T5−T0 включает полный путь до готовности к human review. T4 по-прежнему
означает окончание производства/QA; для анализа времени обязательно
добавить реальные UTC **P0** (начало подготовки к публикации сразу
после T4) и **P1** (подтверждённый Issue + readback/duplicate check),
P1−P0 фиксировать отдельно. Не считать только время Gateway WRITE временем
всей публикации. `duration_seconds` для предварительного Issue payload
целочисленное и должно отражать уже измеренный этап (например T4−T0),
**не будущий T5**. Финальное T5 и полная длительность — в Workfiles handoff.

Для **VT11/VT12** T5 закрывает первый frozen unit без Issue, затем второй
этап в том же runner chat имеет S2.0–S2.5. Публиковать Issue c замороженными
выводами обоих unit **после** результатов второго этапа, до S2.5; P0/P1
внутри этого этапа. Не раскрывать ключ и не пропускать независимый
process-only gate между частями. Считать отдельно T5−T0, S2.5−S2.0,
P1−P0 и паузу между сообщениями. См.
[OWNER-ISSUE-DELIVERY](actions/OWNER-ISSUE-DELIVERY.md).

Ранние прогоны без Issue не являются сравнимыми по T5−T0 с новой
версией; их значения не переписывать задним числом.

## Extension: multi-message versioned scenarios SC01–SC05
The original T0–T5 definition is **unchanged** for the *first* message of a scenario. Record T0 before README, T1 after bootstrap, T2 after brief/plan, T3 after first real inspected Godot full-size frame, T4 after v1 creation/QA, T5 after the v1 report is saved and checked. T5 closes **only stage 01**, not the full owner-review conversation.
For later **messages in the same chat**, record observed UTC marks in the same `timing.md` (never invent timestamps):
| Mark | Meaning for stage N = 2 or 3 |
| --- | --- |
| `S{N}.0` | First available container clock after receiving the owner's new message, before source changes |
| `S{N}.1` | New requirement reconciled against prior brief/version and update plan ready |
| `S{N}.2` | First actual full-size image of the changed source viewed in Godot |
| `S{N}.3` | Source revision and required runtime/visual QA completed |
| `S{N}.4` | GitHub revision receipt and same-Issue READ verified; mark unavailable if blocked |
| `S{N}.5` | Per-stage report and timing saved and checked, before replying to owner |
Report `S2.5−S2.0` and `S3.5−S3.0` separately; also report time to changed preview (`S{N}.2−S{N}.0`), time until publication and write/readback waits. Do not add stage durations to get end-to-end elapsed time when there are human feedback delays: additionally record the actual wall elapsed `S3.5−T0` and each observed interval between prior stage completion and next user message **as owner wait / chat interruption**, not active agent work. If no owner message arrives, follow-up timestamps are unavailable, not zero.
Record exact source SHA, GitHub requestId and actual Issue/comment evidence alongside each stage; do not substitute a fast cached render for end-to-end timing. For playable SC05, keep real controller/input test duration separate from screenshot/GitHub timings. A scenario is not completed by a v1 or v2 T5 alone.

## Extension: sequential read-only visual QA scenarios SV01–SV03

For message 01, retain the existing visual-review UTC T0–T5 definitions. T5 ends **the first part only**. For message 02 in the **same chat** (different clips, same single Workfiles run), record real UTC milestones without restarting the original T0/T1 bootstrap:

| Mark | Event |
| --- | --- |
| S2.0 | First accessible container UTC clock after receiving the next owner message |
| S2.1 | Newly assigned brief/capture read and inspection plan ready |
| S2.2 | First real full-resolution PNG of the second part visually inspected |
| S2.3 | All second-part clips inspected; individual verdicts frozen |
| S2.4 | Individual reports, combined summary and timing draft saved |
| S2.5 | All second-part reports and timing verified immediately before final reply |

Report **T5−T0** for the first part, **S2.5−S2.0** active second-part wall-clock, S2.2−S2.0 first-preview time, each clip's own actual open/complete timestamps, and S2.5−T0 total *elapsed including owner wait*. Do not equate elapsed inter-message delay with active model work; label the T5→S2.0 interval owner wait/chat interruption. If user never sends message 02, second-part timestamps are **not measured**, not zero. One scenario has one run-id and Workfiles folder but multiple per-clip review files.

## Unplanned repairs and independent evaluator clock

After each owner-requested extra repair R1/R2 in the same running chat, record true UTC `R1.0` (message received), `R1.1` (plan), `R1.2` (first inspected correction), `R1.3` (source and QA ready), `R1.4` (same-Issue revision receipt/readback where applicable), and `R1.5` (evidence saved and verified). Use a separate prefix per repair; actual stage IDs are **not** GitHub revision numbers. Report added active rework time and human/evaluator waiting separately from the first-attempt time. The different evaluator chat measures its own effort in evaluator-owned Workfiles, **outside** the runner's T0–T5/S/R marks. Do not invent zero for missing observations. [Unit-gate protocol](_evaluator/unit-gates/README.md).
