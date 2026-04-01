from __future__ import annotations

import math


def ease_out_cubic(value: float) -> float:
    inv = 1.0 - max(0.0, min(1.0, value))
    return 1.0 - inv * inv * inv


def ping_pong(time_value: float, speed: float = 1.0) -> float:
    phase = (time_value * speed) % 2.0
    if phase <= 1.0:
        return phase
    return 2.0 - phase


def pulse(min_value: float, max_value: float, time_value: float, speed: float = 1.0) -> float:
    t = (math.sin(time_value * speed) + 1.0) * 0.5
    return min_value + (max_value - min_value) * t
