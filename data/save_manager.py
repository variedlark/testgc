from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any

import config


class SaveManager:
    def __init__(self, save_file: Path | None = None) -> None:
        self.save_file = save_file or config.SAVE_FILE

    def _default_data(self) -> dict[str, Any]:
        return {
            "version": 1,
            "unlocked_levels": 1,
            "levels": {},
            "settings": deepcopy(config.DEFAULT_SETTINGS),
        }

    def load(self) -> dict[str, Any]:
        if not self.save_file.exists():
            data = self._default_data()
            self.save(data)
            return data

        try:
            with self.save_file.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            data = self._default_data()
            self.save(data)
            return data

        merged = self._default_data()
        merged.update({k: v for k, v in data.items() if k in merged})
        merged["settings"] = {**config.DEFAULT_SETTINGS, **data.get("settings", {})}
        if not isinstance(merged.get("levels"), dict):
            merged["levels"] = {}
        return merged

    def save(self, data: dict[str, Any]) -> None:
        self.save_file.parent.mkdir(parents=True, exist_ok=True)
        with self.save_file.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def level_stats(self, data: dict[str, Any], level_id: str) -> dict[str, Any]:
        levels = data.setdefault("levels", {})
        if level_id not in levels:
            levels[level_id] = {
                "attempts": 0,
                "best_percent": 0.0,
                "best_time": None,
                "completed": False,
            }
        return levels[level_id]

    def add_attempt(self, data: dict[str, Any], level_id: str) -> None:
        stats = self.level_stats(data, level_id)
        stats["attempts"] += 1

    def record_result(
        self,
        data: dict[str, Any],
        level_id: str,
        level_index: int,
        percent: float,
        elapsed: float,
        completed: bool,
    ) -> None:
        stats = self.level_stats(data, level_id)
        stats["best_percent"] = max(float(stats.get("best_percent", 0.0)), percent)

        previous_time = stats.get("best_time")
        if completed and (previous_time is None or elapsed < previous_time):
            stats["best_time"] = elapsed

        if completed:
            stats["completed"] = True
            data["unlocked_levels"] = max(int(data.get("unlocked_levels", 1)), level_index + 2)

        self.save(data)

    def set_settings(self, data: dict[str, Any], settings: dict[str, Any]) -> None:
        data["settings"] = {**config.DEFAULT_SETTINGS, **settings}
        self.save(data)
