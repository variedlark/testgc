from __future__ import annotations


class Camera:
    def __init__(self) -> None:
        self.x = 0.0

    def reset(self) -> None:
        self.x = 0.0

    def advance(self, speed: float, dt: float) -> None:
        self.x += speed * dt
