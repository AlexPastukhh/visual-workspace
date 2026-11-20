# <repair-unitId> — UNPLANNED corrective message for the ORIGINAL runner chat

Existing scenarioId: <scenarioId>
Same runId: <existing runId>
Logical unit: <SCxx.yy-R1 or SVxx.yy-R1>
Original unit + evaluator decision: <prior unitId and exact decision path>
Observed material defect/evidence: <objective failure, precise files, frames or receipt>
Correction request: <minimal concrete change only; no new unrelated task>
Original planned next stage is PAUSED until this repair is independently evaluated.

IMPORTANT: Work through the EXISTING Visual Workspace workflow with Fortis Repo; for SC edit actual editable SVG/Blender/Godot sources in the already registered task worktree, export PNG from the source project, inspect real Godot/Blender frames. NEVER call ChatGPT image_gen or any AI image-generation system to create or edit the object, a replacement illustration, or test evidence. If the source/tools are unavailable, report BLOCKED; do not invent completion. For SV this is a read-only review: do not modify fixtures, generate synthetic frames or leak evaluator-only correct labels.

Keep the original run folder and task identity. Do not overwrite prior reports or previously published versions. If the corrected SC result is shown to owner after a published v1, append ONE next sequential revision to the original GitHub Issue (not a new Issue), using a fresh source Git SHA, runId/requestId as required by UC-VIS-009, actual receipt and readback. Follow live Gateway authorization and UNCERTAIN STOP policy. The planned SCyy.02/.03 prompts remain unexecuted until this new unit passes its gate; their nominal v2/v3 filename does not determine actual comment revision.

Save the resulting proof in /workspace/repo/Workfiles/visual-workspace-practical-tests/runs/<existing runId>/reports/units/<repair-unitId>/submission.md as mandated by UNIT-SUBMISSION-CONTRACT.md. Include source SHA, actual QA files/images, actual Issue/revision/comment, requestId and correct timing for this repair. Send exact handoff path to owner; do not open any adjacent evaluator prompt or _evaluator directory.
