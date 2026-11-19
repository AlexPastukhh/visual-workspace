# Northlight Beacon v1 → v2 in one Issue — acceptance evidence

Date: 2026-11-19 UTC. Scope: **one** existing 2D asset, public
`visual-workspace`, typed Fortis Gateway. This is not a clean-chat
reliability sample or a Windows game acceptance.

- v1: [GitHub Issue #5](https://github.com/AlexPastukhh/visual-workspace/issues/5);
  original run marker `northlight-beacon-e2e-v3-20261117`,
  source SHA `1a171dd03dbc90b422b6dd812b4038fcb8ec95dd`.
  Original PNG SHA256
  `4518f1cfd7c1fd335a7907427ebd9964b3a60f9ac303a94aa2617cb283d7536a`.
- Owner direction: `«измени что то, не важно что»`.
  Real SVG change: north needle, cardinal north tick and center jewel
  changed from amber to coral-pink; existing scene and silhouette kept.
- v2 source Git commit:
  `06b0c9fe3ae9ae1ce7effe83e128045c711701b3`,
  in the preserved original Northlight task branch. Its former PR #6
  was already merged, so Gateway correctly rejected reuse of that branch
  (GIT_DELIVERY_PRIOR_PR_CLOSED). A NEW task based on current main
  carries byte-identical v2 source and documentation. The new PR will
  have its own commit SHA; it does not pretend that this historical v2
  commit is its ancestor. Both task branches remain preserved.
- Godot 4.7.2: new real 1280x720 PNG, 6/6 static frames byte-identical,
  original v1 compared by actual image inspection. SHA256:
  `17f14800b2a7d8baccc1861c1fdcafcb59c0ddea7d95948c4b3c667f1e937310`.
  Runner elapsed 19.515s (not a chat wall-time measurement).
- Typed `prepare_visual_revision`: repeated stable payload SHA
  `c353b1deb891cdb0f5952dbbe215f724e3ae1b0f4ef1c759a1f49239605f82f9`.
  Submitted exactly once via `append_visual_revision` with
  `revision=2`, `baseRunId=northlight-beacon-e2e-v3-20261117`,
  new `runId=northlight-beacon-e2e-v2-20261119`,
  request ID `3a2f326d-b839-46cc-928c-b697cef338c2`.
  Result `EXECUTED`; durable receipt `commentId=7010209589`,
  `uploadedFiles=1`.
- [Actual v2 comment](https://github.com/AlexPastukhh/visual-workspace/issues/5#issuecomment-7010209589).
  Readback: **same** Issue #5, original v1 body/PNG reference unchanged,
  exactly one v2 comment, marker/sourceSha matched and new PNG link
  distinct from v1. No second Issue for this v2.
- Browser acceptance: owner answered `«все нормально»` after
  receiving the exact v2 link. This confirms acceptance **as reported
  by the owner**; Gateway READ only proves Markdown attachment URLs,
  not remote byte-for-byte image integrity. Do not overclaim a
  second independent network image hash verification.
- Current result: `ISSUE_REVIEWED = TRUE`;
  `SOURCE_MERGED = FALSE` until source PR owner-merged;
  `GAMEPLAY_ACCEPTED = FALSE` (preview-only static 2D).
- Recorded run artifacts and immutable intent/receipt:
  `/workspace/repo/Workfiles/visual-workspace/northlight-beacon-e2e-v2-20261119/`.
  Unmeasured chat T0–T5 must remain `NOT MEASURED`.
  Fresh-chat VR01 v1/V08/C03/C04/C05/C06 have **NOT RUN** status.

Policy: live `publishPolicy=ALLOW` and `appendRevisionPolicy=ALLOW`
for exact public `visual-workspace` on 2026-11-19; use fresh
capabilities on every subsequent write. New versioned reviews still need
owner request/feedback and actual browser verification.
