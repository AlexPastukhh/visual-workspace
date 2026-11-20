# Independent unit gates and unplanned interventions

**Purpose:** a separate chat evaluates each completed work unit *before* the owner advances a multi-message scenario. This extends existing UC-VIS-008, UC-VIS-009, SC01–SC05, and SV01–SV03. It does not change accepted scenario prompts, historical fixtures, their answers, or Gateway APIs.

## Separation of responsibilities

- **Runner chat:** executes SCxx/SVxx parts, edits source only when authorized, captures raw QA/receipts, and writes under its own unique `Workfiles/visual-workspace-practical-tests/runs/<run-id>/`. The runner never reads `_evaluator/`, independently written assessments or any hidden key.
- **Owner/orchestrator:** opens the relevant result, gives a real instruction for each next step, and transfers the exact run ID and completed unit ID to an **entirely different evaluator chat**. The owner—not evaluator automation—sends any corrective message to the **original runner chat**.
- **Independent evaluator chat:** checks the brief, exact source commit, frames, import/playback/gameplay evidence, GitHub receipt and original Issue where applicable. It writes only to `Workfiles/visual-workspace-practical-tests/evaluations/<run-id>/<unit-id>/`. It must **never** modify runner files, hidden fixtures, source, or GitHub. It must inspect raw assets/evidence *before* reading the runner's summary or another evaluator's preliminary audit to reduce anchoring.
- **Owner acceptance:** visual taste, browser viewing and a merge decision remain separate. An evaluator's technical PASS does not impersonate the owner.

## Units and decisions

A **unit** is a completed output that can be evaluated independently: SC01.01 (original crystal v1), SC01.02 (planned color change), SV02.01 (two jump reviews), or an unexpected SC01.01-R1 (repair after first review). The unit ID is **not** a GitHub revision number.

Choose one decision per unit: `APPROVED`, `APPROVED_WITH_NOTES` (non-blocking), `CHANGES_REQUIRED` (evidence-backed material defect), `BLOCKED` (missing capability/source or uncertain effect), or `INCONCLUSIVE` (insufficient evidence; request more QA/proof without assuming a fault). Include **severity** `BLOCKER/MAJOR/MINOR/NONE` for each finding, exact evidence, and the smallest concrete corrective requirement. Preserve a distinct **first-attempt verdict** even if repair later succeeds.

1. Owner receives the runner's stage output and freezes its evidence: unit ID, submitted prompt, worktree HEAD/SHA, Workfiles run folder, issueNumber/comment IDs if applicable, and real T0–T5 or S-mark timestamps.
2. Owner starts a **new evaluator chat** using [independent-review-prompt.md](independent-review-prompt.md) with explicit unit identity and paths. The evaluator reads original scenario requirements and raw images/source, independently checks them, then compares the runner's claims.
3. Evaluator writes [decision-template.md](decision-template.md), records objective and aesthetic concerns separately, returns its verdict and path. No automatic grade from the runner's own report. Owner may inspect the same images in a browser.
4. `APPROVED` or owner-approved `APPROVED_WITH_NOTES` unlocks the **next planned user message**. `CHANGES_REQUIRED` stops planned progression and creates an **extra repair step**, sent by the owner to the original runner chat; `INCONCLUSIVE` calls for a bounded evidence-only follow-up; `BLOCKED` requires resolving the blocker without speculative writes.
5. After repair/evidence, freeze the new unit's output and ask another evaluator chat or a fresh independent pass to recheck it. Only then continue the original planned sequence. A scenario finishes when all required planned units pass their gates and the true owner acceptance conditions are met.

## Inserting an unexpected repair without rewriting a test

Maintain [intervention-ledger-template.md](intervention-ledger-template.md) in an evaluator-owned Workfiles folder. A repair request **is not** the already planned creative design change and must be tracked separately. Example: `SC01.01` publishes v1, evaluator finds a serious shape defect, owner issues `SC01.01-R1` in the **same runner chat**, the runner repairs source and publishes v2 in the **same Issue**. Only after re-evaluation does the owner send the immutable file `SC01/02-change-v2.md`: that planned stage might now publish **v3**, and the last planned stage might publish **v4**. Record the actual revision mapping. The filename `02-change-v2.md` names a **historical planned stage**, not an unconditional requirement that revision=2 when repairs intervene.

**Strict publication boundary:** if a review PNG was already published, every owner-visible changed result is a new same-Issue `append_visual_revision` comment with the next sequential revision, new runId/requestId/source SHA, and preserved earlier history. If the flaw is noticed and fixed *before the first owner publication*, it is an **internal attempt**, not a GitHub revision or fabricated owner feedback. Never issue a new Issue to avoid correcting the original, and never retry an `UNCERTAIN` append blindly.

**Do not retroactively edit fixed prompts or outcomes.** Preserve original unit output and first-attempt FAIL. Evaluate recovery separately (number of interventions, active rework time, owner wait, incremental cost, regressions). Report both first-pass quality and eventual accepted quality. Source/Issue SHAs and times must be observational, not invented.

## Two kinds of scenarios require different feedback

- **SC01–SC05 creation/change:** evaluator may disclose concrete rubric-backed defects to the owner, who sends a narrow repair message to the runner. Subjective owner preferences are *planned or new design changes*, not mandatory defect fixes unless they contradict the brief.
- **SV01–SV03 blind defect-finding:** evaluate a completed part without revealing the hidden answer key to the runner. If evidence is incomplete, the owner can request a *neutral* redo (e.g. 'inspect the complete original frame range'), explicitly recorded as an assisted intervention. Giving the runner a correct label or exact seeded defect makes the later result **coached/non-blind**; never count it as independent first-pass performance. The fixtures remain immutable; a repair here means improving **analysis/reporting**, not changing images.

## Metrics and directory convention

Runner: `.../runs/<run-id>/` untouched. Evaluator: `.../evaluations/<run-id>/<unit-id>/decision.md`, plus `.../evaluations/<run-id>/interventions.md` if needed. A preliminary audit by the orchestrator may be stored separately but must be marked **NOT independent** and withheld until the new evaluator has recorded its own findings.

Record per unit: first-attempt verdict, severity and evidence, actual changed source Git SHA and published revision (if any), independent gate outcome, owner browser decision, count of unexpected repairs, time to first useful preview, measured active duration for each unit, and actual elapsed owner wait. Keep `ISSUE_REVIEWED`, `SOURCE_MERGED`, and `GAMEPLAY_ACCEPTED` distinct. One chat with several units is still **one correlated model run**, not multiple independent trials.

**Do not turn a poor result into a PASS by concealing an intervention.** A repaired scenario may have an eventual-success PASS and a first-pass FAIL simultaneously, with explicit repair overhead.
