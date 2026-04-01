from __future__ import annotations

import json
from pathlib import Path

import config
from levels.level import Level, LevelObject


class LevelLoader:
    def __init__(self, level_dir: Path | None = None) -> None:
        self.level_dir = level_dir or config.LEVELS_DIR

    def load_all(self) -> list[Level]:
        levels: list[Level] = []
        for filename in config.LEVEL_FILE_ORDER:
            file_path = self.level_dir / filename
            levels.append(self.load_file(file_path))
        return levels

    def load_file(self, file_path: Path) -> Level:
        with file_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        objects = [
            LevelObject(
                type=obj["type"],
                x=float(obj.get("x", 0)),
                y=float(obj.get("y", 0)),
                width=obj.get("width"),
                height=obj.get("height"),
                size=obj.get("size"),
                kind=obj.get("kind"),
                value=obj.get("value"),
            )
            for obj in data.get("objects", [])
        ]

        return Level(
            id=data["id"],
            name=data["name"],
            difficulty=data.get("difficulty", "Easy"),
            music=data.get("music", "track_01"),
            speed=data.get("speed", "normal"),
            background_theme=data.get("background_theme", "default"),
            length=int(data.get("length", 3500)),
            objects=objects,
        )
