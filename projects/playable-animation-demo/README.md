# Animation Relay — playable 2D/3D integration

A standalone Godot project using existing runtime assets in an actual input-driven game.
Walk/run/jump, activate the amber relay to lift a physical gate, and reach the teal exit.
Switch between a 2D level and a 3D side-view level. No autoplay, pose seeking or QA runtime
dependency is present in the game scripts.

## Play

Open project.godot in Godot (the workspace runtime is 4.7.2) and run the project.
From the Visual Workspace root, the container launcher is:

~~~bash
./tools/godot-xvfb.sh --path projects/playable-animation-demo
~~~

The container launcher uses its virtual display; opening the project in a desktop Godot
editor gives the user a normal interactive window.

| Control | Behaviour |
|---|---|
| A/D or Left/Right | Move and select Walk/Idle |
| Shift while moving | Run |
| Space or JUMP button | Jump while grounded; return to locomotion after landing |
| E or ACTIVATE RELAY button | Open the gate when near the relay |
| 2D LEVEL / 3D LEVEL | Switch level and reset its objective |
| RESTART | Reset the current level |

The 3D level is intentionally constrained to a horizontal lane, not a free-roaming world.

## Resources and parameters

Editable gameplay is in scripts/. assets/robot_atlas.png and assets/gamebot_animated.glb
are unchanged exports reused from Game Animation Lab, copied locally so the game does not
depend on another project's files. Their editable source remains documented in
[Game Animation Lab](../game-animation-mvp/README.md).

The atlas has 64x64 source frames; Idle/Walk/Run/Jump playback is 4/10/15/7 FPS.
Run reuses two walk frames, a known inherited art limitation. GLB clips run through
AnimationTree with explicit looping for Idle/Walk/Run and one-shot Jump.
The project uses CharacterBody2D/3D, collision shapes, gravity and move_and_slide.

Window/QA images: 1280x720. Physics: 60 Hz. Fixed QA rendering: 24 FPS.
Ordinary interactive play is not locked to the QA rate. See [brief.md](brief.md) for intent.

## Repeatable input E2E

~~~bash
# Fast checks with the actual sequential gameplay and input, without image capture:
python3 projects/playable-animation-demo/tests/run_playtest.py --quick

# Full PNG sequence, contact sheet, telemetry, assertions and a clean-project portability test:
python3 projects/playable-animation-demo/tests/run_playtest.py --portable
~~~

Run from the workspace root. This project-scoped driver uses Input.parse_input_event:
keyboard events and mouse press/release coordinates go through the Godot input/GUI path.
Tests do not call player movement methods, set actor positions, select animation poses or
open the gate directly. The 21-step scenario includes both positive and negative cases:
out-of-range activation, closed-gate blocking, left/right movement, walk/run/jump/landing,
relay activation, exit, level change and restart.

Each full run is in .fortis-state/playtests/run-*/:
- frames/: all 383 primary PNGs (15.9583 simulated seconds at 24 FPS);
- metrics.json: per-frame game state and timestamps;
- steps.json: inputs, assertions and before/after observations;
- contact_sheet.png plus selected full-size frames;
- result.json / run.json and per-stage logs;
- portable-project/: runtime-only copied game; imports are rebuilt and the same input
  scenario rerun without any QA scene or test files inside the copied runtime project.

The driver stays in tests/. The game can run without it. Full test orchestration reuses
the existing Godot launchers and shared contact-sheet builder rather than another capture stack.

## Agent observation/action loop

For exploratory play, launch a session from the workspace root with new, absolute output paths:

~~~bash
./tools/godot-xvfb.sh --fixed-fps 24 --disable-vsync \
  --path projects/playable-animation-demo \
  --script "$PWD/projects/playable-animation-demo/tests/input_driver.gd" -- \
  --agent-dir "$PWD/projects/playable-animation-demo/.fortis-state/my-agent-session" \
  --output "$PWD/projects/playable-animation-demo/.fortis-state/my-agent-session"
~~~

Wait for state.json, then submit a short action:

~~~bash
python3 projects/playable-animation-demo/tests/agent_command.py \
  projects/playable-animation-demo/.fortis-state/my-agent-session \
  --keys D SHIFT --frames 24

python3 projects/playable-animation-demo/tests/agent_command.py \
  projects/playable-animation-demo/.fortis-state/my-agent-session \
  --click Jump --frames 8

python3 projects/playable-animation-demo/tests/agent_command.py \
  projects/playable-animation-demo/.fortis-state/my-agent-session --quit
~~~

Between commands the gameplay is paused. The reply gives observation, passed assertions
and the screenshot path. Read the actual PNG through Fortis Repo, inspect it, choose the next
command and repeat. Specify optional --expect with a JSON assertion object. Do not submit
concurrent commands; the client detects a pending request. Each command is 3–240 rendered
frames and idle sessions expire after five minutes. Use a fresh session directory per run.

This is a project-specific observation/action interface with structured telemetry plus images,
not a universal agent that can visually play any arbitrary game. All commands still enter
through keyboard/mouse events rather than direct game-state mutation.

## Verified result and scope

- Quick sequential test: 21/21 steps, 383 simulated frames, about 14.8 seconds including import.
- Full visual + clean runtime copy: 21/21 steps in each copy; 383 PNGs; about 103 seconds.
- Agent-guided session: 9 input steps, 228 PNGs; both exits reached. Actual intermediate
  screenshots and observations informed the next commands, including the 3D jump button.

Evidence: .fortis-state/playtests/run-20261106T043046004059Z and .fortis-state/agent-play/.
The visual review is saved next to the full evidence.

This proves the reused resources work in this small playable game and clean Godot project.
It is not a test of OS-level physical input, an exported executable, another platform/engine,
every possible control sequence or production animation quality. The reused sprite/rig art
retains the source fixture's limitations. It is an integration example, not a required
replacement controller or art template for all future tasks.
