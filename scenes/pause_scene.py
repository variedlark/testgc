from __future__ import annotations

import pygame

import config
from scenes.base_scene import GameSceneBase


class PauseScene(GameSceneBase):
    def __init__(self, game: object) -> None:
        super().__init__(game)
        self.options = ["Resume", "Retry", "Settings", "Level Select", "Main Menu"]
        self.selected = 0
        self.level_index = 0

    def enter(self, payload: dict | None = None) -> None:
        payload = payload or {}
        self.level_index = int(payload.get("level_index", 0))
        self.selected = 0

    def fixed_update(self, dt: float) -> None:
        del dt

        if self.game.input.consume("menu_up"):
            self.selected = (self.selected - 1) % len(self.options)
            self.game.audio.sfx.play("menu_move")

        if self.game.input.consume("menu_down"):
            self.selected = (self.selected + 1) % len(self.options)
            self.game.audio.sfx.play("menu_move")

        if self.game.input.consume("confirm"):
            self.game.audio.sfx.play("menu_select")
            self._activate(self.options[self.selected])

        if self.game.input.consume("pause") or self.game.input.consume("back"):
            self.game.pop_scene()

    def _activate(self, option: str) -> None:
        if option == "Resume":
            self.game.pop_scene()
        elif option == "Retry":
            self.game.replace_scene("game", {"level_index": self.level_index})
        elif option == "Settings":
            self.game.push_scene("settings", {"overlay": True})
        elif option == "Level Select":
            self.game.replace_scene("level_select")
        elif option == "Main Menu":
            self.game.replace_scene("menu")

    def render(self, screen: pygame.Surface) -> None:
        if len(self.game.scene_manager._stack) >= 2:
            self.game.scene_manager._stack[-2].render(screen)

        shade = pygame.Surface(config.WINDOW_SIZE, pygame.SRCALPHA)
        shade.fill((0, 0, 0, 160))
        screen.blit(shade, (0, 0))

        panel = pygame.Rect(360, 170, 560, 390)
        self.draw_panel(screen, panel)

        self.draw_center_text(screen, "Paused", panel.y + 28, config.COLORS["text"], self.font_title)

        for index, option in enumerate(self.options):
            color = config.COLORS["success"] if index == self.selected else config.COLORS["text"]
            line = self.font_medium.render(option, True, color)
            x = panel.x + (panel.width - line.get_width()) // 2
            y = panel.y + 115 + index * 50
            screen.blit(line, (x, y))
