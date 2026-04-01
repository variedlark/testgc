from __future__ import annotations

import pygame

import config
from rendering.backgrounds import BackgroundRenderer
from scenes.base_scene import GameSceneBase


class SettingsScene(GameSceneBase):
    def __init__(self, game: object) -> None:
        super().__init__(game)
        self.background = BackgroundRenderer()
        self.selected = 0
        self.overlay = False
        self.return_scene = "menu"
        self.time_in_scene = 0.0

    def enter(self, payload: dict | None = None) -> None:
        payload = payload or {}
        self.overlay = bool(payload.get("overlay", False))
        self.return_scene = str(payload.get("return_scene", "menu"))
        self.selected = 0
        self.time_in_scene = 0.0

    def fixed_update(self, dt: float) -> None:
        self.time_in_scene += dt

        if self.game.input.consume("menu_up"):
            self.selected = (self.selected - 1) % 4
            self.game.audio.sfx.play("menu_move")

        if self.game.input.consume("menu_down"):
            self.selected = (self.selected + 1) % 4
            self.game.audio.sfx.play("menu_move")

        if self.game.input.consume("menu_left"):
            self._apply_delta(-0.05)

        if self.game.input.consume("menu_right"):
            self._apply_delta(0.05)

        if self.game.input.consume("confirm"):
            self._confirm_selected()

        if self.game.input.consume("back"):
            self._go_back()

    def _apply_delta(self, delta: float) -> None:
        settings = self.game.save_data["settings"]

        if self.selected == 0:
            value = float(settings.get("music_volume", config.DEFAULT_SETTINGS["music_volume"])) + delta
            self.game.update_setting("music_volume", max(0.0, min(1.0, value)))
            self.game.audio.sfx.play("menu_move")
        elif self.selected == 1:
            value = float(settings.get("sfx_volume", config.DEFAULT_SETTINGS["sfx_volume"])) + delta
            self.game.update_setting("sfx_volume", max(0.0, min(1.0, value)))
            self.game.audio.sfx.play("menu_move")

    def _confirm_selected(self) -> None:
        if self.selected == 2:
            current = bool(self.game.save_data["settings"].get("show_fps", False))
            self.game.update_setting("show_fps", not current)
            self.game.audio.sfx.play("menu_select")
        elif self.selected == 3:
            self.game.audio.sfx.play("menu_select")
            self._go_back()

    def _go_back(self) -> None:
        if self.overlay:
            self.game.pop_scene()
        else:
            self.game.replace_scene(self.return_scene)

    def render(self, screen: pygame.Surface) -> None:
        if self.overlay and len(self.game.scene_manager._stack) >= 2:
            self.game.scene_manager._stack[-2].render(screen)
            dim = pygame.Surface(config.WINDOW_SIZE, pygame.SRCALPHA)
            dim.fill((0, 0, 0, 140))
            screen.blit(dim, (0, 0))
        else:
            self.background.draw(screen, self.time_in_scene * 70.0, "default", self.time_in_scene)

        panel = pygame.Rect(300, 170, 680, 380)
        self.draw_panel(screen, panel)
        self.draw_center_text(screen, "Settings", panel.y + 24, config.COLORS["text"], self.font_title)

        settings = self.game.save_data["settings"]
        rows = [
            f"Music Volume: {int(float(settings.get('music_volume', 0.0)) * 100)}%",
            f"SFX Volume: {int(float(settings.get('sfx_volume', 0.0)) * 100)}%",
            f"Show FPS: {'On' if settings.get('show_fps', False) else 'Off'}",
            "Back",
        ]

        start_y = panel.y + 120
        for index, text in enumerate(rows):
            color = config.COLORS["success"] if index == self.selected else config.COLORS["text"]
            line = self.font_medium.render(text, True, color)
            x = panel.x + 80
            y = start_y + index * 62
            screen.blit(line, (x, y))

        hint = self.font_small.render("Left/Right adjust, Enter confirm, Esc back", True, config.COLORS["text_dim"])
        screen.blit(hint, (panel.x + (panel.width - hint.get_width()) // 2, panel.bottom - 38))
