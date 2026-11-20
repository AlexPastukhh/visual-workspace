# Independent evaluator — one unit only (send to a NEW chat with Fortis Repo)

Evaluate **exactly one already-submitted work unit** from an existing Visual Workspace scenario. You are an independent evaluator, not the original creator/tested agent. The owner provides these exact values with this message (do not guess):

- `scenarioId`: <SC01/SV02/etc>
- `unitId`: <SC01.01/etc>
- `runId`: <exact Workfiles run identifier>
- `runner source task/full Git SHA`: <if authoring; may be N/A for SV>
- `GitHub Issue number/comment`: <if published; may be N/A for SV>
- `submitted unit prompt path`: <exact accepted prompt>

Сначала найди подтверждённый маршрут результатов `/workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/reports/units/<unitId>/submission.md` по [контракту](../../UNIT-SUBMISSION-CONTRACT.md) (если run старый и файла нет, проверь реально существующие пути, не выдумывай handoff). Используй только реальные исходники/PNG/QA через Fortis Repo. **Не вызывай image_gen и не генерируй синтетические иллюстрации для оценки.** Подмена рабочего результата генерацией изображений ИИ — критическая проблема производственного теста; если журнал вызовов исполнителя недоступен, явно отмечай проверку инструментария UNKNOWN, а не утверждай отсутствие image_gen.

Read `/workspace/repo/README.md` and accepted `visual-workspace` documentation, applicable use cases, original brief and `practical-tests/_evaluator/unit-gates/README.md`. Verify source and Workfiles paths independently. Do not write to the runner's folders, original source, repo or GitHub. Use only evaluator-owned Workfiles output.

**To reduce anchoring**, inspect the actual unmodified source/export, full-resolution Godot/Blender/runtime screenshots, controller/animation QA (where required), and exact GitHub Issue/receipts **before** reading the runner's self-review or any pre-existing audit. Record observations first. Then check claims, source provenance and all required evidence against the original written brief plus real later owner messages. If the evidence is unavailable, say INCONCLUSIVE rather than substituting a description.

Grade **this unit only**, not the entire planned scenario. Report separately: functional/visual conformity, editable source and QA, real image inspection, publication/revision integrity, timing/report accuracy, owner acceptance, and any issues not yet checked. Give each finding concrete evidence, severity and whether it requires correction. For SV blind fixtures, only consult evaluator-only answer key **after** the tested chat has submitted this unit's verdict; never reveal keyed results back to runner, and flag any coached later redo.

Create `Workfiles/visual-workspace-practical-tests/evaluations/<runId>/<unitId>/decision.md` using `decision-template.md`. Return `APPROVED / APPROVED_WITH_NOTES / CHANGES_REQUIRED / BLOCKED / INCONCLUSIVE`, with confidence, report path, whether the next planned stage may proceed, and the precise owner-mediated repair/evidence instruction if not. Do not publish GitHub or fabricate owner browser acceptance.

Do not read another evaluator's previous findings until after your own conclusion is recorded. Time your own evaluation separately if needed; do not add it to the runner's T0–T5.
