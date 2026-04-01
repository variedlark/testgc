from __future__ import annotations

import pygame

import config
from core.scene import BaseScene


class GameSceneBase(BaseScene):
    def __init__(self, game: object) -> None:
        super().__init__(game)
        self.font_large = pygame.font.Font(config.FONT_MAIN, 68)
        self.font_title = pygame.font.Font(config.FONT_MAIN, 54)
        self.font_medium = pygame.font.Font(config.FONT_MAIN, 34)
        self.font_small = pygame.font.Font(config.FONT_MAIN, 24)

    def draw_center_text(
        self,
        screen: pygame.Surface,
        text: str,
        y: int,
        color: tuple[int, int, int],
        font: pygame.font.Font | None = None,
    ) -> None:
        used_font = font or self.font_medium
        surface = used_font.render(text, True, color)
        x = (config.SCREEN_WIDTH - surface.get_width()) // 2
        screen.blit(surface, (x, y))

    def draw_panel(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel, (12, 20, 42, 220), (0, 0, rect.width, rect.height), border_radius=14)
        pygame.draw.rect(panel, (129, 149, 207, 240), (0, 0, rect.width, rect.height), 2, border_radius=14)
        screen.blit(panel, rect.topleft)
