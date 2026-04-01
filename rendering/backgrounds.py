from __future__ import annotations

import pygame

import config


THEMES = {
    "sunset": ((255, 145, 109), (83, 42, 122), (43, 18, 60)),
    "aqua": ((111, 226, 255), (41, 96, 171), (20, 39, 80)),
    "storm": ((197, 215, 255), (68, 73, 128), (27, 31, 67)),
    "reactor": ((255, 178, 121), (146, 42, 67), (58, 16, 35)),
    "midnight": ((172, 194, 255), (63, 53, 130), (21, 17, 47)),
    "default": ((130, 180, 255), (39, 68, 135), (16, 29, 64)),
}


class BackgroundRenderer:
    def draw(self, screen: pygame.Surface, camera_x: float, theme: str, run_time: float) -> None:
        top_color, mid_color, bottom_color = THEMES.get(theme, THEMES["default"])

        height = screen.get_height()
        width = screen.get_width()

        for y in range(height):
            blend = y / max(1, height - 1)
            if blend < 0.5:
                local = blend / 0.5
                color = (
                    int(top_color[0] + (mid_color[0] - top_color[0]) * local),
                    int(top_color[1] + (mid_color[1] - top_color[1]) * local),
                    int(top_color[2] + (mid_color[2] - top_color[2]) * local),
                )
            else:
                local = (blend - 0.5) / 0.5
                color = (
                    int(mid_color[0] + (bottom_color[0] - mid_color[0]) * local),
                    int(mid_color[1] + (bottom_color[1] - mid_color[1]) * local),
                    int(mid_color[2] + (bottom_color[2] - mid_color[2]) * local),
                )
            pygame.draw.line(screen, color, (0, y), (width, y))

        # Parallax ribbons.
        for i in range(6):
            ribbon_y = int(120 + i * 80 + (run_time * 16 * (i + 1)) % 40)
            speed_factor = 0.1 + i * 0.05
            offset = int((camera_x * speed_factor) % (width + 320))
            rect = pygame.Rect(-320 + offset, ribbon_y, width // 2, 12)
            shade = min(255, 95 + i * 18)
            pygame.draw.rect(screen, (shade, shade, min(255, shade + 30)), rect, border_radius=8)

        # Moving glow circles for depth.
        for i in range(7):
            px = int((camera_x * (0.03 + i * 0.01) + i * 190) % (width + 320)) - 160
            py = 120 + i * 70
            radius = 28 + i * 4
            alpha = 45
            glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow, (255, 255, 255, alpha), (radius, radius), radius)
            screen.blit(glow, (px, py))

        ground_rect = pygame.Rect(0, config.GROUND_Y, width, config.SCREEN_HEIGHT - config.GROUND_Y)
        pygame.draw.rect(screen, config.COLORS["ground"], ground_rect)
        pygame.draw.line(screen, config.COLORS["ground_glow"], (0, config.GROUND_Y), (width, config.GROUND_Y), 3)
