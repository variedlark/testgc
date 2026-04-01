from __future__ import annotations

from collections import defaultdict

import pygame


class InputManager:
    def __init__(self) -> None:
        self._keys_for_action = {
            "jump": {pygame.K_SPACE, pygame.K_UP, pygame.K_w},
            "menu_up": {pygame.K_UP, pygame.K_w},
            "menu_down": {pygame.K_DOWN, pygame.K_s},
            "menu_left": {pygame.K_LEFT, pygame.K_a},
            "menu_right": {pygame.K_RIGHT, pygame.K_d},
            "confirm": {pygame.K_RETURN, pygame.K_SPACE},
            "back": {pygame.K_ESCAPE, pygame.K_BACKSPACE},
            "pause": {pygame.K_ESCAPE},
        }
        self._held: set[str] = set()
        self._just_pressed: set[str] = set()
        self._mouse_buttons = defaultdict(bool)
        self._just_mouse_pressed: set[int] = set()

    def begin_frame(self) -> None:
        self._just_pressed.clear()
        self._just_mouse_pressed.clear()

    def handle_event(self, event: pygame.event.Event) -> None:
        # Some pygame builds/events may not include a `repeat` attribute.
        # Use getattr() with a default to remain compatible.
        if event.type == pygame.KEYDOWN and not getattr(event, "repeat", False):
            for action, keys in self._keys_for_action.items():
                if event.key in keys:
                    self._held.add(action)
                    self._just_pressed.add(action)

        if event.type == pygame.KEYUP:
            for action, keys in self._keys_for_action.items():
                if event.key in keys and action in self._held:
                    self._held.remove(action)

        if event.type == pygame.MOUSEBUTTONDOWN:
            self._mouse_buttons[event.button] = True
            self._just_mouse_pressed.add(event.button)

        if event.type == pygame.MOUSEBUTTONUP:
            self._mouse_buttons[event.button] = False

    def is_pressed(self, action: str) -> bool:
        return action in self._held

    def was_pressed(self, action: str) -> bool:
        return action in self._just_pressed

    def consume(self, action: str) -> bool:
        if action in self._just_pressed:
            self._just_pressed.remove(action)
            return True
        return False

    def mouse_just_pressed(self, button: int = 1) -> bool:
        return button in self._just_mouse_pressed
