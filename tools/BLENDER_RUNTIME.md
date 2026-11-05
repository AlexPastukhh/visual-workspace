# Blender runtime in Fortis Repo

## Runtime

- Blender 5.2.3 LTS, official Linux x86_64 archive.
- Official archive: `https://download.blender.org/release/Blender5.2/blender-5.2.3-linux-x64.tar.xz`
- Official SHA-256: `78486c018b4443efe5e75ab54c290ed8c15abafd249b862c2c9ce2530a918eec`
- Executable: `.local-tools/blender-5.2.3-linux-x64/blender`
- Local Debian runtime libraries: `.local-tools/system-libs/usr/lib/x86_64-linux-gnu`
- Launcher: `./tools/blender.sh`

The downloaded archive was checked against the Blender Foundation checksum manifest. Missing Debian 12 runtime libraries were downloaded from `deb.debian.org`, checked against the SHA-256 values in Debian's Bookworm package index, and extracted under `.local-tools/system-libs`. Nothing was installed into `/usr`, no package database was changed, and no Docker settings were changed.

`.local-tools/` is excluded by `.gitignore`; do not commit the Blender binary, downloaded archive, Debian packages or local runtime libraries.

## First full cycle

The first test opened the existing editable project `projects/visual-mvp/output/3d/scene_v2.blend`, added a chimney and doorstep, saved a new `.blend`, rendered a PNG, and read the PNG back through Fortis Repo.

```bash
./tools/blender.sh --background projects/visual-mvp/output/3d/scene_v2.blend \
  --python-exit-code 11 --python tools/blender_runtime_smoke.py -- \
  projects/visual-mvp/output/3d fortis_house_fortis_v1
```

The second iteration opened the first saved result, added window trim, mullions and a brass door handle, saved a second editable `.blend`, rendered another PNG and read it back through Fortis Repo.

```bash
./tools/blender.sh --background projects/visual-mvp/output/3d/fortis_house_fortis_v1.blend \
  --python-exit-code 11 --python tools/blender_refine_v2.py -- \
  projects/visual-mvp/output/3d fortis_house_fortis_v2
```

## Current limitations

- This is Blender background automation, not interactive GUI control.
- CPU-only Cycles rendering; the container has two CPU cores and no GPU device.
- The launcher uses the shared binary/runtime under `.local-tools/`, but keeps Blender user config, scripts, datafiles, extensions, XDG state and temporary files under the current Worktree's ignored `.fortis-state/blender/`.
- The current 4 GiB RAM limit is enough for this small house scene; complex scenes may need more memory.
- Krita execution in this container is not established yet. Godot 4.7.2 is available through `tools/godot.sh`; the tested 2D/3D animation project and its test commands are documented in `projects/game-animation-mvp/README.md`.
