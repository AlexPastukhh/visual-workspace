# Per-unit submission route — Visual Workspace

The executor and evaluator are **different chats**. Each completed scenario stage supplies a small stable **locator file** rather than pre-guessing changing run IDs, source SHAs, or GitHub comment IDs.

## Executor contract (new SC and SV prompts)

1. One entire scenario chat has **one unique** runId and root directory: /workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/.
2. After each completed **unitId**, save /workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<runId>/reports/units/<unitId>/submission.md. Keep old units immutable. This is a **handoff**, not the executor's own independent score or a replacement for detailed QA.
3. In the handoff include these fields, using real values or explicit NOT_APPLICABLE / UNAVAILABLE:
   - scenarioId, unitId, runId, original requested prompt full path and exact Git HEAD/version when started.
   - runner chat identifier if available; output timestamp; original requirements and *actual* owner message for the unit.
   - task worktree absolute path, current full source Git SHA, previous source Git SHA (SC only), source/edit/export paths; SV states READ_ONLY.
   - original Issue URL + issueNumber + baseRunId + assetId, **actual** revision number and comment ID (if applicable), requestId and receipt path (SC only).
   - actual full-resolution PNG paths, runtime/animation/gameplay evidence paths, original per-case review files, exact report and timing paths.
   - executor verdict, known deficiencies and tool/runtime limits. Distinguish screen captures from generative images.
4. The runner uses **Visual Workspace via Fortis Repo**. For SC, edit real SVG/Blender/Godot source and export/render through project tooling. For SV, inspect original images. No image_gen or AI picture generation to create, modify, or substitute work products or QA evidence.
5. The final executor reply mentions the exact handoff path and runId. The owner can supply just this runId with the adjacent planned evaluator prompt in a **fresh evaluator chat**.
6. Evaluator first opens the exact original prompt and real raw source/images, then self-review and handoff claims; writes /workspace/repo/Workfiles/visual-workspace-practical-tests/evaluations/<runId>/<unitId>/decision.md. It does not change original evidence, source, GitHub or evaluation key.

## Новый Action human-first gate (отдельно от исторических SC/SV)

Для локальных `practical-tests/actions/VTxx/visual-testing.yaml` сначала
проверяется `variants[].human_review_required`:

- `true`: исполнитель сдаёт Workfiles evidence, **человек** смотрит визуальный
  результат и оставляет реальный отзыв `evaluations/<runId>/<unitId>/human-review.md`,
  **затем** отдельный чат VT15 получает эту запись и проверяет остальные
  критерии. До неё он **не начинает** ревью и не пишет `decision.md`.
  Чат фиксирует только `TECHNICAL_ONLY / NOT_FINAL`, а не полный PASS.
  Общий исход после обоих отзывов принадлежит owner/orchestrator.
- `false`: независимая чат-проверка без обязательного human gate. В
  новых Actions VT11/VT12 применяются [специальные evaluator-промпты и
  сравнение ответов с эталоном](actions/DEFECT-SCORING.md): **не** повторный
  визуальный поиск. Первый unit — process-only, сравнение с ключом — после
  завершения второго. Исторические SV evaluator-промпты не переписываются.

См. [единый порядок](actions/HUMAN-REVIEW.md). Старые SC/RS/SV prompts и
прежние outcomes не переписываются задним числом, и наличие human flag
само по себе **не** считается фактическим человеческим отзывом.

## Backwards compatibility and protection against guessing

For runs predating this contract (such as SC01.01 created under earlier prompts), the handoff may not exist. In that case the evaluator can inspect the **uniquely identified** existing run folder and reports, with the supplied runId and exact Git source SHA / issue identity. Never pick the newest run when multiple candidates match, never invent a source SHA or pretend an absent handoff exists. Missing proof is INCONCLUSIVE; a delayed handoff should not be backfilled as a fictional originally submitted artifact.

Accepted scenario prompt revisions are versioned by Git SHA. The original first-pass output, historical benchmark prompts, and original GitHub comments are immutable evidence. New tooling guard text is an explicitly new prompt revision, not a silent historical rewrite.

## Outside-plan repair

The *owner/orchestrator* creates two Workfiles messages at once under evaluations/<runId>/interventions/<repair-unitId>/:
- 01-to-runner.md — exact corrective instruction for **the same runner chat**; must demand Visual Workspace/Fortis Repo and ban image_gen.
- 02-to-evaluator.md — exact independent review request for a **new evaluator chat**, including a known unitId and the above expected handoff path.
An additional manifest/ledger records the planned stage being held, raw evidence, criteria and actual revision mapping. The post-repair runner writes reports/units/<repair-unitId>/submission.md in the **original** run folder.

See the dedicated pair-authoring instructions in _evaluator/unit-gates/author-unplanned-pair.md. Never let the runner read evaluator-only source/answer key, and never treat a coached SV reanalysis as a first-pass blind success.

## Scope of enforcement

These prompt guards are an **instructional test constraint**, not an operating-system-level tool-permission boundary. For stronger prevention, launch test-taking chats in a tool profile that exposes Fortis Repo but does not offer AI image-generation tools if that profile is available. In any profile, audit actual source artifacts and tool trace (when accessible). If image_gen/AI generated imagery was substituted, treat the unit as a substantive noncompliance and require source-level rework; if a tool-call trace is unavailable, record UNKNOWN rather than asserting the model never invoked it.
