# Animation Relay — playable integration brief

Create a small standalone Godot game demonstrating that the existing 2D atlas and rigged
3D GLB work as gameplay resources. Reuse the assets; do not recreate art or the capture stack.

Two side-view levels (2D and a 3D level constrained to a horizontal lane):
move left/right, walk/run, jump and land, activate an amber relay to lift a closed gate,
then reach the teal exit. A native UI switches levels, jumps, activates the relay and restarts.
Keyboard: A/D or arrows, Shift, Space, E. No autoplay and no qa_set_time in gameplay code.

Acceptance: real input selects visible animations; movement uses CharacterBody collisions/
gravity; the closed gate blocks passage; activation outside relay range does nothing;
the relay animates the gate open and permits reaching the exit; restart resets the objective.
The same executable gameplay path handles keyboard and native mouse clicks.

Parameters: existing 64x64 source atlas frames with Idle 4, Walk 10, Run 15 and Jump 7 FPS;
existing GLB clips with explicit Godot loop configuration (Idle/Walk/Run loop, Jump one-shot).
Window/QA images 1280x720, physics 60 Hz, QA fixed sampling 24 FPS. Runtime normal launch
is not locked to the QA capture rate. The 21-step scenario lasts 383 frames / 15.9583 seconds.
These values are project/reused-asset constraints and implementation choices, not a user
requirement for all future games. No source animation quality enhancement is in scope.

Deliver a Godot project with project-local runtime resources, no QA dependency in the game,
a repeatable input-driven test and screenshots/metrics suitable for direct visual review.
Test a fresh isolated copy with imports rebuilt. A platform executable build and OS-level
input automation are separate, untested delivery levels.
