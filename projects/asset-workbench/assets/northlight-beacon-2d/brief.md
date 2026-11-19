# Northlight navigation beacon — static 2D icon

**Purpose:** a small, clear navigation-console emblem for the first real UC-VIS-009 owner review and public GitHub PNG Issue E2E.

**Scope:** editable 256×256 SVG vector (transparent corners), imported in Godot Asset Workbench as a static 2D sprite. No animation, interaction or gameplay integration is claimed. Scene preview uses the maintained neutral 2D QA stage; this is an inspection asset, not an exported game.

**Design:** crisp dark blue octagonal badge, luminous teal compass rose with clearly visible cardinal ticks and one coral-pink north pointer. The dark base should remain legible against the QA stage; ring, needle, core and outline must stay distinct. No external images/fonts.

**Acceptance:** SVG loads in Godot; whole badge is visible and centred in a real 1280×720 capture; no clipping, missing facets or import errors; transparent corners are preserved. No motion is expected across the six QA frames. Review visible appearance of the actual PNG, not the SVG text alone.

**Owner review:** The original v1 is preserved in GitHub Issue #5. On 2026-11-19, the owner requested any visible change for v2; the north needle, cardinal tick and center jewel change from amber to coral-pink. The typed `append_visual_revision` operation uses scoped ALLOW and adds a v2 comment to the same Issue. This public GitHub Issue is for visual feedback, not proof of source merge or Windows gameplay. Preserve editable SVG and QA config in an exact Git commit before publishing.
