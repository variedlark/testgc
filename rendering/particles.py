from __future__ import annotations

from dataclasses import dataclass
import random

import pygame


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    max_life: float
    size: float
    color: tuple[int, int, int]


class ParticleSystem:
    def __init__(self) -> None:
        self._particles: list[Particle] = []

    def clear(self) -> None:
        self._particles.clear()

    def spawn_trail(self, x: float, y: float, color: tuple[int, int, int]) -> None:
        spread = random.uniform(-18.0, 18.0)
        self._particles.append(
            Particle(
                x=x,
                y=y,
                vx=-random.uniform(60.0, 120.0),
                vy=spread,
                life=0.22,
                max_life=0.22,
                size=random.uniform(3.0, 6.0),
                color=color,
            )
        )

    def spawn_burst(self, x: float, y: float, color: tuple[int, int, int], count: int = 26) -> None:
        for _ in range(count):
            angle = random.uniform(0.0, 6.283)
            speed = random.uniform(100.0, 360.0)
            self._particles.append(
                Particle(
                    x=x,
                    y=y,
                    vx=speed * pygame.math.Vector2(1, 0).rotate_rad(angle).x,
                    vy=speed * pygame.math.Vector2(1, 0).rotate_rad(angle).y,
                    life=random.uniform(0.25, 0.7),
                    max_life=random.uniform(0.25, 0.7),
                    size=random.uniform(2.0, 6.0),
                    color=color,
                )
            )

    def update(self, dt: float) -> None:
        alive: list[Particle] = []
        for p in self._particles:
            p.life -= dt
            if p.life <= 0.0:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vy += 200.0 * dt
            alive.append(p)
        self._particles = alive

    def render(self, screen: pygame.Surface, camera_x: float) -> None:
        for p in self._particles:
            ratio = max(0.0, p.life / max(0.0001, p.max_life))
            alpha = int(255 * ratio)
            size = max(1, int(p.size * ratio))
            surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p.color, alpha), (size, size), size)
            screen.blit(surf, (int(p.x - camera_x - size), int(p.y - size)))
