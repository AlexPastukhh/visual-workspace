# <repair-unitId> — independent evaluation message for a NEW evaluator chat

Evaluate one actual completed additional repair/review unit, not an entire scenario. Use Fortis Repo read-only. No image_gen, AI picture-generation, synthetic replacement images or source modifications of any kind.

scenarioId: <scenarioId>
unitId: <repair-unitId>
runId: <existing runId>
original failed unit: <prior unit ID>
original evaluator decision path: <decision path>
exact corrective runner message: <owner-owned Workfiles interventions path>/01-to-runner.md
expected submission path: /workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/reports/units/<repair-unitId>/submission.md
output decision path: /workspace/repo/Workfiles/visual-workspace-practical-tests/evaluations/<runId>/<repair-unitId>/decision.md

Read /workspace/repo/README.md, accepted Visual Workspace README, the original unchanged scenario brief, actual change request and unit-gates/README.md. Start by inspecting raw original+repaired editable source, full-size actual screenshots/runtime, QA and relevant Gateway receipts and Issue comments. Record independent observations *before* reading the repair runner's self-review, previous evaluator or any preliminary audit. Never trust a filename as the actual GitHub revision.

Check that the requested defect is corrected without regressions or changed unrelated requirements, compare with original first-pass evidence and source SHA. For SC ensure no image-generation substitute, current source SHA and the next sequential comment in the **same original Issue** if owner-visible output was republished. For SV preserve read-only original fixtures; if the correction was guided by evaluator feedback, label the later result ASSISTED/COACHED and never replace original blind result.

Return APPROVED / APPROVED_WITH_NOTES / CHANGES_REQUIRED / BLOCKED / INCONCLUSIVE, severity and exact evidence. Store a distinct decision; preserve earlier failed grade and actual additional repair duration. Never modify runner files, original Issue, repository fixtures or past report. Owner alone authorizes resuming the planned next unit.
