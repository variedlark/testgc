from __future__ import annotations

from typing import Any, Callable
import os
from pathlib import Path

import pygame

import config
from audio.manager import AudioManager
from core.clock import GameClock
from core.events import EventBus
from core.scene import BaseScene, SceneManager
from core.di import ServiceContainer
from core.hotreload import HotReloader
from core.plugin_manager import PluginManager
from data.high_scores import HighScoreService
from data.save_manager import SaveManager
from input.input_manager import InputManager
from levels.level_builder import LevelBuilder
from levels.loader import LevelLoader


class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.display.set_caption(config.WINDOW_TITLE)
        self.screen = pygame.display.set_mode(config.WINDOW_SIZE)

        self.clock = GameClock(config.FPS_LIMIT, config.FIXED_TIMESTEP, config.MAX_SUBSTEPS)
        self.event_bus = EventBus()
        self.scene_manager = SceneManager(self)
        self.input = InputManager()

        self.save_manager = SaveManager()
        self.save_data = self.save_manager.load()
        self.high_scores = HighScoreService(self.save_data)

        self.audio = AudioManager(self.save_data.get("settings", config.DEFAULT_SETTINGS))

        self.level_loader = LevelLoader()
        self.level_builder = LevelBuilder()
        self.levels = self.level_loader.load_all()

        # Dependency Injection container
        self.services = ServiceContainer()
        # Register core services so plugins/systems can resolve them
        self.services.register_singleton("event_bus", self.event_bus)
        self.services.register_singleton("game", self)
        self.services.register_singleton("clock", self.clock)
        self.services.register_singleton("scene_manager", self.scene_manager)
        self.services.register_singleton("input", self.input)
        self.services.register_singleton("audio", self.audio)
        self.services.register_singleton("save_manager", self.save_manager)
        self.services.register_singleton("high_scores", self.high_scores)
        self.services.register_singleton("level_loader", self.level_loader)
        self.services.register_singleton("level_builder", self.level_builder)

        # Plugin manager
        self.plugin_manager = PluginManager()
        self.services.register_singleton("plugin_manager", self.plugin_manager)
        # Load available plugins with the current game instance
        try:
            self.plugin_manager.load_all(self)
        except Exception:
            # Plugin errors should not prevent the game from running
            pass

        # Hot reloader (development only). Enable by setting env var TESTGC_HOTRELOAD=1
        self.hotreloader: HotReloader | None = None
        try:
            if os.environ.get("TESTGC_HOTRELOAD", "0").lower() in ("1", "true"):
                watch_paths: list[Path] = [self.plugin_manager.plugin_dir]
                if hasattr(config, "ASSETS_DIR"):
                    watch_paths.append(Path(config.ASSETS_DIR))
                if hasattr(config, "LEVELS_DIR"):
                    watch_paths.append(Path(config.LEVELS_DIR))

                self.hotreloader = HotReloader(watch_paths, self._hot_reload_cb)
                self.hotreloader.start()
        except Exception:
            # Don't fail startup for dev-only tooling
            self.hotreloader = None

        self._scene_registry: dict[str, Callable[[Game], BaseScene]] = {}
        self.running = True

    def register_scene(self, scene_key: str, scene_factory: Callable[[Game], BaseScene]) -> None:
        self._scene_registry[scene_key] = scene_factory

    def push_scene(self, scene_key: str, payload: dict[str, Any] | None = None) -> None:
        scene = self._build_scene(scene_key)
        self.scene_manager.push(scene, payload)

    def replace_scene(self, scene_key: str, payload: dict[str, Any] | None = None) -> None:
        scene = self._build_scene(scene_key)
        self.scene_manager.replace(scene, payload)

    def pop_scene(self) -> None:
        self.scene_manager.pop()
        if self.scene_manager.current is None:
            self.running = False

    def _build_scene(self, scene_key: str) -> BaseScene:
        if scene_key not in self._scene_registry:
            raise KeyError(f"Unknown scene key: {scene_key}")
        return self._scene_registry[scene_key](self)

    def add_attempt(self, level_id: str) -> int:
        self.save_manager.add_attempt(self.save_data, level_id)
        self.save_manager.save(self.save_data)
        stats = self.save_manager.level_stats(self.save_data, level_id)
        return int(stats["attempts"])

    def get_level_stats(self, level_id: str) -> dict[str, Any]:
        return self.save_manager.level_stats(self.save_data, level_id)

    def record_level_result(
        self,
        level_id: str,
        level_index: int,
        percent: float,
        elapsed: float,
        completed: bool,
    ) -> None:
        self.save_manager.record_result(self.save_data, level_id, level_index, percent, elapsed, completed)

    def is_level_unlocked(self, level_index: int) -> bool:
        return level_index < int(self.save_data.get("unlocked_levels", 1))

    def update_setting(self, key: str, value: Any) -> None:
        self.save_data.setdefault("settings", {})[key] = value
        if key == "music_volume":
            self.audio.set_music_volume(float(value))
        elif key == "sfx_volume":
            self.audio.set_sfx_volume(float(value))
        self.save_manager.set_settings(self.save_data, self.save_data["settings"])

    def run(self, start_scene_key: str) -> None:
        self.replace_scene(start_scene_key)

        while self.running and self.scene_manager.current is not None:
            frame_dt = self.clock.begin_frame()
            self.input.begin_frame()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                self.input.handle_event(event)

                current = self.scene_manager.current
                if current is not None:
                    current.handle_event(event)

            fixed_steps = self.clock.pop_fixed_steps()
            for _ in range(fixed_steps):
                current = self.scene_manager.current
                if current is not None:
                    current.fixed_update(config.FIXED_TIMESTEP)

            # Process any events scheduled for later emission by systems/plugins
            try:
                self.event_bus.process_pending()
            except Exception:
                # Keep game loop robust if event handlers misbehave
                pass

            current = self.scene_manager.current
            if current is not None:
                current.update(frame_dt, self.clock.alpha)
                current.render(self.screen)

            pygame.display.flip()

        self.shutdown()

    def shutdown(self) -> None:
        self.save_manager.save(self.save_data)
        self.audio.shutdown()
        # Stop hot-reloader if running
        try:
            if self.hotreloader is not None:
                self.hotreloader.stop()
        except Exception:
            pass

        # Unload plugins to allow clean reloads in dev
        try:
            if hasattr(self, "plugin_manager"):
                self.plugin_manager.unload_all()
        except Exception:
            pass
        pygame.quit()

    def _hot_reload_cb(self, path: Path, change_type: str = "modified") -> None:
        """Callback for HotReloader: reload plugins or emit asset-changed events."""
        try:
            # Plugins are stored in the plugin dir; if a .py changed there, reload it
            if path.suffix == ".py" and path.parent == self.plugin_manager.plugin_dir:
                try:
                    plugin_name = self.plugin_manager.module_name_for_path(path)
                    if change_type == "deleted":
                        self.plugin_manager.unload(plugin_name)
                        self.event_bus.emit_later(
                            "plugin.unloaded",
                            {"name": plugin_name, "path": str(path), "change": change_type},
                        )
                    else:
                        plugin_module = self.plugin_manager.reload(path, self)
                        self.event_bus.emit_later(
                            "plugin.reloaded",
                            {
                                "name": plugin_name,
                                "path": str(path),
                                "change": change_type,
                                "ok": plugin_module is not None,
                            },
                        )
                except Exception:
                    # Loading may fail; swallow to avoid breaking the reloader
                    pass
            elif path.suffix == ".json" and path.parent == Path(config.LEVELS_DIR):
                try:
                    self.levels = self.level_loader.load_all()
                    self.event_bus.emit_later(
                        "levels.reloaded",
                        {"count": len(self.levels), "path": str(path), "change": change_type},
                    )
                except Exception:
                    pass
            else:
                # Notify systems/plugins that an asset changed
                try:
                    self.event_bus.emit_later(
                        "hotreload.file_changed",
                        {"path": str(path), "change": change_type},
                    )
                except Exception:
                    pass
        except Exception:
            pass
