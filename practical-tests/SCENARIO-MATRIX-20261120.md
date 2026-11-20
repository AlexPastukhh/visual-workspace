# UC-VIS-008 + UC-VIS-009 — scenario execution matrix v1 (2026-11-20)
**All new independent SC01–SC05 runs: NOT RUN.** Preparing prompts and activating Gateway methods is not evidence that a new chat completed the sequence. The original V01–V09 / C01–C06 / VR01 prompts and results remain separately attributed.
| ID | Initial message | Owner change 1 | Owner change 2 | Current state | Evidence / T0–T5 |
| --- | --- | --- | --- | --- | --- |
| SC01 | [create v1](scenarios/SC01/01-create-v1.md) | [v2](scenarios/SC01/02-change-v2.md) | [v3](scenarios/SC01/03-change-v3.md) | NOT RUN | None |
| SC02 | [create v1](scenarios/SC02/01-create-v1.md) | [v2](scenarios/SC02/02-change-v2.md) | [v3](scenarios/SC02/03-change-v3.md) | NOT RUN | None |
| SC03 | [create v1](scenarios/SC03/01-create-v1.md) | [v2](scenarios/SC03/02-change-v2.md) | [v3](scenarios/SC03/03-change-v3.md) | NOT RUN | None |
| SC04 | [create v1](scenarios/SC04/01-create-v1.md) | [v2](scenarios/SC04/02-change-v2.md) | [v3](scenarios/SC04/03-change-v3.md) | NOT RUN | None |
| SC05 | [create v1](scenarios/SC05/01-create-v1.md) | [v2](scenarios/SC05/02-change-v2.md) | [v3](scenarios/SC05/03-change-v3.md) | NOT RUN | None |
## Execution gates
- One SCxx = **one new chat with three sequential user messages**. Subsequent stages must be sent only after owner inspection and independently verifiable prior output; never all at once.
- Every new SCxx run gets unique `/workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<run-id>/` and distinct registered source task; each owner-shown source version must be committed at a different full Git SHA.
- For each version: source/export, actual inspected full-resolution runtime frames, brief/updated requirements, QA, local PNG SHA, source SHA, exact runId/requestId, receipt, Issue link; v2/v3 additionally comment ID and same-Issue readback. After v3, owner browser decision.
- Grade stage 01 production quality against A0x; stage 02/03 against **original still-active requirements plus changed owner's clause**. Do not treat correct requested changes as defects; do not silently preserve superseded numerical specs.
- Distinguish `V1_OWNER_FEEDBACK_PENDING`, `V2_NEXT_CHANGE_PENDING`, blocked publication, owner acceptance, source merge and gameplay. One Issue is not enough evidence for all three stages.
- Record observed UTC T0–T5 for v1 and S2.0–S2.5/S3.0–S3.5 for later owner messages; total elapsed/wait separately. User UI latency outside clock marks is not measured.
## Priority
Run **SC01 first** to establish 2D static change/history, independently evaluate it, then SC02 3D, SC03 2D animation, SC04 3D animation, SC05 game. Gate later public publications on actual lessons from previous scenario; failures do not authorize automatic retries or bypasses.
**VR01 remains a distinct historical single-review integration baseline**; the new scenarios test production plus multiple separate real owner requests. V01–V09 remain visual QA without mandatory GitHub side effects. C01–C06 remain Workfiles-only historical creation baselines.
