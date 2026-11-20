# Make an unplanned repair + independent-review message pair (owner/orchestrator chat)

This is **prompt authoring**, not source fixing. Use only when an owner or a per-unit independent decision identifies a concrete issue that needs a new step within a running scenario. Do not generate images or use image_gen as a substitute for Visual Workspace, do not write to runner source, fixtures or GitHub.

Inputs: scenarioId, existing runId, completed prior unitId, exact evaluator decision path/evidence, original frozen prompt file, identified defect/requirement and whether it is a SC producer or SV read-only review. If a required ID is missing, inspect the existing uniquely identified Workfiles run and ask for the missing identifier only if ambiguous; never invent it.

Before authoring, read /workspace/repo/Repos/visual-workspace/practical-tests/UNIT-SUBMISSION-CONTRACT.md and this folder's README, template files and existing interventions ledger. Check actual history and avoid duplicate repair IDs.

**Create BOTH messages atomically** in the evaluator/owner-owned Workfiles area, not in an accepted repo and not in the runner's own output:
  /workspace/repo/Workfiles/visual-workspace-practical-tests/evaluations/<runId>/interventions/<unitId-R1>/
    01-to-runner.md
    02-to-evaluator.md
    manifest.md

Use unit ID SCxx.yy-R1 / R2 (or SVxx.yy-R1 / R2). Write 01-to-runner.md following repair-runner-template.md: preserve the original planned prompt, the same original chat, same source task, and existing Issue (SC), state exactly what failed, distinguish evidence collection from production rework, demand Visual Workspace/Fortis Repo and prohibit AI image-generation. For SV, do not reveal the answer key/seeded defect labels: give only neutral QA/review coverage instructions and mark the assisted retry.

Write 02-to-evaluator.md **in the same authoring operation** following repair-evaluator-template.md: separate NEW evaluator chat, exact runId/unitId, before/after source/frames, original and repaired acceptance criteria, actual vs expected GitHub revision proof, expected new submission path (/runs/<runId>/reports/units/<repair-unitId>/submission.md), outcome path (/evaluations/<runId>/<repair-unitId>/decision.md), strict image_gen ban.

Write manifest.md with paths, source decision and prompts, who should receive which file, original planned stage paused, assumed evidence versus observed facts and timestamp. If the actual future source SHA or comment ID does not yet exist, leave it as **to verify after execution**. Only after review decision can the owner send the planned next stage. Append the real event to evaluations/<runId>/interventions.md when it happens; do not invent a successful intervention.

Return **links/paths to both messages side by side**, plus the proposed step order. Do not send them automatically, do not change runner chat history, do not revise frozen benchmark prompts or the evaluation key. The owner personally sends the first message to the original runner chat and the second to a separate evaluator chat after the runner reports completion.
