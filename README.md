# Visual Workspace

Git-tracked visual projects and source assets created with AI tools inside Fortis Repo.

- `projects/visual-mvp/` — historical editable Blender (`.blend`) and Krita (`.kra`) test projects, corresponding PNG previews and generators.
- `experiments/fortis-visual-poc/` — SVG/OBJ/PNG proof of concept and reproducible source.

## Fortis Repo (Linux Docker)

Local checkout: `/workspace/repos/visual-workspace`.

The existing Fortis Repo container is the development environment. Project files can contain code or application-specific active content; work produced by AI in this environment is treated as untrusted.

The old Blender/Krita files in `projects/visual-mvp/` are historical test artifacts. Current Blender and Krita execution in this container has **not yet been established**.

## Blender in Fortis Repo (Linux)

The Fortis Repo runtime has a local, ignored Blender installation. It is not committed to Git.

- Version: Blender 5.2.3 LTS (official Linux x64 archive).
- Launcher: `./tools/blender.sh`. It sets the local library search path and keeps Blender config/cache under `.local-tools/`.
- Check version: `./tools/blender.sh --version`.
- First round-trip: see `tools/BLENDER_RUNTIME.md`.
- Render mode: background mode, Cycles CPU, two threads. No GPU or X server is needed for this workflow.

The official Blender archive and required Debian 12 runtime libraries are stored under `.local-tools/`, which `.gitignore` excludes. The archive SHA-256 was verified against Blender's official checksum manifest. Runtime libraries were extracted locally from checksum-verified Debian packages; no system packages, Docker image, mounts, permissions, network policy or services were changed.

The `.blend` files and PNG renders produced by the workflow remain normal project deliverables and are tracked by Git.
