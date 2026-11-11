# Asset Workbench

A small Godot project for creating and independently reviewing new 2D/3D assets. It is the pilot consumer of the shared asset-level Visual QA contract.

## Assets

- assets/planes-dual-pass/ — editable SVG aircraft sources, task brief and QA manifest.
- assets/car-jump-turn-reverse/ — editable Blender source, generated GLB, task brief and QA manifest.
- assets/pulse-beacon-2d/ and assets/rotor-beacon-3d/ — new content assets prepared with shared neutral stages and ordinary animation clips.

Each asset owns its brief and technical manifest. The project owns shared scenes and scripts. Runtime captures and caches are generated under the ignored project .fortis-state directory.

## Run an asset

From the Visual Workspace repository root:

~~~bash
python3 tools/visual_qa/validate_asset.py --manifest projects/asset-workbench/assets/planes-dual-pass/asset.qa.json
python3 tools/visual_qa/run_visual_qa.py --asset projects/asset-workbench/assets/planes-dual-pass/asset.qa.json

python3 tools/visual_qa/validate_asset.py --manifest projects/asset-workbench/assets/car-jump-turn-reverse/asset.qa.json
python3 tools/visual_qa/run_visual_qa.py --asset projects/asset-workbench/assets/car-jump-turn-reverse/asset.qa.json
~~~

## Targeted iteration

~~~bash
python3 tools/visual_qa/run_visual_qa.py --asset projects/asset-workbench/assets/car-jump-turn-reverse/asset.qa.json --phase turn_180
python3 tools/visual_qa/run_visual_qa.py --asset projects/asset-workbench/assets/car-jump-turn-reverse/asset.qa.json --force-rebuild
~~~

A phase-only run produces evidence for that phase; it does not replace the final full-asset End-to-End review. The incremental cache is per asset and phase. Unchanged phases are reused; contact sheets can be rebuilt without recapturing runtime frames.

## Capture contract

- Every scene implements `qa_set_time(seconds)`; the runner freezes wall-clock simulation and requests each sample at its exact timestamp.
- kind 2d_scene tracks Node2D actors and captures the shared scene at the configured FPS.
- kind 3d_scene tracks Node3D actors, captures perspective frames and optionally synchronized Front / Side / Top / Perspective composites.
- Actor position, derived velocity, forward vector, rotation and facing/velocity alignment are recorded.
- The runner captures the actual Godot scene over time. It does not repair assets or infer artistic quality from metrics.
- The selected QA modules are assembled into the review prompt. GPT must receive the actual PNGs through the Fortis Repo image-transfer method in tools/README.md.

The contract is defined in tools/visual_qa/asset-contract.schema.json. The standard-library validator is tools/visual_qa/validate_asset.py. Capture and cache implementation details belong in tools/visual_qa/README.md.


## Start a task

Use the maintained neutral stages in qa/ via tools/visual_qa/new_asset.py from the repository root. See [the tool documentation](../../tools/visual_qa/README.md#start-a-new-asset-with-shared-stages) for commands, framing and custom-controller boundaries. Only content behaviour and task configuration belong in each asset.

## Content versus review scenes

The asset content/source scene or exported runtime resource is what can be integrated into
another game. Generated preview.tscn, the neutral qa/ stages and asset.qa.json are review
infrastructure. Do not present the preview scene as a portable gameplay implementation.
For game-ready delivery, follow [the integration acceptance rules](../../WORKFLOW.md#evidence-required-for-game-ready-delivery).
