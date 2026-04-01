from __future__ import annotations

from dataclasses import dataclass

import pygame

import config


@dataclass
class JumpPad:
    x: float
    y: float
    width: int = 42
    height: int = 20
    boost: float = config.PAD_BOOST_VELOCITY
    cooldown: float = 0.0

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def reset(self) -> None:
        self.cooldown = 0.0

    def fixed_update(self, dt: float) -> None:
        self.cooldown = max(0.0, self.cooldown - dt)

    def try_activate(self, player_hitbox: pygame.Rect) -> bool:
        if self.cooldown > 0.0:
            return False
        if self.rect().colliderect(player_hitbox):
            self.cooldown = 0.20
            return True
        return False

    def draw(self, screen: pygame.Surface, camera_x: float) -> None:
        body = pygame.Rect(int(self.x - camera_x), int(self.y), self.width, self.height)
        pygame.draw.rect(screen, config.COLORS["pad"], body, border_radius=5)
        pygame.draw.rect(screen, (220, 255, 235), body.inflate(-6, -6), border_radius=4)
