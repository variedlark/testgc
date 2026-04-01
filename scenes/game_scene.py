from __future__ import annotations

import pygame

import config
from entities.player import Player
from physics.collision import resolve_block_collision
from rendering.backgrounds import BackgroundRenderer
from rendering.camera import Camera
from rendering.particles import ParticleSystem
from rendering.renderer import GameRenderer
from scenes.base_scene import GameSceneBase


class GameScene(GameSceneBase):
    def __init__(self, game: object) -> None:
        super().__init__(game)
        self.background = BackgroundRenderer()
        self.renderer = GameRenderer()
        self.camera = Camera()
        self.particles = ParticleSystem()

        self.level_index = 0
        self.level = None
        self.built_level = None
        self.player = Player()
        self.scroll_speed = config.BASE_SCROLL_SPEED
        self.attempts = 0

        self.state = "playing"
        self.transition_timer = 0.0
        self.run_time = 0.0
        self.elapsed = 0.0
        self.final_percent = 0.0

    def enter(self, payload: dict | None = None) -> None:
        payload = payload or {}
        self.level_index = max(0, min(int(payload.get("level_index", 0)), len(self.game.levels) - 1))
        self.level = self.game.levels[self.level_index]
        self.built_level = self.game.level_builder.build(self.level)
        self.built_level.reset_runtime_state()

        self.player.reset(config.PLAYER_SPAWN_Y)
        self.camera.reset()
        self.particles.clear()

        speed_name = self.level.speed
        self.scroll_speed = config.BASE_SCROLL_SPEED * config.SPEED_MULTIPLIERS.get(speed_name, 1.0)
        self.attempts = self.game.add_attempt(self.level.id)

        self.state = "playing"
        self.transition_timer = 0.0
        self.run_time = 0.0
        self.elapsed = 0.0
        self.final_percent = 0.0

        self.game.audio.music.play(self.level.music)

    def fixed_update(self, dt: float) -> None:
        self.particles.update(dt)

        if self.state != "playing":
            self.transition_timer -= dt
            if self.transition_timer <= 0.0:
                self._to_result_scene()
            return

        if self.game.input.consume("pause"):
            self.game.push_scene("pause", {"level_index": self.level_index})
            return

        jump_pressed = self.game.input.consume("jump") or self.game.input.mouse_just_pressed(1)
        if jump_pressed and self.player.on_ground:
            self.player.jump()
            self.game.audio.sfx.play("jump")

        previous_camera_x = self.camera.x
        previous_rect = self.player.world_rect(previous_camera_x)

        self.camera.advance(self.scroll_speed, dt)
        self.player.on_ground = False
        self.player.fixed_update(dt)
        self.player.clamp_to_base_surface()

        player_rect = self.player.world_rect(self.camera.x)

        solids = self.built_level.blocks + self.built_level.platforms
        for solid in solids:
            solid_rect = solid.rect()
            if solid_rect.right < self.camera.x - 200:
                continue
            if solid_rect.left > self.camera.x + config.SCREEN_WIDTH + 200:
                continue

            player_rect, outcome = resolve_block_collision(
                player_rect,
                previous_rect,
                solid_rect,
                self.player.gravity_direction,
            )
            if outcome == "landed":
                self.player.on_ground = True
                self.player.velocity_y = 0.0
                self.player.y = player_rect.y
            elif outcome == "crashed":
                self.player.y = player_rect.y
                self._trigger_death()
                return

        self.player.y = player_rect.y
        player_hitbox = self.player.world_hitbox(self.camera.x)

        for spike in self.built_level.spikes:
            if spike.rect().right < self.camera.x - 80:
                continue
            if spike.rect().left > self.camera.x + config.SCREEN_WIDTH + 80:
                continue
            if player_hitbox.colliderect(spike.rect()):
                self._trigger_death()
                return

        for orb in self.built_level.orbs:
            if orb.try_activate(player_hitbox, jump_pressed):
                self.player.force_boost(orb.boost)
                self.game.audio.sfx.play("orb")

        for pad in self.built_level.pads:
            pad.fixed_update(dt)
            if pad.try_activate(player_hitbox):
                self.player.force_boost(pad.boost)
                self.game.audio.sfx.play("pad")

        for portal in self.built_level.portals:
            if portal.try_trigger(player_hitbox):
                if portal.kind == "speed":
                    multiplier = config.SPEED_MULTIPLIERS.get(portal.value, 1.0)
                    self.scroll_speed = config.BASE_SCROLL_SPEED * multiplier
                elif portal.kind == "gravity":
                    self.player.invert_gravity()
                self.game.audio.sfx.play("orb")

        trail_x = self.camera.x + config.PLAYER_START_X + self.player.size * 0.5
        trail_y = self.player.y + self.player.size * 0.5
        self.particles.spawn_trail(trail_x, trail_y, config.COLORS["player_trail"])

        self.run_time += dt
        self.elapsed += dt

        if self.player.is_out_of_bounds():
            self._trigger_death()
            return

        if self.progress() >= 1.0:
            self._complete_level()

    def update(self, frame_dt: float, alpha: float) -> None:
        del frame_dt
        del alpha

    def progress(self) -> float:
        if not self.built_level or self.built_level.end_x <= 0:
            return 0.0
        player_world_x = self.camera.x + config.PLAYER_START_X
        return max(0.0, min(1.0, player_world_x / self.built_level.end_x))

    def _trigger_death(self) -> None:
        if self.state != "playing":
            return

        self.state = "dead"
        self.transition_timer = 1.0
        self.final_percent = self.progress()

        burst_x = self.camera.x + config.PLAYER_START_X + self.player.size / 2
        burst_y = self.player.y + self.player.size / 2
        self.particles.spawn_burst(burst_x, burst_y, config.COLORS["danger"], 30)

        self.game.audio.sfx.play("death")
        self.game.record_level_result(
            self.level.id,
            self.level_index,
            self.final_percent,
            self.elapsed,
            False,
        )

    def _complete_level(self) -> None:
        if self.state != "playing":
            return

        self.state = "completed"
        self.transition_timer = 1.0
        self.final_percent = 1.0

        self.game.audio.sfx.play("complete")
        self.game.record_level_result(
            self.level.id,
            self.level_index,
            self.final_percent,
            self.elapsed,
            True,
        )

    def _to_result_scene(self) -> None:
        self.game.replace_scene(
            "game_over",
            {
                "completed": self.state == "completed",
                "level_index": self.level_index,
                "level_name": self.level.name,
                "percent": self.final_percent,
                "elapsed": self.elapsed,
            },
        )

    def render(self, screen: pygame.Surface) -> None:
        self.background.draw(screen, self.camera.x, self.level.background_theme, self.run_time)

        for obj in self.built_level.blocks:
            if obj.x + obj.width >= self.camera.x - 100 and obj.x <= self.camera.x + config.SCREEN_WIDTH + 100:
                obj.draw(screen, self.camera.x)

        for obj in self.built_level.platforms:
            if obj.x + obj.width >= self.camera.x - 100 and obj.x <= self.camera.x + config.SCREEN_WIDTH + 100:
                obj.draw(screen, self.camera.x)

        for spike in self.built_level.spikes:
            if spike.x + spike.size >= self.camera.x - 100 and spike.x <= self.camera.x + config.SCREEN_WIDTH + 100:
                spike.draw(screen, self.camera.x)

        for orb in self.built_level.orbs:
            if orb.x + 60 >= self.camera.x - 100 and orb.x <= self.camera.x + config.SCREEN_WIDTH + 100:
                orb.draw(screen, self.camera.x)

        for pad in self.built_level.pads:
            if pad.x + pad.width >= self.camera.x - 100 and pad.x <= self.camera.x + config.SCREEN_WIDTH + 100:
                pad.draw(screen, self.camera.x)

        for portal in self.built_level.portals:
            if portal.x + portal.width >= self.camera.x - 100 and portal.x <= self.camera.x + config.SCREEN_WIDTH + 100:
                portal.draw(screen, self.camera.x)

        self.particles.render(screen, self.camera.x)

        player_world_rect = self.player.world_rect(self.camera.x)
        player_screen_rect = player_world_rect.move(-int(self.camera.x), 0)
        self.renderer.draw_player(screen, player_screen_rect, self.player.rotation)

        self.renderer.draw_progress(screen, self.progress())
        self.renderer.draw_hud(
            screen,
            self.level.name,
            self.attempts,
            bool(self.game.save_data["settings"].get("show_fps", False)),
            self.game.clock.fps,
        )

        if self.state == "dead":
            text = self.font_title.render("Crashed", True, config.COLORS["danger"])
            screen.blit(text, ((config.SCREEN_WIDTH - text.get_width()) // 2, 250))
        elif self.state == "completed":
            text = self.font_title.render("Completed", True, config.COLORS["success"])
            screen.blit(text, ((config.SCREEN_WIDTH - text.get_width()) // 2, 250))
