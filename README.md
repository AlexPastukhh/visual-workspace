# Visual Workspace

Git-tracked visual projects and source assets created with AI tools inside Fortis Repo.

- `projects/visual-mvp/` — historical editable Blender (`.blend`) and Krita (`.kra`) test projects, corresponding PNG previews and generators.
- `projects/game-animation-mvp/` — reproducible 2D sprite and rigged 3D character animation demo for Godot, with editable source assets and automated tests.
- `experiments/fortis-visual-poc/` — SVG/OBJ/PNG proof of concept and reproducible source.

## Fortis Repo (Linux Docker)

Primary clone: `/workspace/repo/Repos/visual-workspace`.

The existing Fortis Repo container is the development environment. Project files can contain code or application-specific active content; work produced by AI in this environment is treated as untrusted.

The old Blender/Krita files in `projects/visual-mvp/` are historical test artifacts. Blender 5.2.3 and Godot 4.7.2 execution are established and covered by launchers/tests. Krita execution in this container has **not yet been established**.

## Blender in Fortis Repo (Linux)

The Fortis Repo runtime has a local, ignored Blender installation. It is not committed to Git.

- Version: Blender 5.2.3 LTS (official Linux x64 archive).
- Launcher: `./tools/blender.sh`. It loads the shared runtime and keeps Blender config/cache under the current Worktree's `.fortis-state/blender/`.
- Check version: `./tools/blender.sh --version`.
- First round-trip: see `tools/BLENDER_RUNTIME.md`.
- Render mode: background mode, Cycles CPU, two threads. No GPU or X server is needed for this workflow.

The official Blender archive and required Debian 12 runtime libraries are stored under `.local-tools/`, which `.gitignore` excludes. The archive SHA-256 was verified against Blender's official checksum manifest. Runtime libraries were extracted locally from checksum-verified Debian packages; no system packages, Docker image, mounts, permissions, network policy or services were changed.

The `.blend` files and PNG renders produced by the workflow remain normal project deliverables and are tracked by Git.

## Godot and animation project

- Godot 4.7.2 is installed once under the shared `.local-tools/` runtime and launched through `./tools/godot.sh`.
- Run the editor in this container with `./tools/godot-xvfb.sh --editor --path projects/game-animation-mvp`; the wrapper starts an authenticated, temporary Xvfb display.
- Run the full asset/import/2D/3D animation test suite with `cd projects/game-animation-mvp && ./tools/run_tests.sh`.
- Blender and Godot binaries/runtime libraries are shared; each Worktree keeps its own home, XDG settings, runtime directory, caches and temporary files under `.fortis-state/`.

## Shared tools across Worktrees

Install heavy tools and their runtime libraries once in the primary clone's ignored `.local-tools/` directory. After creating a task Worktree, run `./tools/link-shared-tools.sh` once from it; the helper safely links `.local-tools` to the primary clone. Do not copy Blender, Godot or their libraries into individual Worktrees. Project sources and deliverables stay inside the Worktree. The launchers store Blender/Godot settings, home-directory fallbacks, XDG data, shader/font caches and temporary files under the ignored `.fortis-state/` directory in that Worktree. Godot's project import cache stays in that project's own `.godot/` directory. Removing a Worktree must never remove the shared `.local-tools` target.

Parallel use was smoke-tested with two Worktrees at once: both launched Blender and Godot, ran the animation test suite, and opened the Godot editor through separate temporary Xvfb displays. Their application state, caches and project files remained separate; the temporary test Worktree was removed afterward.
