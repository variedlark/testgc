from __future__ import annotations

from dataclasses import dataclass

import pygame

import config


@dataclass
class JumpOrb:
    x: float
    y: float
    radius: int = 16
    boost: float = config.ORB_BOOST_VELOCITY
    consumed: bool = False

    def rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

    def reset(self) -> None:
        self.consumed = False

    def try_activate(self, player_hitbox: pygame.Rect, jump_pressed: bool) -> bool:
        if self.consumed:
            return False
        if jump_pressed and self.rect().colliderect(player_hitbox):
            self.consumed = True
            return True
        return False

    def draw(self, screen: pygame.Surface, camera_x: float) -> None:
        center = (int(self.x - camera_x), int(self.y))
        color = config.COLORS["orb"] if not self.consumed else config.COLORS["text_dim"]
        pygame.draw.circle(screen, color, center, self.radius)
        pygame.draw.circle(screen, (255, 252, 221), center, self.radius - 6, 2)
