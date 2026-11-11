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
