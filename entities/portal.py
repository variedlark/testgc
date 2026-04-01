from __future__ import annotations

from dataclasses import dataclass

import pygame

import config


@dataclass
class Portal:
    x: float
    y: float
    kind: str
    value: str
    width: int = 48
    height: int = 110
    triggered: bool = False

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def reset(self) -> None:
        self.triggered = False

    def try_trigger(self, player_hitbox: pygame.Rect) -> bool:
        if self.triggered:
            return False
        if self.rect().colliderect(player_hitbox):
            self.triggered = True
            return True
        return False

    def draw(self, screen: pygame.Surface, camera_x: float) -> None:
        body = pygame.Rect(int(self.x - camera_x), int(self.y), self.width, self.height)
        color = config.COLORS["portal_speed"] if self.kind == "speed" else config.COLORS["portal_gravity"]
        pygame.draw.ellipse(screen, color, body, 4)
        pygame.draw.ellipse(screen, color, body.inflate(-14, -14), 3)
