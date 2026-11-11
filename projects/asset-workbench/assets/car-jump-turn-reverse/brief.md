# Jump, turn and reverse — 3D vehicle brief

Create a stylized, compact sports car and demonstrate one clearly readable movement sequence in Godot.

## Desired action

1. The car drives straight forward along the test lane.
2. It performs one visible jump with a clear takeoff, airborne arc and landing.
3. After landing, it turns smoothly through 180 degrees around its vertical axis.
4. It then continues travelling along the same world-space direction while moving backward relative to the car's new forward direction.

The last phase is intentional reverse motion: the car's forward vector should point opposite to its velocity. Do not interpret this as a facing bug.

## Visual direction

Use a polished low-poly sports/rally car with a deep turquoise body, dark trim, glass, visible wheels, headlights and a rear spoiler. The vehicle must remain recognizably upright and framed throughout the sequence. The test lane and environment should provide scale and motion context without distracting from the car.

## Acceptance intent

The forward phase has positive facing/velocity alignment. The jump has a distinct apex and a stable landing, and the landing pose is included in the jump capture before the turn begins. The 180-degree turn is continuous and finishes at the intended orientation. During reverse travel, facing/velocity alignment is negative and the wheels rotate consistently with backward travel. No teleport, hovering, ground penetration or wheel detachment.

## Review emphasis

Use perspective for readability and synchronized Front / Side / Top / Perspective samples at key moments. Inspect the jump arc, yaw progression, forward vector and velocity before and after the turn.
