from __future__ import annotations

import pygame

import config
from physics.collision import scaled_rect
from physics.gravity import apply_gravity
from physics.movement import integrate_position


class Player:
    def __init__(self) -> None:
        self.size = config.PLAYER_SIZE
        self.spawn_y = config.PLAYER_SPAWN_Y
        self.reset(self.spawn_y)

    def reset(self, spawn_y: float) -> None:
        self.y = spawn_y
        self.velocity_y = 0.0
        self.gravity_direction = 1
        self.rotation = 0.0
        self.on_ground = True
        self.alive = True

    def world_rect(self, camera_x: float) -> pygame.Rect:
        return pygame.Rect(int(camera_x + config.PLAYER_START_X), int(self.y), self.size, self.size)

    def world_hitbox(self, camera_x: float) -> pygame.Rect:
        return scaled_rect(self.world_rect(camera_x), config.PLAYER_HITBOX_SCALE)

    def fixed_update(self, dt: float) -> float:
        previous_y = self.y
        self.velocity_y = apply_gravity(self.velocity_y, self.gravity_direction, dt)
        self.y = integrate_position(self.y, self.velocity_y, dt)

        if self.on_ground:
            self.rotation = round(self.rotation / 90.0) * 90.0
        else:
            self.rotation = (self.rotation + config.ROTATION_SPEED * dt * self.gravity_direction) % 360

        return previous_y

    def clamp_to_base_surface(self) -> None:
        if self.gravity_direction >= 0:
            if self.y + self.size >= config.GROUND_Y:
                self.y = config.GROUND_Y - self.size
                self.velocity_y = 0.0
                self.on_ground = True
        else:
            if self.y <= config.CEILING_Y:
                self.y = config.CEILING_Y
                self.velocity_y = 0.0
                self.on_ground = True

    def jump(self, power: float = config.JUMP_VELOCITY) -> None:
        self.velocity_y = -power * self.gravity_direction
        self.on_ground = False

    def force_boost(self, power: float) -> None:
        self.velocity_y = -power * self.gravity_direction
        self.on_ground = False

    def invert_gravity(self) -> None:
        self.gravity_direction *= -1
        self.velocity_y = 0.0
        self.on_ground = False

    def is_out_of_bounds(self) -> bool:
        return self.y > config.SCREEN_HEIGHT + 200 or self.y + self.size < -200
