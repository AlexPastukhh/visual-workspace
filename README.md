# Visual Workspace

Git-tracked visual projects and source assets created with AI tools inside Fortis Repo.

- `projects/visual-mvp/` — historical editable Blender (`.blend`) and Krita (`.kra`) test projects, corresponding PNG previews and generators.
- `experiments/fortis-visual-poc/` — SVG/OBJ/PNG proof of concept and reproducible source.
- `tools/Connect-VisualWorkspace-Windows.ps1` — optional Windows clone / fast-forward-only pull helper.

## Fortis Repo (Linux Docker)

Local checkout: `/workspace/repos/visual-workspace`.

The existing Fortis Repo container is the development environment. Project files can contain code or application-specific active content; work produced by AI in this environment is treated as untrusted.

The old Blender/Krita files in `projects/visual-mvp/` are historical test artifacts. Current Blender and Krita execution in this container has **not yet been established**.

Git operations use the centrally configured shared credential helper described in `/workspace/repo/README.md`. Never copy GitHub credentials into this repository, project data or Git remotes.

## Windows checkout

Windows path: `C:\Users\alexa\Repos\visual-workspace`.

Run in Windows PowerShell for the first time:

```powershell
git clone https://github.com/AlexPastukhh/visual-workspace.git "C:\Users\alexa\Repos\visual-workspace"
```

For subsequent synchronization of the default branch:

```powershell
git -C "C:\Users\alexa\Repos\visual-workspace" pull --ff-only origin main
```

Alternatively, run the optional Windows helper script once it is obtained locally. It will clone the missing folder or fast-forward an existing clean `main` checkout.

**Important:** the Linux and Windows directories are separate Git clones, not shared mounts. Changes created in Docker become available in Windows only after the appropriate reviewed branch is merged/pushed to the remote branch and Windows pulls it. GitHub Actions, antivirus checks and the Windows trusted admission pipeline are still future work; a successful download alone does not make a file safe to execute.

## Versioning

Track editable project files, sources, scripts and useful PNG previews. Exclude installed dependencies, caches and temporary renders. Large binary assets may later require Git LFS, but it is not needed for these small initial examples.

Work in feature branches; do not force push or change the default branch without an explicit release/merge decision.
