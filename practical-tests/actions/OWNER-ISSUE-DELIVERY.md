# Owner-facing GitHub Issue delivery for the baseline Visual Actions

**Scope:** VT01 (`crystal-text-l1`), VT02, VT03, VT04, VT11, VT12. This is a
versioned amendment to those Action *work prompts*. It does not change the
historical SC/SV prompts, reference fixtures, evaluator prompts, answer key,
`action.yaml` registration or `human_review_required` flags. Other variants,
including VT01 `bomb-text-l1` and multi-stage VT07–VT10, retain their
existing scope until separately planned. Do not silently extend this rule to
source-gated v2+ visual revisions without a real Git source SHA.

## Required outcome

**Every completed baseline run must produce exactly one owner-facing GitHub
Issue for its own new runId, with original real PNG previews, a direct URL,
a typed Gateway receipt and a checked readback.** Issue publication is part of
the Action, not a separate test or optional convenience. The runner remains
responsible for this delivery; the coordinator is not a replacement runner.
If publication is blocked, the run is `ISSUE_PUBLICATION_BLOCKED`, not
`READY_FOR_HUMAN_REVIEW` or a full workflow PASS. A real QA failure is still
reported as a failure; do not conceal it merely to publish an Issue.

Do not create PRs, push source commits, change accepted `main`, or publish
incomplete transient drafts. Run products stay in the unique Workfiles
`runs/<runId>/` directory. Do not use `image_gen` or generated pictures as
assets or QA proof. Preview uploads are **PNG-only**; Blender/Godot source,
GLB, logs and chronological unabridged frame sequences remain in Workfiles
with exact paths and hashes. Issue screenshots do not prove animation playback.

## Typed Fortis delivery, no fallback client

Follow [UC-VIS-009](../../docs/use-cases/media-github-review.md#uc-vis-009),
`/workspace/repo/README.md`, UC-CONT-002/003, UC-GW-009 and the
`fortis_approvals/integrations/github/README.md` visual-review contract.
Only `fortis_approvals.workflow.client.default_client().github` is authorized:

1. Recheck `capabilities(refresh=True)` and `visualReview.repository`,
   `visualReview.publishPolicy=ALLOW`, `allowGitHub` containing
   `publish_visual_review`; validate target `visual-workspace`. Denial,
   missing capability or unknown status means STOP, not `gh`, PAT, GitHub
   connector, curl/REST or direct Git fallback.
2. Select **1–5 real PNGs**, each <=10 MiB, ordinary non-symlink files under
   this runId's Workfiles folder. At least one should be the real intended
   preview: VT01 exported 64x64 + Godot runtime; VT02 front/perspective/side;
   VT03/VT04 labeled clip phases/loop boundaries and Godot runtime; VT11/VT12
   provenance-preserving copies of chosen original frames (plus labeled
   contact sheets if useful), without evaluator material. Check full-size
   originals yourself; for 3D/animation retain original complete QA evidence
   outside the limited 1–5 PNG uploads.
3. Build an Issue title/body with Action/variant/unitId(s), runId, exact
   accepted definition HEAD, brief/fixtures, original source/QA evidence
   paths, observed strengths and deficits, and human-review state. No
   hidden answer-key contents, credentials or private data. Use a true integer
   `duration_seconds` measured **through the most recent completed stage**
   (e.g. T4-T0 for authoring), **not** a float or a fabricated final T5.
4. Choose and persist one `requestId` before writing. Perform read-only
   `prepare_visual_review(...)`, preserve `payloadSha256`, image SHA-256 and
   exact fields, then submit **one** `publish_visual_review(...)` using the
   same runId/requestId and `expected_payload_sha256`. Store the receipt.
   Do not send a new WRITE or new requestId on timeout, `UNCERTAIN` or
   lost response: investigate the same UUID via UC-GW-009 and stop.
5. On `EXECUTED`, read the **exact** `get_issue` through the typed Gateway:
   verify number, returned URL, expected runId marker, body and Markdown PNG
   references. Also page through `list_issues(state='all')`, including
   closed issues, to check there is exactly one same-runId result; report
   `DUPLICATE_CHECK_PENDING` if pagination is incomplete. GitHub markdown
   references alone do not verify remote image bytes: request the owner's
   browser review of actual attachment visibility.
6. In `runs/<runId>/reports/visual-issue-publication.md` or `.json` preserve
   capabilities/policy, preview digest, requestId, receipt state, Issue URL,
   real media list and local hashes, readback, duplicate-check and clock
   observations. In the per-unit submission link this receipt and URL; use
   `N/A` **only** for fields genuinely not applicable (source Git commit,
   source PR, revisions that did not occur). Final reply **must display**
   the direct clickable Issue URL, runId, submission path and whether owner
   browser attachment verification is still pending. Never call a missing
   Issue `N/A` after a successful visual Action.

## Order, timing and roles

- **VT01/VT02/VT03/VT04:** at T4 the actual authoring, exports, Godot visual
  review and technical QA are complete; start publication clock P0, complete
  Issue+readback+duplicate-check at P1, save evidence and final reports, then
  record T5 immediately before the runner's reply. Therefore **T5-T0 includes
  the Issue path**. Record P1-P0 separately for optimization. Neither P1 nor
  T5 may be guessed. Attachments must be ready for the owner to review before
  declaring `HUMAN_REVIEW_PENDING`. Human review remains **required**:
  owner checks real images in the Issue and comments
  `ACCEPTED/CHANGES_REQUESTED/INCONCLUSIVE`; coordinator records the real
  response to `human-review.md` and only then starts independent VT15.
- **VT11/VT12:** preserve blind experiment boundaries. First unit: complete
  original T0–T5, freeze its report/submission, independent first evaluator
  does **process-only** gate; **no GitHub write during this first stage**.
  Second unit in the **same runner chat**: record real S2.0–S2.5; freeze
  both case findings before publication. At S2.3 case reviews are complete;
  save the second unit's immutable findings/submission, then P0→Issue→P1
  before final S2.5. Publish only the runner's frozen findings, source case
  IDs and real PNGs, never the hidden key or evaluator score. Evaluators
  continue separately: final correctness scoring only after both frozen
  units; no human gate and no VT15 for these Actions. Preserve timing for
  first stage T5-T0, second stage S2.5-S2.0 and P1-P0 separately; do not
  hide owner/chat interruption in active work time.
- **Blocked publication:** keep real source/QA and all frozen unit reports,
  plus one stable attempt/receipt/UNCERTAIN trail; do not fake success or
  repeat a reserved runId. The coordinator decides what to do with that
  failure before starting human review. A subsequent independent rerun
  requires a **new chat and new runId**, not edits to historical evidence.

**Current first-pass history:** VT01 run
`VT01-crystal-20261121T052635Z-21234591a0` was generated under an *older*
no-Issue prompt and later published in Issue #22. Its recorded 598.231 s
T0–T5 must not be relabeled as an end-to-end run of this updated contract.
Rerun after an accepted new prompt revision, using a fresh runId and Issue.
