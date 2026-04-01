from __future__ import annotations

from dataclasses import dataclass, field

import config
from entities.obstacle import Block, Spike
from entities.orb import JumpOrb
from entities.pad import JumpPad
from entities.platform import Platform
from entities.portal import Portal
from levels.level import Level


@dataclass
class BuiltLevel:
    blocks: list[Block] = field(default_factory=list)
    spikes: list[Spike] = field(default_factory=list)
    platforms: list[Platform] = field(default_factory=list)
    orbs: list[JumpOrb] = field(default_factory=list)
    pads: list[JumpPad] = field(default_factory=list)
    portals: list[Portal] = field(default_factory=list)
    end_x: float = 0.0

    def reset_runtime_state(self) -> None:
        for orb in self.orbs:
            orb.reset()
        for pad in self.pads:
            pad.reset()
        for portal in self.portals:
            portal.reset()


class LevelBuilder:
    def build(self, level: Level) -> BuiltLevel:
        built = BuiltLevel()

        for obj in level.objects:
            if obj.type == "block":
                width = int(obj.width or 64)
                height = int(obj.height or 64)
                built.blocks.append(Block(obj.x, obj.y, width, height))
            elif obj.type == "spike":
                size = int(obj.size or 40)
                built.spikes.append(Spike(obj.x, obj.y, size))
            elif obj.type == "platform":
                width = int(obj.width or 64)
                height = int(obj.height or 32)
                built.platforms.append(Platform(obj.x, obj.y, width, height))
            elif obj.type == "orb":
                built.orbs.append(JumpOrb(obj.x, obj.y))
            elif obj.type == "pad":
                width = int(obj.width or 42)
                height = int(obj.height or 20)
                built.pads.append(JumpPad(obj.x, obj.y, width, height))
            elif obj.type == "portal":
                kind = obj.kind or "speed"
                value = obj.value or "normal"
                built.portals.append(Portal(obj.x, obj.y, kind, value))

        built.end_x = max(
            float(level.length),
            max([0.0] + [s.x + s.size for s in built.spikes] + [b.x + b.width for b in built.blocks] + [p.x + p.width for p in built.platforms]),
        ) + config.LEVEL_END_BUFFER

        return built
