from __future__ import annotations

import pygame

import config
from rendering.backgrounds import BackgroundRenderer
from scenes.base_scene import GameSceneBase


class LevelSelectScene(GameSceneBase):
    def __init__(self, game: object) -> None:
        super().__init__(game)
        self.selected = 0
        self.background = BackgroundRenderer()
        self.time_in_scene = 0.0

    def enter(self, payload: dict | None = None) -> None:
        del payload
        self.selected = 0
        self.time_in_scene = 0.0

    def fixed_update(self, dt: float) -> None:
        self.time_in_scene += dt

        if self.game.input.consume("menu_up"):
            self.selected = (self.selected - 1) % len(self.game.levels)
            self.game.audio.sfx.play("menu_move")

        if self.game.input.consume("menu_down"):
            self.selected = (self.selected + 1) % len(self.game.levels)
            self.game.audio.sfx.play("menu_move")

        if self.game.input.consume("confirm"):
            if self.game.is_level_unlocked(self.selected):
                self.game.audio.sfx.play("menu_select")
                self.game.replace_scene("game", {"level_index": self.selected})
            else:
                self.game.audio.sfx.play("death")

        if self.game.input.consume("back"):
            self.game.replace_scene("menu")

    def render(self, screen: pygame.Surface) -> None:
        self.background.draw(screen, self.time_in_scene * 80.0, "aqua", self.time_in_scene)
        self.draw_center_text(screen, "Select Level", 70, config.COLORS["text"], self.font_title)

        panel = pygame.Rect(220, 150, 840, 460)
        self.draw_panel(screen, panel)

        line_height = 78
        base_y = panel.y + 40

        for index, level in enumerate(self.game.levels):
            row_y = base_y + index * line_height
            selected = index == self.selected
            unlocked = self.game.is_level_unlocked(index)

            stats = self.game.get_level_stats(level.id)
            percent = int(stats.get("best_percent", 0.0) * 100)
            attempts = int(stats.get("attempts", 0))

            name_color = config.COLORS["success"] if selected and unlocked else config.COLORS["text"]
            if not unlocked:
                name_color = config.COLORS["text_dim"]

            prefix = "▶ " if selected else "  "
            title = f"{prefix}{index + 1}. {level.name}"
            left_surface = self.font_medium.render(title, True, name_color)
            screen.blit(left_surface, (panel.x + 34, row_y))

            if unlocked:
                right_text = f"{level.difficulty}  |  Best: {percent}%  |  Attempts: {attempts}"
                right_color = config.COLORS["text_dim"]
            else:
                right_text = "Locked"
                right_color = config.COLORS["danger"]

            right_surface = self.font_small.render(right_text, True, right_color)
            screen.blit(right_surface, (panel.x + 420, row_y + 9))

        hint = self.font_small.render("Enter to play, Esc to go back", True, config.COLORS["text_dim"])
        screen.blit(hint, ((config.SCREEN_WIDTH - hint.get_width()) // 2, config.SCREEN_HEIGHT - 44))
