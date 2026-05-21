from __future__ import annotations

from dataclasses import dataclass
import random
import pygame


Vec2 = pygame.math.Vector2


@dataclass
class Particle:
    pos: Vec2
    vel: Vec2
    life: float
    radius: float
    color: tuple[int, int, int]
    age: float = 0.0

    def update(self, dt: float, gravity: Vec2) -> bool:
        self.vel += gravity * dt
        self.pos += self.vel * dt
        self.age += dt
        return self.age < self.life

    @property
    def alpha(self) -> float:
        if self.life <= 0:
            return 0.0
        return max(0.0, 1.0 - self.age / self.life)


class ParticleEmitter:
    def __init__(self, pos: Vec2):
        self.pos = Vec2(pos)
        self.rate = 80.0
        self.burst_count = 30
        self.gravity = Vec2(0, 260)
        self.base_speed = 180.0
        self.spread = 2.6
        self.particles: list[Particle] = []
        self._emit_accumulator = 0.0

    def set_pos(self, pos: Vec2) -> None:
        self.pos.update(pos)

    def emit(self, count: int) -> None:
        for _ in range(count):
            angle = random.uniform(-self.spread, self.spread)
            speed = random.uniform(self.base_speed * 0.35, self.base_speed * 1.15)
            vel = Vec2(math_cos(angle) * speed, math_sin(angle) * speed)
            vel.x += random.uniform(-50, 50)
            vel.y -= random.uniform(60, 130)
            color = (
                random.randint(100, 255),
                random.randint(120, 255),
                random.randint(180, 255),
            )
            self.particles.append(
                Particle(
                    pos=Vec2(self.pos),
                    vel=vel,
                    life=random.uniform(1.0, 2.4),
                    radius=random.uniform(2.0, 4.5),
                    color=color,
                )
            )

    def burst(self) -> None:
        self.emit(self.burst_count)

    def update(self, dt: float) -> None:
        self._emit_accumulator += self.rate * dt
        while self._emit_accumulator >= 1.0:
            self._emit_accumulator -= 1.0
            self.emit(1)

        alive: list[Particle] = []
        for particle in self.particles:
            if particle.update(dt, self.gravity):
                alive.append(particle)
        self.particles = alive

    def draw(self, surface: pygame.Surface) -> None:
        for p in self.particles:
            radius = max(1, int(p.radius))
            color = tuple(min(255, int(channel * (0.35 + 0.65 * p.alpha))) for channel in p.color)
            pygame.draw.circle(surface, color, (int(p.pos.x), int(p.pos.y)), radius)


def math_sin(x: float) -> float:
    import math
    return math.sin(x)


def math_cos(x: float) -> float:
    import math
    return math.cos(x)
