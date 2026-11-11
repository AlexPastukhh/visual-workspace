# Multi-Actor Motion QA

Apply when multiple moving actors share a scene or their relative timing matters.

## Review

- Verify each actor independently: trajectory, speed, direction and facing.
- Verify relationships: vertical/horizontal ordering, separation, relative speed and timing.
- Check that phase changes occur when intended for each actor; do not assume actors are synchronized unless the brief says so.
- Look for unintended crossings, collisions, overlap, occlusion or one actor disappearing from the composition.
- Confirm that all actors remain visible/readable at the intended camera and scale.
- Check the combined scene as well as per-actor metrics. Isolated crops cannot prove the composition is correct.

## Evidence

Capture the whole scene for every sample. Record each actor's position, derived velocity and forward/facing vector. A per-actor crop or metric track is supplementary, never a replacement for the shared scene.

## GPT focus

Track each actor separately through time, then assess the composition and relationships. Cite timestamps and actor IDs. Distinguish an intentional crossing/formation change from an accidental one by checking the brief.
