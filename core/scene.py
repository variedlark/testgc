from __future__ import annotations

from typing import Any, Optional


class BaseScene:
    def __init__(self, game: Any) -> None:
        self.game = game

    def enter(self, payload: Optional[dict[str, Any]] = None) -> None:
        del payload

    def exit(self) -> None:
        return

    def on_cover(self) -> None:
        return

    def on_reveal(self) -> None:
        return

    def handle_event(self, event: Any) -> None:
        del event

    def fixed_update(self, dt: float) -> None:
        del dt

    def update(self, frame_dt: float, alpha: float) -> None:
        del frame_dt
        del alpha

    def render(self, screen: Any) -> None:
        del screen


class SceneManager:
    def __init__(self, game: Any) -> None:
        self.game = game
        self._stack: list[BaseScene] = []

    @property
    def current(self) -> Optional[BaseScene]:
        if not self._stack:
            return None
        return self._stack[-1]

    def push(self, scene: BaseScene, payload: Optional[dict[str, Any]] = None) -> None:
        if self.current:
            self.current.on_cover()
        self._stack.append(scene)
        scene.enter(payload)

    def replace(self, scene: BaseScene, payload: Optional[dict[str, Any]] = None) -> None:
        while self._stack:
            self._stack.pop().exit()
        self._stack.append(scene)
        scene.enter(payload)

    def pop(self) -> Optional[BaseScene]:
        if not self._stack:
            return None

        scene = self._stack.pop()
        scene.exit()
        if self.current:
            self.current.on_reveal()
        return scene
