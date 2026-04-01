import pygame


class GameClock:
    def __init__(self, fps_limit: int, fixed_timestep: float, max_substeps: int) -> None:
        self._clock = pygame.time.Clock()
        self.fps_limit = fps_limit
        self.fixed_timestep = fixed_timestep
        self.max_substeps = max_substeps
        self.accumulator = 0.0

    def begin_frame(self) -> float:
        frame_dt = min(self._clock.tick(self.fps_limit) / 1000.0, 0.2)
        self.accumulator += frame_dt
        return frame_dt

    def pop_fixed_steps(self) -> int:
        steps = 0
        while self.accumulator >= self.fixed_timestep and steps < self.max_substeps:
            self.accumulator -= self.fixed_timestep
            steps += 1

        if steps >= self.max_substeps:
            self.accumulator = 0.0

        return steps

    @property
    def alpha(self) -> float:
        if self.fixed_timestep <= 0.0:
            return 0.0
        return self.accumulator / self.fixed_timestep

    @property
    def fps(self) -> float:
        return self._clock.get_fps()
