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
