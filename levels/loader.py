from __future__ import annotations

import json
import re
from pathlib import Path

import config
from levels.level import Level, LevelObject


class LevelLoader:
    def __init__(self, level_dir: Path | None = None) -> None:
        self.level_dir = level_dir or config.LEVELS_DIR

    def discover_level_files(self) -> list[Path]:
        files = [p for p in self.level_dir.glob("*.json") if p.name != "__init__.json"]
        if files:
            return sorted(files, key=self._sort_key)

        # Backward-compatible fallback for explicit config ordering
        return [self.level_dir / filename for filename in config.LEVEL_FILE_ORDER]

    def load_all(self) -> list[Level]:
        levels: list[Level] = []
        for file_path in self.discover_level_files():
            levels.append(self.load_file(file_path))
        return levels

    def _sort_key(self, file_path: Path) -> tuple[int, str]:
        stem = file_path.stem
        match = re.search(r"(\d+)$", stem)
        if match:
            return (int(match.group(1)), file_path.name)
        return (10**9, file_path.name)

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
