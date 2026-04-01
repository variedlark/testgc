from __future__ import annotations

import pygame


def scaled_rect(rect: pygame.Rect, scale: float) -> pygame.Rect:
    new_w = max(2, int(rect.width * scale))
    new_h = max(2, int(rect.height * scale))
    cx, cy = rect.center
    out = pygame.Rect(0, 0, new_w, new_h)
    out.center = (cx, cy)
    return out


def intersects(a: pygame.Rect, b: pygame.Rect) -> bool:
    return a.colliderect(b)


def resolve_block_collision(
    player_rect: pygame.Rect,
    previous_rect: pygame.Rect,
    block_rect: pygame.Rect,
    gravity_direction: int,
) -> tuple[pygame.Rect, str | None]:
    if not player_rect.colliderect(block_rect):
        return player_rect, None

    if gravity_direction >= 0:
        landed = previous_rect.bottom <= block_rect.top and player_rect.bottom >= block_rect.top
        if landed:
            player_rect.bottom = block_rect.top
            return player_rect, "landed"
    else:
        landed = previous_rect.top >= block_rect.bottom and player_rect.top <= block_rect.bottom
        if landed:
            player_rect.top = block_rect.bottom
            return player_rect, "landed"

    return player_rect, "crashed"
