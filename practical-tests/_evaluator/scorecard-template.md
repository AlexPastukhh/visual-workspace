# Evaluation scorecard template — COPY INTO WORKFILES, DO NOT FILL IN REPO

This file is for the **owner/evaluator after submission**, not the tested
chat. Preserve one scorecard per run in
`/workspace/repo/Workfiles/visual-workspace-practical-tests/evaluations/`
or an evaluator-owned Workfiles folder. Never modify fixture keys/scores
based on the model's unsupported claims.

## Identity / comparability

| Field | Value |
| --- | --- |
| Run ID / report path | |
| Prompt ID and repo revision (HEAD) | |
| Test mode: cold / batch / production / confirmation | |
| Case IDs or authoring brief ID | |
| Workspace Git HEAD / uncommitted status | |
| Chat model/config (if known) | |
| Reference evidence completeness: frames actually opened | |
| Test date and reviewer | |

## Clocked timing (UTC, from raw tool-returned timestamps)

| Phase | Start | End | Seconds | Notes |
| --- | --- | --- | --- | --- |
| Bootstrap | T0 | T1 | | |
| Brief / preparation | T1 | T2 | | |
| Work until review/tests done | T2 | T4 | | |
| Finalization | T4 | T5 | | |
| **Whole observed run** | **T0** | **T5** | | |
| First full-res image / Godot preview | T0 | T3 | | |

Include per-case time intervals in a batch and make sure `T5−T0`
matches tool timestamps. If T0 is missing, label total time unavailable
rather than inferring from a path or self-reported estimate. Owner-observed
chat send-to-final latency, if available, is a **separate** field.

## QA outcomes

For each visual case: `case ID | label from key | predicted PASS/FAIL/
UNCERTAIN | TP/TN/FP/FN | precise location | image evidence actually seen |
material invented defects | verdict score`. Aggregate by **chat** as
well as by case; do not treat multiple cases inside one chat as independent
model replicates. Prefer including one good control and one bad case.

For creation: `brief criterion | required deliverable / screenshot /
test evidence | observed result | pass/partial/fail | severity`.
Use the written brief, real editable files, exported resources and
game-size Godot images. For gameplay, include actual input/collisions/
transitions. Technical import PASS alone does not certify visual quality.

## Cost / bottleneck / interpretation

Record separately: first useful full-res image or working preview,
full QA result, total observed wall-clock, significant Godot/Blender
tool durations, cache versus cold start, failures/retries, and time lost
to irrelevant document reading. Name concrete improvement opportunities;
do not speculate about CPU utilization from elapsed wall time.

Decision: PASS / PARTIAL / FAIL / INCONCLUSIVE relative to this specific
task; separate correctness from speed. For comparing two revisions,
keep prompt/input/expected evidence fixed, describe changes and run
the same task in independent chats where possible. One success is a
smoke test, not proof of a general reliability percentage.

## Multi-message SCxx extension (fill after each submitted message)
| Field | v1 initial | v2 owner change | v3 owner change |
| --- | --- | --- | --- |
| Real owner message / requirement deltas | | | |
| Source paths and full Git SHA | | | |
| Original requirements still applicable | | | |
| Edited source comparison actually checked | | | |
| Godot/Blender QA and inspected full-size PNGs | | | |
| Real animation/controller/runtime tests if required | | | |
| Local media SHA256, PNG count and byte sizes | | | |
| issueNumber / baseRunId / assetId | | | |
| revision / runId / requestId | | | |
| EXECUTED receipt and commentId (v2+) | | | |
| GitHub Issue + comment / unchanged earlier versions | | | |
| Owner browser inspection and explicit status | | | |
| Timing T0–T5 or S2/S3 stage clock marks | | | |
| Stage verdict / blocker / uncertainty | | | |
Verify exactly **one** original Issue, no extra Issue for v2/v3, and **one comment each** for v2 and v3; three **different source Git SHAs**. Compare requested change and unchanged requirements per version, not only new PNG links. Owner messages arrive sequentially in the **same chat**; all stages are correlated.
Final whole-scenario status: PASS / PARTIAL / FAIL / BLOCKED / NOT RUN. Record owner-wait intervals separately from active stage durations. Score `ISSUE_REVIEWED`, `SOURCE_MERGED`, `GAMEPLAY_ACCEPTED` separately. A missing third user message must not be graded as a failed v3 change.

## SVxx — sequential read-only review extension (complete after both messages)

| Field | Message 01 | Message 02 |
| --- | --- | --- |
| Scenario ID, exact prompt file, accepted main HEAD / dirty | | |
| Input clips and per-case written brief/capture | | |
| Actual original full-size PNG frame IDs opened for each case | | |
| Separate per-case PASS/FAIL/UNCERTAIN and frame/time evidence | | |
| Per-case TP/TN/FP/FN, localization, false positives (evaluator only) | | |
| UTC T0–T5 or S2.0–S2.5, first full-resolution preview and clip intervals | | |
| Files submitted and verified before the next user message | | |
| Independent verdict, limitations, stage status | | |

One SVxx = one chat and one Workfiles run folder, **not** one independent model observation per clip. Report T5→S2.0 user-wait interval separately. SV03 repeats existing clips and is optional. Full scenario verdict only after both messages, and evaluator-only scoring only after final submission.

## Unit-gate decision and interventions

For a scenario graded **after each work unit by another chat**, use the more detailed [unit decision template](unit-gates/decision-template.md) and [intervention ledger](unit-gates/intervention-ledger-template.md). The scorecard for the whole scenario cannot overwrite a first-pass FAIL with a successful repair. Track actual GitHub revision number separately from immutable planned file names v2/v3; never report the independent evaluator as the original runner.

## Provenance of generated images (current guarded kit)

Check that SC production used actual Visual Workspace/Fortis Repo editable SVG/Blender/Godot sources and exported/runtime PNGs. A ChatGPT image_gen or other AI image-generation substitution violates the production test regardless of image attractiveness. Examine actual tool-call evidence where available; otherwise record provenance as UNKNOWN, not proven absent. Planned work and evaluator messages are paired next to each other in [SC](../scenarios/README.md) and [SV](../review-scenarios/README.md) indexes. Unplanned steps use [paired message authoring](unit-gates/author-unplanned-pair.md).
