# Scenario interventions — <run-id>

Preserve this in `Workfiles/visual-workspace-practical-tests/evaluations/<run-id>/interventions.md` and add one row **after** each real unplanned owner/evaluator-directed action. Do not alter original scenario prompt files.

| Sequence | Planned unit held | Intervention unit ID | Reason and original evidence | Owner message exact text/ref | Old/new source SHA | Actual old/new GitHub revision + comment ID | Result and new evaluator gate | Active seconds; owner wait seconds |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| | | | | | | | | |

Types: `SOURCE_REPAIR`, `QA_EVIDENCE_ONLY`, `PUBLICATION_RECONCILIATION`, `REVIEW_REDO`, `OWNER_DESIGN_CHANGE` (not a defect fix). For SV blind reviews, add `COACHED` if the runner learned a keyed label/defect before the re-review.

Example revision mapping when a published v1 needs rework:

| Logical unit | User message | GitHub artifact |
| --- | --- | --- |
| SC01.01 | Initial accepted prompt | Issue body v1 |
| SC01.01-R1 | Unplanned factual correction after independent gate | Same-Issue comment revision v2 |
| SC01.02 | Original planned color change (file name may mention v2) | Same-Issue comment revision v3 |
| SC01.03 | Original planned shape change | Same-Issue comment revision v4 |

Do not change the actual order of published revisions, invent owner feedback, or replace existing Issue media. Preserve the initial FAIL and the later recovery outcome separately.

Every unplanned stage must have the **paired** runner/reviewer messages under evaluations/<runId>/interventions/<repairUnitId>/ (01-to-runner.md and 02-to-evaluator.md). Both explicitly demand Visual Workspace/Fortis Repo and prohibit image_gen and synthetic substitute imagery. The reviewer uses reports/units/<repairUnitId>/submission.md, or explicitly verified historical evidence, and records a separate decision. See [author-unplanned-pair.md](author-unplanned-pair.md).
