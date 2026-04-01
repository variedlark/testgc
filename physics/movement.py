from __future__ import annotations


def integrate_position(position_y: float, velocity_y: float, dt: float) -> float:
    return position_y + velocity_y * dt


def approach(value: float, target: float, speed: float, dt: float) -> float:
    if value < target:
        return min(target, value + speed * dt)
    return max(target, value - speed * dt)
