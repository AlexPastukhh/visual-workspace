# 3D Vehicle QA

Apply to cars and other vehicles with meaningful movement, steering, jumping or suspension.

## Review

- Compare vehicle forward vector with velocity. A negative alignment may be correct for reversing; judge against the brief and current phase.
- Verify yaw/steering changes are continuous and reach the intended angle. Look for snaps, overshoot or rotation around the wrong axis.
- Check that a 180-degree turn actually changes vehicle orientation, not merely its travel path.
- During reverse motion, verify that the vehicle travels backward relative to its own forward direction.
- Jump: readable takeoff, coherent arc, appropriate attitude, clear apex and stable landing; no hovering or teleport.
- Wheels: rotation direction/speed should agree with travel when wheel animation is part of the asset.
- Suspension/body: no unexplained bouncing, clipping, wheel separation or ground penetration.
- Keep the vehicle framed and recognizable throughout the sequence.

## Evidence

Use perspective frames for overall readability and synchronized Front / Side / Top / Perspective samples at key moments. Record position, derived velocity, forward vector, yaw, vertical height and wheel rotation where available.

## GPT focus

Check the sequence before and after the turn. Explicitly distinguish forward travel, backward travel and a vehicle that has simply changed its world-space route. Cite frame/timestamp and relevant transform evidence.
