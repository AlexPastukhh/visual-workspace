# Timing protocol — reproducible wall-clock measurement

Use this protocol for **every new practical test**, both read-only visual QA
and production (2D, 3D, animation, game integration). It measures elapsed
**wall-clock time of an actual chat run**, not CPU/Godot runtime alone.

## How to measure without a test launcher

A fresh chat has no reliable built-in timer spanning reasoning and tool calls.
At the milestones below, read **the container's UTC clock** using Fortis Repo,
for example a short shell command:

```sh
date -u +"%Y-%m-%dT%H:%M:%S.%NZ"
```

Copy the *returned timestamps* (never estimates or invented timings) to
`timing.md` in the run's own Workfiles folder. Do this **before opening**
the workspace README for T0 and immediately after the relevant milestone.
There is no need to run a project-local benchmark script or prepare folders
before the prompt. If the clock is unavailable, record `unavailable` and
explain; do not substitute confident-looking estimates.

| Mark | Visual review (existing images) | Authoring (new 2D/3D/game) |
| --- | --- | --- |
| **T0** | First accessible clock read, before README/bootstrap. | Same. |
| **T1** | Workspace bootstrap and necessary workflow/QA reading complete. | Same. |
| **T2** | All assigned briefs/metadata reviewed, review plan ready. | Requested written brief and initial implementation plan ready. |
| **T3** | First *actual* full-resolution PNG visually inspected (not its path/JSON alone). | First real Godot/runtime game-size preview visually inspected (not a source-file mockup). |
| **T4** | All assigned case images inspected and per-case verdicts formulated. | Required production, in-game checks, final visual review and targeted tests completed. |
| **T5** | Final reports and timing record saved and verified, immediately before final reply. | Same. |

**Total measured:** T5 − T0, including bootstrap, tool wait, viewing, reasoning,
development, rendering, validation and documentation. Do not measure only
script runtime, cached capture or time spent opening PNGs and call it total.

**Phase breakdown:** bootstrap T1−T0; brief/plan T2−T1; first useful
visual feedback T3−T0; substantive work T4−T2; final reporting T5−T4.
These phases overlap in the intended sense of a cumulative milestone:
do not sum the cumulative T3−T0 with phase durations.

For a **multi-case review**, also record the time when visual inspection of
each case starts and when its assessment is complete; these per-case intervals
may not add up to the total because shared preparation, tool calls and report
writing are outside them. Name the case, count of original PNGs actually
opened, and any reason for missing evidence. Prefer scanning all original
frames for tests of rare one-frame glitches; a sparse contact sheet does not
establish smoothness.

For authoring, optionally record first export, first import and final
gameplay test as additional marks. The first preview **must be real Godot
output**; don't replace it with a generated illustration. Repeated/cached
preview times, if checked, are supplementary and separately labeled.

## Minimum timing.md in Workfiles

Write a small table with `T0..T5`, exact UTC timestamps, observed event,
calculated durations in seconds, **total T5−T0**, and a short note on
whether time was measured using tool-returned timestamps. For multi-case
reviews list per-case start/end and input frame coverage. Also include
prompt ID, assigned case/order IDs, workspace HEAD and dirty status as
observable, and evidence paths. Avoid extensive telemetry or custom runners
that themselves dominate the task.

## Interpretation / limitations

- The interval before the first clock call and the period after T5,
  including UI delivery, are **not** in T5−T0. For exact user-perceived
  end-to-end latency, the owner must also use external chat send/finish
  timestamps where available.
- Human waiting/approvals, network stalls and reused warm caches affect
  wall-clock time; disclose material conditions. Use consistent tools,
  model/configuration, and inputs before comparing runs.
- Do not trade away required temporal frame coverage, brief compliance or
  source/preview quality for a shorter measured runtime.
- A correct artistic PASS and a good runtime are **separate outcomes**;
  summarize the bottleneck (bootstrap, images, rendering, tool calls,
  retries, QA, game tests) only when supported by observed timings.
- Legacy V03/V04 runs completed before this protocol have quality
  results, but **no comparable total timing**. Never retroactively infer
  their duration from prose or timestamps embedded in a path.
