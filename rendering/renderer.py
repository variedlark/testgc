from __future__ import annotations

import pygame

import config


class GameRenderer:
    def __init__(self) -> None:
        self.font_small = pygame.font.Font(config.FONT_MAIN, 22)
        self.font_medium = pygame.font.Font(config.FONT_MAIN, 30)

    def draw_player(self, screen: pygame.Surface, screen_rect: pygame.Rect, rotation: float) -> None:
        cube = pygame.Surface((screen_rect.width, screen_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(cube, config.COLORS["player"], (0, 0, screen_rect.width, screen_rect.height), border_radius=8)
        pygame.draw.rect(cube, (226, 255, 255), (7, 7, screen_rect.width - 14, screen_rect.height - 14), 2, border_radius=6)

        eye_size = 6
        pygame.draw.rect(cube, (11, 22, 43), (10, 13, eye_size, eye_size), border_radius=2)
        pygame.draw.rect(cube, (11, 22, 43), (screen_rect.width - 16, 13, eye_size, eye_size), border_radius=2)

        rotated = pygame.transform.rotozoom(cube, -rotation, 1.0)
        target = rotated.get_rect(center=screen_rect.center)
        screen.blit(rotated, target)

    def draw_progress(self, screen: pygame.Surface, percent: float) -> None:
        bar_w = 340
        bar_h = 14
        x = (config.SCREEN_WIDTH - bar_w) // 2
        y = 18
        pygame.draw.rect(screen, (20, 27, 50), (x, y, bar_w, bar_h), border_radius=7)
        fill = int(bar_w * max(0.0, min(1.0, percent)))
        pygame.draw.rect(screen, config.COLORS["success"], (x, y, fill, bar_h), border_radius=7)
        label = self.font_small.render(f"{int(percent * 100)}%", True, config.COLORS["text"])
        screen.blit(label, (x + bar_w + 12, y - 3))

    def draw_hud(self, screen: pygame.Surface, level_name: str, attempts: int, show_fps: bool, fps: float) -> None:
        left = self.font_medium.render(level_name, True, config.COLORS["text"])
        screen.blit(left, (22, 16))

        attempts_surface = self.font_small.render(f"Attempts: {attempts}", True, config.COLORS["text_dim"])
        screen.blit(attempts_surface, (24, 54))

        if show_fps:
            fps_surface = self.font_small.render(f"FPS: {fps:0.0f}", True, config.COLORS["text_dim"])
            screen.blit(fps_surface, (config.SCREEN_WIDTH - 120, 20))
