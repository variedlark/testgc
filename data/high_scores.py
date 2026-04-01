from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LevelScore:
    level_id: str
    attempts: int
    best_percent: float
    best_time: float | None
    completed: bool


class HighScoreService:
    def __init__(self, save_data: dict) -> None:
        self.save_data = save_data

    def get_level_score(self, level_id: str) -> LevelScore:
        stats = self.save_data.get("levels", {}).get(level_id, {})
        return LevelScore(
            level_id=level_id,
            attempts=int(stats.get("attempts", 0)),
            best_percent=float(stats.get("best_percent", 0.0)),
            best_time=stats.get("best_time"),
            completed=bool(stats.get("completed", False)),
        )
