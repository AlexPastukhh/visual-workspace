# Visual QA Registry

Read this file at the start of every asset task. Select only modules that match the task; do not apply every checklist by default.

## Selection

| Module | Apply when | Main questions |
|---|---|---|
| [Common](modules/common.md) | Always | Is the result readable, intentional and consistent with the brief? |
| [2D Animation](modules/2d-animation.md) | Animated 2D sprites or scenes | Are frames, timing, pivots and screen-space motion correct? |
| [Multi-Actor Motion](modules/multi-actor-motion.md) | Two or more moving actors interact or share a scene | Are their trajectories, relative positions and timing correct? |
| [3D Character](modules/3d-character.md) | Rigged or skeletal characters | Are pose, gait, facing, feet and deformation correct? |
| [3D Vehicle](modules/3d-vehicle.md) | Vehicles with translation, steering, turning or suspension | Does orientation match the intended forward/reverse motion? |

## Selection boundaries

A static prop normally needs Common; selecting a 2D/3D kind alone does not require every animation module. Add specialist modules for the actual behaviour and acceptance risks. Required evidence is selected in [WORKFLOW.md](../WORKFLOW.md#5-choose-evidence-to-match-the-acceptance-question); module questions do not require all possible captures on every iteration.

## Use rules

- Read Common plus every clearly applicable specialist module before review.
- Record the selected module IDs in asset.qa.json; the brief remains the authority for intent.
- A module describes review questions and evidence needs. It does not force every possible metric or camera on every asset.
- If a check is irrelevant, mark it not applicable and explain briefly; do not invent a defect.
- If no existing module covers a genuinely reusable problem, review whether to extend an existing module before proposing a new one.
- Keep task-specific values and one-off observations in that asset's brief.md or review report, not in this registry.
- Promote knowledge only when it is generalizable, useful and supported by evidence. See the Knowledge Review section in WORKFLOW.md.

## Asset QA entry point

See [STATUS.md](STATUS.md) for current implementation coverage, regression results and known limitations.

Use tools/visual_qa/run_visual_qa.py --asset <path-to-asset.qa.json>.
The manifest schema is tools/visual_qa/asset-contract.schema.json; validation is available with tools/visual_qa/validate_asset.py.
The asset-level runner can capture contract-driven skeletal and foot evidence; projects/game-animation-mvp retains its specialized AnimationTree/controller regression runner and tests.
