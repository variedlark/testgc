from __future__ import annotations

from dataclasses import dataclass

import pygame

import config


@dataclass
class Platform:
    x: float
    y: float
    width: int
    height: int

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))

    def draw(self, screen: pygame.Surface, camera_x: float) -> None:
        body = pygame.Rect(int(self.x - camera_x), int(self.y), int(self.width), int(self.height))
        pygame.draw.rect(screen, config.COLORS["panel_alt"], body, border_radius=4)
