from __future__ import annotations

from dataclasses import dataclass

import pygame

import config


@dataclass
class Block:
    x: float
    y: float
    width: int
    height: int

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    def draw(self, screen: pygame.Surface, camera_x: float) -> None:
        body = pygame.Rect(int(self.x - camera_x), int(self.y), int(self.width), int(self.height))
        glow = body.inflate(8, 8)
        pygame.draw.rect(screen, config.COLORS["ground_glow"], glow, border_radius=6)
        pygame.draw.rect(screen, config.COLORS["block"], body, border_radius=4)


@dataclass
class Spike:
    x: float
    y: float
    size: int = 40

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.size, self.size)

    def draw(self, screen: pygame.Surface, camera_x: float) -> None:
        left = int(self.x - camera_x)
        top = int(self.y)
        points = [
            (left, top + self.size),
            (left + self.size // 2, top),
            (left + self.size, top + self.size),
        ]
        pygame.draw.polygon(screen, config.COLORS["danger"], points)
        pygame.draw.polygon(screen, (255, 210, 220), points, 2)
