# Evaluator-only instructions — not for the test-taking chat

The key in answer-key.json is **not copied** to Workfiles runs by run.py.
The evaluator-only `verify_seeded.py` checks that the intended original
fault injections remain exact without revealing those case labels through
the public fixture verifier. Run this integrity check only as the
owner/evaluator **outside** the test-taking chat.
Within a shared repository it is not access-controlled secrecy: an agent
given arbitrary repo read permissions can open it. For truly blind tests,
the owner must prevent the evaluated agent from reading this directory and
withhold the correct labels until its output is final.

## Interpreting evidence across chats

Preserve the `cold`, `batch`, `production` or `confirmation` mode
for each reported result. Several case scores from **one chat** are
correlated observations, not independent model trials. Bootstrap and
warm-context durations should not be pooled as if the same conditions
held. A single V03/V04 pass confirms only the specific smoke test.
Do not infer a reliable success percentage from the current tiny fixture
set, and do not reveal the key before a test chat submits its final result.

When prompt text, source images, brief, sampling policy or the workflow
changes, record its version/HEAD and separate it from earlier results.
Keep existing examples immutable for before/after comparisons, and add
new previously unseen cases to detect overfitting to a fixed key.
Track time-to-first-preview and total end-to-end time separately, and
cite external timings where possible rather than relying on the tested
chat's unsupported claims.

## Timing and acceptance across complexity levels

All **new graded prompts** require [actual UTC timestamps](../TIMING.md)
T0..T5 recorded by the test-taking chat from tool-returned clock values,
not guessed human estimates. After the run, copy the
[scorecard template](scorecard-template.md) **into Workfiles** and fill it as
an independent evaluator, preserving the raw marks and any unknowns.

Compare **total T5−T0** (bootstrap, tools, reasoning, QA, reporting)
only for comparable prompts/fixtures/environments. Also report bootstrap
T1−T0, first image or actual Godot preview T3−T0, substantive work
T4−T2, and per-case review durations. The interval before T0 and after
T5 is not included; compare actual UI send-to-finish timing separately
if available. An attractive model-reported number without raw timestamps
is not a measured performance result.

For review tests V05 (2D pair), V08 (mixed pair), V06 (3D trio), V07
(five-case stress), compare both aggregate quality and each case's
individual verdict. They differ in scope, so do **not** rank models or
workflow versions solely by absolute runtime across different tiers.
For production C01/C02 test static basics, C03/C04 animation, C05
full gameplay; require one written order per normal test. C06 is an
optional multi-order workload and should not inflate the default test.

A speed improvement with degraded temporal coverage, fewer real Godot
previews, or a skipped requirement is **not** a valid optimization.
Record failures and rework without altering a fixed benchmark prompt.

## Visual detection scoring (per case)

- 2 points: correct fault/no-fault verdict. No-defect controls count.
- 1 point: accurate temporal localization for a defective case (local frame
  index and/or time, within a relevant short interval); for a control, correct
  explicit assessment that examined frames reveal no material defect.
- 1 point: observations grounded in actual images and brief, distinguishing
  visible evidence from speculation/metrics.
- Minus 1 per material invented defect, floor at 0. A high-confidence false
  accusation on a normal case is a regression; no fabricated certainty.
- Track confusion matrix: TP/TN/FP/FN and localization separately. Avoid
  percentage conclusions from a single small sample or self-review.

## Authoring acceptance (per independent requested unit)

- 25% brief compliance: specified form, 2D/3D, proportions, colors/style,
  formats, sizes and named action requirements actually match.
- 20% editable source, export and Godot import: required real resources
  exist, project opens without missing dependencies.
- 20% animation/game behaviour: requested clips and loop policy work;
  where requested, actual user input and state transitions are exercised.
  Mark this block N/A and redistribute to other blocks for static orders.
- 25% visual evidence and self-critique: real game-size PNGs were received,
  relevant phases/views/loop boundaries were examined, observed shortcomings
  were addressed or explicitly disclosed.
- 10% efficiency/reproducibility: first preview and total time, chosen
  targeted tests, separate output units, repeat commands and no repo writes.
- An absent required editable source or game integration cannot be compensated
  by attractive screenshots. A technical PASS is not visual acceptance.
- For A06 grade crystal and column separately, then verify non-overlap.
  For A05 verify gate collision, out-of-range E, opening, exiting and reset.

## Evidence record template

Run ID / new chat ID (nonsecret), task/case, start/end timestamps, touched
paths, actual image paths inspected, observed issues with local frames/times,
objective test markers, final verdict, remaining uncertainty, first-capture
seconds, cached-repeat seconds. Compare with the key only after submitting
the tested model's output. Do not modify the test key based on reviewer guesses.

## Fixture provenance

Visual controls were copied from existing Visual Workspace captures and
two faults were seeded as a single abrupt frame replacement. The historical
walk-freeze example is from an earlier intentionally failing QA snapshot.
These are practical controls, **not** certified gold-standard production art.
The default selected set is balanced by dimension (2D normal/fault; 3D normal/
transient fault plus historical walk failure). Reviewers may have false alarms
about noncritical stylistic issues: require evidence and task relevance.
