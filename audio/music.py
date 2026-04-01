from __future__ import annotations

from pathlib import Path

import pygame


class MusicController:
    def __init__(self, manager: object) -> None:
        self.manager = manager
        self.current_track: str | None = None

    def play(self, track_name: str, loop: bool = True) -> None:
        if not self.manager.enabled:
            return

        key = Path(track_name).stem
        track_path = self.manager.music_tracks.get(key)
        if not track_path:
            return

        if self.current_track == key and pygame.mixer.music.get_busy():
            return

        pygame.mixer.music.load(str(track_path))
        pygame.mixer.music.set_volume(self.manager.music_volume)
        pygame.mixer.music.play(-1 if loop else 0)
        self.current_track = key

    def stop(self) -> None:
        if not self.manager.enabled:
            return
        pygame.mixer.music.stop()
        self.current_track = None
