# Tools for Visual Workspace

Use [WORKFLOW.md](../WORKFLOW.md) to choose the work and review sequence.
This file is the capability index and the verified image-transfer procedure.
Read only the detailed documentation relevant to the selected route.

## Find a reusable capability

| Need | Existing capability / reference | Scope |
|---|---|---|
| Prepare an isolated asset preview | [Asset preparer and neutral stages](visual_qa/README.md#start-a-new-asset-with-shared-stages) | Workbench textures, 2D/3D scenes and ordinary AnimationPlayer clips |
| Capture one asset or phase | [Asset Visual QA Runner](visual_qa/README.md) | Deterministic scene state/clip capture, metrics, sheets and cache |
| Set cameras and read frame/time captions | [Framing](visual_qa/README.md#framing-and-readable-sheets) | Manifest-driven multiview; main-view stage exports |
| Edit/generate and export in Blender | [Blender runtime](BLENDER_RUNTIME.md), [launcher](blender.sh) | Existing installed runtime and editable source/export workflow |
| Import or run Godot without rendering | [Headless launcher](godot.sh) | Resource import, structural and controller tests |
| Render/run Godot in the container | [Graphics launcher](godot-xvfb.sh) | Runtime images, scene playback and editor |
| Create sprite frames / atlas | [2D generator example](../projects/game-animation-mvp/tools/make_2d_assets.py), [project documentation](../projects/game-animation-mvp/README.md) | Reference for editable ORA, PNG atlas and SpriteFrames; new art/timing remain task work |
| Create a rig and clips | [Blender robot generator example](../projects/game-animation-mvp/tools/make_3d_robot.py), [project documentation](../projects/game-animation-mvp/README.md) | Reference for rig/Action/export plumbing, not a universal character generator |
| Procedural motion / multiple actors | [Planes scene](../projects/asset-workbench/scripts/planes_dual_pass.gd), [vehicle scene](../projects/asset-workbench/scripts/car_jump_turn_reverse.gd) | Behavioural examples using the common capture contract |
| Character skeletal evidence | [Character adapter documentation](visual_qa/README.md#supported-capture-adapters), [configured fixture](../projects/game-animation-mvp/assets/qa-character/asset.qa.json) | Skeleton, feet and simple animation-state metadata |
| Validate animations in an actual playable game | [Animation Relay](../projects/playable-animation-demo/README.md) | Keyboard/mouse input, collisions, sequential animation, clean-project portability and screenshot/observation agent loop |
| Controller regression / specialized humanoid QA | [Game Animation Lab](../projects/game-animation-mvp/README.md), [specialized runner](../projects/game-animation-mvp/tools/visual_qa/README.md) | Existing fixture/controller tests; not automatically required for every new model |

Examples show reusable techniques, not the required art style or production-quality ceiling.
Inspect and adapt the relevant part; do not regenerate or overwrite unrelated demo assets.
Tool details, supported formats, CLI arguments and limitations have one home in the linked docs.
Runtime/worktree setup is documented in the [repository README](../README.md).

## Record sequential Godot playback when the task needs it

Godot Movie Maker can record a scene as PNG frames. This is a playback path, not an
automatic controller-input harness; use the project's controller/demo inputs as appropriate.

~~~bash
mkdir -p projects/game-animation-mvp/.fortis-state/visual-review
./tools/godot-xvfb.sh \
  --path projects/game-animation-mvp \
  --scene res://scenes/demo_3d.tscn \
  --write-movie projects/game-animation-mvp/.fortis-state/visual-review/walk.png \
  --fixed-fps 24 --quit-after 120 --disable-vsync
~~~

The output is a numbered PNG sequence. Choose the scene, duration and FPS for the task.
The generic asset runner's deterministic sampling and the specialized controller tests
have different evidence scopes; see their own documentation.

## External video and frame sequences

For [UC-VIS-006](../docs/use-cases/README.md#uc-vis-006), an **existing**
numbered PNG sequence can be reviewed without a Godot source scene, asset
manifest or rerunning any asset capture. Retain the original complete sequence,
its real FPS and source time origin (do not mistake sampled frames for the
original playback FPS). Use an ignored, task-local output directory.

For a sequence `frame_0000.png`, `frame_0001.png`, etc. at 24 FPS:

~~~bash
mkdir -p projects/asset-workbench/.fortis-state/video-review/example
./tools/godot.sh --headless --path projects/asset-workbench \
  --script "$PWD/tools/visual_qa/build_contact_sheet.gd" -- \
  --input-dir "/absolute/path/to/numbered/pngs" \
  --output "$PWD/projects/asset-workbench/.fortis-state/video-review/example/contact_sheet.png" \
  --prefix frame_ --max-frames 24 --columns 6 \
  --tile-width 320 --tile-height 180 --fps 24
~~~

The builder creates `contact_sheet.png`, `contact_sheet.json` and a
`selected/` directory, mapping selected frames to original frame indices
and times. The command was verified with an existing 24-FPS Godot animation
sequence. Adjust prefix and FPS to **actual** source metadata; if a sequence
was already subsampled, supply explicit timestamps and do not infer the
original timing from its file names. Open the real contact sheet through the
image reader below, then 4–6 chronological original full-resolution PNGs
around each event and suspicious boundary. Inspect more densely when a
short defect could lie between sampled frames.

**Encoded video limitation:** there is currently no verified decoder for
arbitrary MP4/MOV/WebM in this container. `ffmpeg`/`ffprobe` are absent;
the installed Blender build does not expose FFmpeg output. Do not claim that
an encoded video was inspected without successfully decoding it to frames.
If no approved decoder/source frames are available, report the review as
blocked. Godot Movie Maker (above) already creates numbered PNGs and needs
no decoder. The visual-inspection strategy is in
[WORKFLOW](../WORKFLOW.md#5-choose-evidence-to-match-the-acceptance-question).

## Передача PNG в визуальный контекст GPT через Fortis Repo

Image paths and JSON do not supply image content. Read actual PNGs through the available
Fortis Repo reader, then forward each image item into visual context. Discover the enabled reader rather than depending on a client-specific tool-name prefix.

~~~js
const readers = ALL_TOOLS.filter(({ name }) => /fortis.*read_multiple_files$/i.test(name));
if (readers.length !== 1) throw new Error("Select the intended Fortis Repo reader from connected tools");
const result = await tools[readers[0].name]({ paths });
const items = result.content_items?.some(item => item.type === "image")
  ? result.content_items : (result.content ?? []);
const images = items.filter(item => item.type === "image");
text({ requested: paths.length, received: images.length });
for (const item of images) image(item);
~~~

- Use absolute paths and order frames chronologically.
- Read a small batch (normally 4–6 full-resolution images) and verify received counts.
  If a read is incomplete, inspect its error and retry the missing images.
- Forward images with image(item); do not print Base64 or the complete reader response.
- Start with overview sheets; then inspect individual PNGs around relevant actions,
  transitions, loop boundaries or suspected defects. Keep the full sequence available.
- For 3D details, use full-size synchronized composites and additional views/crops when needed.
  Do not infer foot or mesh quality solely from a small multiview contact-sheet tile.
- Supply frame/time metadata as a separate compact text block.
- Use maintained capture scripts. Historical ad-hoc helpers under .fortis-state are not
  a substitute unless their synchronization and timestamps have been verified.

## Support boundaries

Krita execution is not established in this container. There is no external vision model
or automatic artistic acceptance. GPT reviews images against the brief and selected QA
modules. A separate graphics worker, heavy CV package or mandatory full benchmark is not
needed for the ordinary asset loop.

[Current implementation evidence and known limitations](../qa/STATUS.md) are a status record,
not additional operating instructions. [Historical visual feedback PoC](../experiments/fortis-visual-poc/README.md)
documents the original static-image experiment.
