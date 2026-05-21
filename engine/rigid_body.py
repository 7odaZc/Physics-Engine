from __future__ import annotations

from dataclasses import dataclass
import math
import random
import pygame


Vec2 = pygame.math.Vector2


@dataclass
class RigidCircle:
    pos: Vec2
    vel: Vec2
    radius: float
    mass: float
    angle: float = 0.0
    angular_velocity: float = 0.0
    restitution: float = 0.72
    color: tuple[int, int, int] = (255, 255, 255)
    kind: str = "neutral"
    hp: int = 1
    alive: bool = True
    age: float = 0.0
    lifetime: float | None = None
    static: bool = False

    @property
    def inv_mass(self) -> float:
        return 0.0 if self.mass <= 0 else 1.0 / self.mass


class RigidBodyWorld:
    def __init__(self, size=(1200, 800)):
        self.width, self.height = size
        self.gravity = Vec2(0, 900)
        self.friction = 0.985
        self.spin_decay = 0.995
        self.bodies: list[RigidCircle] = []
        self.contacts: list[tuple[RigidCircle, RigidCircle]] = []
        self.reset()

    def reset(self) -> None:
        self.bodies = []
        self.contacts = []
        for i in range(6):
            self.spawn(Vec2(180 + i * 70, 120), radius=18 + i * 2, mass=1.0 + i * 0.35, randomize=True)
        self.spawn(Vec2(900, 150), radius=26, mass=3.5, randomize=True)

    def clear(self) -> None:
        self.bodies = []

    def spawn(
        self,
        pos: Vec2,
        radius: float = 22,
        mass: float | None = None,
        randomize: bool = False,
        vel: Vec2 | None = None,
        color: tuple[int, int, int] | None = None,
        kind: str = "neutral",
        hp: int = 1,
        restitution: float = 0.72,
        angular_velocity: float | None = None,
        lifetime: float | None = None,
        static: bool = False,
    ) -> RigidCircle:
        if mass is None:
            mass = max(1.0, radius / 10.0)
        if vel is None:
            vel = Vec2(0, 0)
            if randomize:
                vel = Vec2(random.uniform(-120, 120), random.uniform(-50, 50))
        if color is None:
            color = (
                random.randint(120, 255),
                random.randint(120, 255),
                random.randint(120, 255),
            )
        if angular_velocity is None:
            angular_velocity = random.uniform(-2.5, 2.5)

        body = RigidCircle(
            pos=Vec2(pos),
            vel=Vec2(vel),
            radius=radius,
            mass=mass,
            color=color,
            restitution=restitution,
            angular_velocity=angular_velocity,
            kind=kind,
            hp=hp,
            lifetime=lifetime,
            static=static,
        )
        self.bodies.append(body)
        return body

    def apply_explosion(self, center: Vec2, strength: float = 320.0) -> None:
        for body in self.bodies:
            delta = body.pos - center
            dist = delta.length()
            if dist < 1:
                dist = 1
            impulse = delta.normalize() * (strength / dist)
            body.vel += impulse

    def update(self, dt: float) -> None:
        for body in self.bodies:
            if not body.alive:
                continue

            body.age += dt
            if body.lifetime is not None and body.age >= body.lifetime:
                body.alive = False
                continue

            if body.static:
                body.vel.update(0, 0)
                body.angular_velocity = 0.0
                continue

            body.vel += self.gravity * dt
            body.pos += body.vel * dt
            body.angle += body.angular_velocity * dt
            body.vel *= self.friction
            body.angular_velocity *= self.spin_decay

            # Walls and ground.
            if body.pos.x - body.radius < 0:
                body.pos.x = body.radius
                body.vel.x = abs(body.vel.x) * body.restitution
                body.angular_velocity += body.vel.y * 0.002
            if body.pos.x + body.radius > self.width:
                body.pos.x = self.width - body.radius
                body.vel.x = -abs(body.vel.x) * body.restitution
                body.angular_velocity -= body.vel.y * 0.002
            if body.pos.y - body.radius < 0:
                body.pos.y = body.radius
                body.vel.y = abs(body.vel.y) * body.restitution
            if body.pos.y + body.radius > self.height - 50:
                body.pos.y = self.height - 50 - body.radius
                body.vel.y = -abs(body.vel.y) * body.restitution
                body.vel.x *= 0.98
                body.angular_velocity += body.vel.x * 0.001

        self.contacts = []
        self._resolve_circle_collisions()
        self.bodies = [body for body in self.bodies if body.alive]

    def _should_collide(self, a: RigidCircle, b: RigidCircle) -> bool:
        """Determine if two bodies should collide based on their kinds."""
        kinds = (a.kind, b.kind)
        
        # Prevent enemy bullets from colliding with each other
        if kinds == ("enemy_bullet", "enemy_bullet"):
            return False
        # Prevent player bullets from colliding with each other
        if kinds == ("player_bullet", "player_bullet"):
            return False
        # Prevent player bullets from colliding with the player
        if kinds in (("player_bullet", "player"), ("player", "player_bullet")):
            return False
        # Prevent enemy bullets from colliding with enemies
        if kinds in (("enemy_bullet", "enemy"), ("enemy", "enemy_bullet")):
            return False
        # Prevent enemies from colliding with each other
        if kinds == ("enemy", "enemy"):
            return False
        # All other collisions are allowed
        return True

    def _resolve_circle_collisions(self) -> None:
        for i in range(len(self.bodies)):
            a = self.bodies[i]
            if not a.alive:
                continue
            for j in range(i + 1, len(self.bodies)):
                b = self.bodies[j]
                if not b.alive:
                    continue

                # Check if these bodies should collide
                if not self._should_collide(a, b):
                    continue

                delta = b.pos - a.pos
                dist = delta.length()
                min_dist = a.radius + b.radius
                if dist == 0:
                    delta = Vec2(1, 0)
                    dist = 1
                if dist >= min_dist:
                    continue

                normal = delta / dist
                penetration = min_dist - dist

                # Record the contact for game logic
                self.contacts.append((a, b))

                inv_mass_sum = a.inv_mass + b.inv_mass
                if inv_mass_sum == 0:
                    # Both bodies are static, no physics response needed
                    continue

                # Positional correction.
                correction = normal * (penetration / inv_mass_sum) * 0.8
                if a.inv_mass > 0:
                    a.pos -= correction * a.inv_mass
                if b.inv_mass > 0:
                    b.pos += correction * b.inv_mass

                rel_vel = b.vel - a.vel
                vel_along_normal = rel_vel.dot(normal)
                if vel_along_normal > 0:
                    continue

                restitution = min(a.restitution, b.restitution)
                impulse_mag = -(1 + restitution) * vel_along_normal
                impulse_mag /= inv_mass_sum
                impulse = normal * impulse_mag

                if a.inv_mass > 0:
                    a.vel -= impulse * a.inv_mass
                if b.inv_mass > 0:
                    b.vel += impulse * b.inv_mass

                tangent = Vec2(-normal.y, normal.x)
                tangent_speed = rel_vel.dot(tangent)
                a.angular_velocity -= tangent_speed * 0.002
                b.angular_velocity += tangent_speed * 0.002

    def draw(self, surface: pygame.Surface) -> None:
        ground_y = self.height - 50
        pygame.draw.rect(surface, (35, 35, 45), pygame.Rect(0, ground_y, self.width, 50))
        pygame.draw.line(surface, (160, 160, 180), (0, ground_y), (self.width, ground_y), 3)

        for body in self.bodies:
            pygame.draw.circle(surface, body.color, (int(body.pos.x), int(body.pos.y)), int(body.radius))