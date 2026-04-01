from __future__ import annotations

import pygame

import config
from rendering.backgrounds import BackgroundRenderer
from scenes.base_scene import GameSceneBase


class GameOverScene(GameSceneBase):
    def __init__(self, game: object) -> None:
        super().__init__(game)
        self.background = BackgroundRenderer()
        self.completed = False
        self.level_index = 0
        self.level_name = ""
        self.percent = 0.0
        self.elapsed = 0.0
        self.options: list[str] = []
        self.selected = 0
        self.time_in_scene = 0.0

    def enter(self, payload: dict | None = None) -> None:
        payload = payload or {}
        self.completed = bool(payload.get("completed", False))
        self.level_index = int(payload.get("level_index", 0))
        self.level_name = str(payload.get("level_name", "Unknown Level"))
        self.percent = float(payload.get("percent", 0.0))
        self.elapsed = float(payload.get("elapsed", 0.0))
        self.time_in_scene = 0.0

        self.options = []
        if self.completed and self.level_index + 1 < len(self.game.levels):
            self.options.append("Next Level")
        self.options.extend(["Retry", "Level Select", "Main Menu"])
        self.selected = 0

    def fixed_update(self, dt: float) -> None:
        self.time_in_scene += dt

        if self.game.input.consume("menu_up"):
            self.selected = (self.selected - 1) % len(self.options)
            self.game.audio.sfx.play("menu_move")

        if self.game.input.consume("menu_down"):
            self.selected = (self.selected + 1) % len(self.options)
            self.game.audio.sfx.play("menu_move")

        if self.game.input.consume("confirm"):
            self.game.audio.sfx.play("menu_select")
            self._activate(self.options[self.selected])

        if self.game.input.consume("back"):
            self.game.replace_scene("level_select")

    def _activate(self, option: str) -> None:
        if option == "Next Level":
            self.game.replace_scene("game", {"level_index": self.level_index + 1})
        elif option == "Retry":
            self.game.replace_scene("game", {"level_index": self.level_index})
        elif option == "Level Select":
            self.game.replace_scene("level_select")
        elif option == "Main Menu":
            self.game.replace_scene("menu")

    def render(self, screen: pygame.Surface) -> None:
        theme = "sunset" if self.completed else "storm"
        self.background.draw(screen, self.time_in_scene * 90.0, theme, self.time_in_scene)

        panel = pygame.Rect(300, 140, 680, 430)
        self.draw_panel(screen, panel)

        title = "Level Complete" if self.completed else "Try Again"
        title_color = config.COLORS["success"] if self.completed else config.COLORS["danger"]
        self.draw_center_text(screen, title, panel.y + 28, title_color, self.font_title)

        details = [
            f"{self.level_name}",
            f"Progress: {int(self.percent * 100)}%",
            f"Time: {self.elapsed:0.2f}s",
        ]

        for index, text in enumerate(details):
            line = self.font_medium.render(text, True, config.COLORS["text"])
            x = panel.x + (panel.width - line.get_width()) // 2
            y = panel.y + 110 + index * 44
            screen.blit(line, (x, y))

        start_y = panel.y + 250
        for index, option in enumerate(self.options):
            color = config.COLORS["success"] if index == self.selected else config.COLORS["text"]
            line = self.font_medium.render(option, True, color)
            x = panel.x + (panel.width - line.get_width()) // 2
            y = start_y + index * 48
            screen.blit(line, (x, y))
