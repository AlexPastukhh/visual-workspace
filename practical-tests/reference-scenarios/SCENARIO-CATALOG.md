# Reference scenario catalog — flexible facets

The family RS identifies reproducible reference-driven creation tests. Existing SC01–SC05 production and SV01–SV03 read-only review scenarios remain untouched. Group by **independent facets**, not a permanent split into everyday versus advanced: reference operation, modality, visual style, fidelity target, source count, estimated difficulty, real observed cost and risks. Multiple facets may describe one scenario.

| ID | Operation and what it probes | Input | Modality | Initial difficulty hypothesis | Planned work units | Status |
| --- | --- | --- | --- | --- | --- | --- |
| [RS01](RS01/01-work.md) | Closely reproduce shape, palette, light and composition | One bomb icon | 2D SVG → Godot | 2/5 | 1 | NOT RUN |
| [RS02](RS02/01-work.md) | Recreate then change a limited region, preserve geometry | One top-down crate | 2D SVG → Godot | 3/5 | 2 | NOT RUN |
| [RS03](RS03/01-work.md) | Combine two inputs into one coherent original; then adjust material | Two isometric wooden objects | 2D SVG → Godot | 4/5 | 2 | NOT RUN |
| [RS04](RS04/01-work.md) | Infer editable 3D geometry from one 2D view, validate multiple cameras | One isometric crate | Blender → glTF → Godot | 5/5 | 1 | NOT RUN |

Difficulty numbers are provisional **task challenge descriptors**, not measured performance scores. The same task can be difficult for fidelity but easy for technical export, or the reverse. Add/free-form tags and comments as new scenarios arise, without mandatory exclusive categories. Suggested tags: reference:fidelity; reference:targeted-edit; reference:multi-source; reference:2d-to-3d; source:vector; source:blender; output:godot; priority:regression; cost:short/medium/long. Add scenario tags independently.

## Selective testing strategy

A scenario is **chosen for a reason**, not run by default because it exists. For a quick changed-tool smoke check, choose one relevant lightweight existing SC case or RS01. For geometry-preservation edits, run RS02; for multi-reference fusion changes, RS03; for 3D modeling/perspective improvements, RS04. For a significant release, compose a small temporary suite covering distinct operations and include an easier fixed control case. Run costly complex tests selectively; do not always retest the entire catalog.

Record suite selection rationale, exact accepted Git commit, scenario prompt hashes, reference SHA256, model/config, runId, per-unit work time, time-to-first-useful-preview, independent first-pass outcome, final outcome and repair/evaluator overhead. Compare identical scenarios across changes and versions; do not silently treat different references or prompts as the same controlled regression. No numeric pass percentages from one correlated scenario chat.
