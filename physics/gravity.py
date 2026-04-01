from __future__ import annotations

import config


def apply_gravity(velocity_y: float, gravity_direction: int, dt: float) -> float:
    gravity_direction = 1 if gravity_direction >= 0 else -1
    velocity_y += config.GRAVITY * gravity_direction * dt
    if gravity_direction > 0:
        return min(velocity_y, config.MAX_FALL_SPEED)
    return max(velocity_y, -config.MAX_FALL_SPEED)
