from __future__ import annotations

import pygame

import config
from rendering.backgrounds import BackgroundRenderer
from rendering.animations import pulse
from scenes.base_scene import GameSceneBase


class MenuScene(GameSceneBase):
    def __init__(self, game: object) -> None:
        super().__init__(game)
        self.options = ["Play", "Settings", "Quit"]
        self.selected = 0
        self.background = BackgroundRenderer()
        self.time_in_scene = 0.0

    def enter(self, payload: dict | None = None) -> None:
        del payload
        self.selected = 0
        self.time_in_scene = 0.0
        self.game.audio.music.play("track_01")

    def fixed_update(self, dt: float) -> None:
        self.time_in_scene += dt

        if self.game.input.consume("menu_up"):
            self.selected = (self.selected - 1) % len(self.options)
            self.game.audio.sfx.play("menu_move")

        if self.game.input.consume("menu_down"):
            self.selected = (self.selected + 1) % len(self.options)
            self.game.audio.sfx.play("menu_move")

        if self.game.input.consume("confirm") or self.game.input.mouse_just_pressed(1):
            self.game.audio.sfx.play("menu_select")
            option = self.options[self.selected]
            if option == "Play":
                self.game.replace_scene("level_select")
            elif option == "Settings":
                self.game.replace_scene("settings", {"overlay": False, "return_scene": "menu"})
            else:
                self.game.running = False

    def render(self, screen: pygame.Surface) -> None:
        self.background.draw(screen, self.time_in_scene * 120.0, "sunset", self.time_in_scene)

        self.draw_center_text(screen, config.WINDOW_TITLE, 120, config.COLORS["text"], self.font_large)
        subtitle = self.font_small.render("Rhythm platformer built in pure Python", True, config.COLORS["text_dim"])
        screen.blit(subtitle, ((config.SCREEN_WIDTH - subtitle.get_width()) // 2, 205))

        start_y = 300
        for index, option in enumerate(self.options):
            active = index == self.selected
            color = config.COLORS["success"] if active else config.COLORS["text"]
            scale = pulse(1.0, 1.1, self.time_in_scene, 4.0) if active else 1.0
            font = self.font_title if active else self.font_medium
            text_surface = font.render(option, True, color)
            if active:
                text_surface = pygame.transform.rotozoom(text_surface, 0.0, scale)
            x = (config.SCREEN_WIDTH - text_surface.get_width()) // 2
            y = start_y + index * 78
            screen.blit(text_surface, (x, y))

        hint = self.font_small.render("Arrows/WASD to navigate, Enter/Space to confirm", True, config.COLORS["text_dim"])
        screen.blit(hint, ((config.SCREEN_WIDTH - hint.get_width()) // 2, config.SCREEN_HEIGHT - 48))
