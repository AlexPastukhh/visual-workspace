# UC-VIS-008 / Handoff 02 — clean-chat execution matrix (v1)

**Status at preparation: NOT RUN.** This document specifies prospective
independent runs; it is not an execution transcript and cannot establish
success or timings. Use accepted `visual-workspace/main` as bootstrap,
not the old Northlight task or this ongoing chat. Each row means a
different fresh chat and a different unique Workfiles run directory.

| ID / immutable prompt | Purpose | State | Recorded T0–T5 | Evidence |
| --- | --- | --- | --- | --- |
| [V08](prompts/V08-review-mixed-pair.md) | One 2D + 3D batch, separate visual verdicts | NOT RUN | Not measured | None |
| [C03](prompts/C03-create-2d-animation.md) | Editable 2D animation, Godot QA | NOT RUN | Not measured | None |
| [C04](prompts/C04-create-3d-animation.md) | Editable 3D animation, export/import/QA | NOT RUN | Not measured | None |
| [C05](prompts/C05-create-playable-game.md) | Game/control input + actual gameplay | NOT RUN | Not measured | None |
| [VR01 v1](prompts/VR01-versioned-review-v1.md) | Real owner feedback; v1→v2 same-Issue GitHub E2E | NOT RUN | Not measured | None |
| [C06](prompts/C06-create-multiple-orders.md) | Optional independent-order isolation | NOT RUN | Not measured | None |

Each chat writes exact prompt ID/version, UTC T0–T5 from
[Timing](TIMING.md), bootstrap main SHA/dirty state, model/config if known,
input IDs, observed frames, time-to-first-preview, QA output, real
GitHub links when applicable, final verdict and limitations into its own
`/workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<id>/`.
Owner/evaluator grades only after results are submitted and must not
give the chat the evaluator key or expected defects. V08 includes
correlated cases within ONE independent chat, not two independent samples.
Never claim clean-chat PASS before actual execution.

**Historical separate evidence:** Northlight #5 has successful live
owner-reviewed v1→v2 in an **existing** conversation, not VR01 v1 and
not a cold-chat timing measurement. See
[UC-VIS-009](../docs/use-cases/media-github-review.md#uc-vis-009).
