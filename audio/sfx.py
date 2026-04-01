from __future__ import annotations


class SfxController:
    def __init__(self, manager: object) -> None:
        self.manager = manager

    def play(self, sound_name: str) -> None:
        if not self.manager.enabled:
            return

        sound = self.manager.sounds.get(sound_name)
        if sound is not None:
            sound.play()

    def stop_all(self) -> None:
        if not self.manager.enabled:
            return

        for sound in self.manager.sounds.values():
            sound.stop()
