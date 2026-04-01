from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class LevelObject:
    type: str
    x: float
    y: float
    width: int | None = None
    height: int | None = None
    size: int | None = None
    kind: str | None = None
    value: str | None = None


@dataclass
class Level:
    id: str
    name: str
    difficulty: str
    music: str
    speed: str
    background_theme: str
    length: int
    objects: list[LevelObject] = field(default_factory=list)
