from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

import pygame

import config
from audio.music import MusicController
from audio.sfx import SfxController


class AudioManager:
    def __init__(self, settings: dict) -> None:
        self.enabled = False
        self.music_volume = float(settings.get("music_volume", config.DEFAULT_SETTINGS["music_volume"]))
        self.sfx_volume = float(settings.get("sfx_volume", config.DEFAULT_SETTINGS["sfx_volume"]))
        self.music_tracks: dict[str, Path] = {}
        self.sounds: dict[str, pygame.mixer.Sound] = {}

        self.music = MusicController(self)
        self.sfx = SfxController(self)

        self._init_mixer()
        if self.enabled:
            self._prepare_audio_files()
            self._load_audio_files()
            self.apply_volumes()

    def _init_mixer(self) -> None:
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.enabled = True
        except pygame.error:
            self.enabled = False

    def _prepare_audio_files(self) -> None:
        config.GENERATED_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

        self._ensure_track(
            config.GENERATED_AUDIO_DIR / "track_01.wav",
            bpm=140,
            pattern=[
                (392.0, 0.5),
                (440.0, 0.5),
                (523.25, 1.0),
                (659.25, 1.0),
                (523.25, 1.0),
                (440.0, 1.0),
                (392.0, 1.0),
                (329.63, 1.0),
            ],
            loops=12,
        )

        self._ensure_track(
            config.GENERATED_AUDIO_DIR / "track_02.wav",
            bpm=148,
            pattern=[
                (523.25, 0.5),
                (587.33, 0.5),
                (659.25, 0.5),
                (783.99, 0.5),
                (698.46, 1.0),
                (659.25, 1.0),
                (587.33, 1.0),
                (523.25, 1.0),
            ],
            loops=12,
        )

        self._ensure_track(
            config.GENERATED_AUDIO_DIR / "track_03.wav",
            bpm=160,
            pattern=[
                (329.63, 0.5),
                (392.0, 0.5),
                (493.88, 0.5),
                (523.25, 0.5),
                (659.25, 0.5),
                (587.33, 0.5),
                (523.25, 0.5),
                (493.88, 0.5),
                (440.0, 1.0),
                (392.0, 1.0),
                (329.63, 1.0),
                (261.63, 1.0),
            ],
            loops=10,
        )

        self._ensure_sfx(config.GENERATED_AUDIO_DIR / "jump.wav", [(670.0, 0.08), (870.0, 0.06)], "square")
        self._ensure_sfx(config.GENERATED_AUDIO_DIR / "death.wav", [(420.0, 0.08), (260.0, 0.12), (130.0, 0.16)], "saw")
        self._ensure_sfx(config.GENERATED_AUDIO_DIR / "orb.wav", [(820.0, 0.05), (980.0, 0.05)], "triangle")
        self._ensure_sfx(config.GENERATED_AUDIO_DIR / "pad.wav", [(580.0, 0.04), (780.0, 0.06)], "sine")
        self._ensure_sfx(config.GENERATED_AUDIO_DIR / "complete.wav", [(392.0, 0.08), (523.0, 0.08), (659.0, 0.08)], "sine")
        self._ensure_sfx(config.GENERATED_AUDIO_DIR / "menu_move.wav", [(500.0, 0.03)], "triangle")
        self._ensure_sfx(config.GENERATED_AUDIO_DIR / "menu_select.wav", [(700.0, 0.05)], "triangle")

    def _load_audio_files(self) -> None:
        for path in config.GENERATED_AUDIO_DIR.glob("track_*.wav"):
            self.music_tracks[path.stem] = path

        mapping = {
            "jump": "jump.wav",
            "death": "death.wav",
            "orb": "orb.wav",
            "pad": "pad.wav",
            "complete": "complete.wav",
            "menu_move": "menu_move.wav",
            "menu_select": "menu_select.wav",
        }

        for key, filename in mapping.items():
            wav_path = config.GENERATED_AUDIO_DIR / filename
            if wav_path.exists():
                self.sounds[key] = pygame.mixer.Sound(str(wav_path))

    def apply_volumes(self) -> None:
        if not self.enabled:
            return

        pygame.mixer.music.set_volume(self.music_volume)
        for sound in self.sounds.values():
            sound.set_volume(self.sfx_volume)

    def set_music_volume(self, value: float) -> None:
        self.music_volume = max(0.0, min(1.0, value))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume)

    def set_sfx_volume(self, value: float) -> None:
        self.sfx_volume = max(0.0, min(1.0, value))
        if self.enabled:
            for sound in self.sounds.values():
                sound.set_volume(self.sfx_volume)

    def shutdown(self) -> None:
        if not self.enabled:
            return
        pygame.mixer.music.stop()
        pygame.mixer.stop()

    def _ensure_track(self, path: Path, bpm: int, pattern: list[tuple[float, float]], loops: int) -> None:
        if path.exists():
            return

        beat_seconds = 60.0 / bpm
        sample_rate = 44100
        amplitude = 0.35
        data = bytearray()

        for _ in range(loops):
            for frequency, beats in pattern:
                duration = beat_seconds * beats
                sample_count = int(duration * sample_rate)
                for i in range(sample_count):
                    t = i / sample_rate
                    env = min(1.0, i / max(1, int(sample_rate * 0.01)))
                    if sample_count - i < int(sample_rate * 0.02):
                        env *= (sample_count - i) / max(1, int(sample_rate * 0.02))

                    if frequency <= 1.0:
                        value = 0.0
                    else:
                        melody = math.sin(2.0 * math.pi * frequency * t)
                        harmony = 0.45 * math.sin(2.0 * math.pi * (frequency * 0.5) * t)
                        pulse = 0.18 * (1.0 if math.sin(2.0 * math.pi * frequency * t) >= 0 else -1.0)
                        value = (melody + harmony + pulse) / 1.63

                    sample = int(32767 * amplitude * env * value)
                    packed = struct.pack("<h", sample)
                    data.extend(packed)
                    data.extend(packed)

        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(2)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(bytes(data))

    def _ensure_sfx(self, path: Path, sequence: list[tuple[float, float]], waveform: str) -> None:
        if path.exists():
            return

        sample_rate = 44100
        amplitude = 0.45
        data = bytearray()

        for frequency, duration in sequence:
            sample_count = int(duration * sample_rate)
            for i in range(sample_count):
                t = i / sample_rate
                progress = i / max(1, sample_count)
                env = max(0.0, 1.0 - progress)

                if waveform == "square":
                    wave_value = 1.0 if math.sin(2.0 * math.pi * frequency * t) >= 0.0 else -1.0
                elif waveform == "triangle":
                    wave_value = 2.0 * abs(2.0 * ((frequency * t) % 1.0) - 1.0) - 1.0
                elif waveform == "saw":
                    wave_value = 2.0 * ((frequency * t) % 1.0) - 1.0
                else:
                    wave_value = math.sin(2.0 * math.pi * frequency * t)

                sample = int(32767 * amplitude * env * wave_value)
                packed = struct.pack("<h", sample)
                data.extend(packed)
                data.extend(packed)

        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(2)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(bytes(data))
