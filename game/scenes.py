from __future__ import annotations

import random
import pygame

from engine.particle import ParticleEmitter
from engine.mass_spring import MassSpringSystem
from engine.pbd import PBDChain
from engine.rigid_body import RigidBodyWorld
from engine.kinematics import TwoLinkArm


Vec2 = pygame.math.Vector2


class SceneBase:
    title = "Scene"

    def handle_event(self, event: pygame.event.Event) -> None:
        pass

    def update(self, dt: float, mouse_pos: Vec2, mouse_buttons: tuple[int, int, int], keys) -> None:
        pass

    def draw(self, surface: pygame.Surface) -> None:
        pass

    def reset(self) -> None:
        pass

    def overlay_text(self) -> list[str]:
        return []


class BallSmashScene(SceneBase):
    title = "Star Shooter"

    def __init__(self, size):
        self.size = size
        self.reset()

    def reset(self) -> None:
        self.world = RigidBodyWorld(size=self.size)
        self.world.clear()
        self.world.gravity = Vec2(0, 0)
        self.world.friction = 1.0
        self.world.spin_decay = 1.0

        self.emitters: list[ParticleEmitter] = []
        self.background_color = (9, 12, 24)

        self.score = 0
        self.lives = 3
        self.game_state = "playing"  # playing, win, lose

        self.player_y = self.size[1] - 92
        self.player_x = self.size[0] / 2
        self.player_speed = 460
        self.player_body = self.world.spawn(
            Vec2(self.player_x, self.player_y),
            radius=18,
            mass=0,
            vel=Vec2(0, 0),
            color=(85, 220, 255),
            kind="player",
            hp=1,
            restitution=0.2,
            static=True,
        )

        self.shoot_cooldown = 0.0
        self.reload_timer = 0.0
        self.ammo_max = 20
        self.ammo = self.ammo_max
        self.enemy_fire_timer = 1.0
        self.enemy_fire_interval = 2.2
        self._spawn_wave()

    def _spawn_wave(self) -> None:
        self.world.bodies = [b for b in self.world.bodies if b.kind == "player"]

        cols = 7
        rows = 4
        start_x = 150
        end_x = self.size[0] - 150
        step_x = (end_x - start_x) / (cols - 1)
        xs = [start_x + i * step_x for i in range(cols)]

        start_y = 120
        step_y = 66
        palette = [
            (255, 90, 140),
            (255, 175, 75),
            (95, 220, 255),
            (175, 255, 115),
            (205, 120, 255),
        ]

        for row in range(rows):
            for col, x in enumerate(xs):
                if row == rows - 1 and col in (0, cols - 1):
                    continue
                hp = 1
                color = palette[(row + col) % len(palette)]
                self.world.spawn(
                    Vec2(x, start_y + row * step_y),
                    radius=19 + (row % 2),
                    mass=0,
                    vel=Vec2(0, 0),
                    color=color,
                    kind="enemy",
                    hp=hp,
                    restitution=0.25,
                    static=True,
                )

        self.reload_timer = 0.0
        self.ammo = self.ammo_max
        self.enemy_fire_timer = 1.0
        self.enemy_fire_interval = 2.2

    def _add_burst(self, pos: Vec2, count: int = 16) -> None:
        emitter = ParticleEmitter(Vec2(pos))
        emitter.rate = 0
        emitter.burst_count = count
        emitter.base_speed = 180
        emitter.spread = 3.1
        emitter.gravity = Vec2(0, 240)
        emitter.burst()
        self.emitters.append(emitter)

    def _draw_background(self, surface: pygame.Surface) -> None:
        surface.fill(self.background_color)
        # Subtle stars only, no gradients or stripe changes.
        for i in range(90):
            x = (i * 127) % self.size[0]
            y = (i * 67) % self.size[1]
            c = 55 + (i * 11) % 70
            pygame.draw.circle(surface, (c, c, c + 8), (x, y), 1)

    def _shoot(self) -> None:
        if self.game_state != "playing" or self.shoot_cooldown > 0 or self.reload_timer > 0:
            return
        if self.ammo <= 0:
            self.reload_timer = 1.0
            return

        muzzle = Vec2(self.player_x, self.player_y - 28)
        self.world.spawn(
            muzzle,
            radius=6,
            mass=0.2,
            vel=Vec2(0, -620),
            color=(255, 245, 160),
            kind="player_bullet",
            hp=1,
            restitution=0.2,
            lifetime=2.0,
            static=False,
        )
        self._add_burst(muzzle + Vec2(0, -4), 6)
        self.ammo -= 1
        self.shoot_cooldown = 0.12
        if self.ammo <= 0:
            self.reload_timer = 0.6

    def _enemy_fire(self) -> None:
        enemies = [b for b in self.world.bodies if b.kind == "enemy" and b.alive]
        if not enemies:
            return
        # All enemies shoot together.
        for shooter in enemies:
            pos = Vec2(shooter.pos.x, shooter.pos.y + shooter.radius + 10)
            self.world.spawn(
                pos,
                radius=6,
                mass=0.25,
                vel=Vec2(0, 180),
                color=(255, 90, 90),
                kind="enemy_bullet",
                hp=1,
                restitution=0.2,
                lifetime=3.0,
            )
        self._add_burst(Vec2(self.size[0] / 2, 86), 12)

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._shoot()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self._shoot()
            elif event.key == pygame.K_r and self.game_state != "playing":
                self.reset()
            elif event.key == pygame.K_RETURN and self.game_state != "playing":
                self.reset()

    def update(self, dt: float, mouse_pos: Vec2, mouse_buttons, keys) -> None:
        if self.game_state != "playing":
            for emitter in self.emitters:
                emitter.update(dt)
            self.emitters = [e for e in self.emitters if e.particles]
            return

        move = 0.0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move -= 1.0
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move += 1.0
        self.player_x += move * self.player_speed * dt
        self.player_x = max(34, min(self.size[0] - 34, self.player_x))
        self.player_body.pos.update(self.player_x, self.player_y)

        self.shoot_cooldown = max(0.0, self.shoot_cooldown - dt)
        if self.reload_timer > 0:
            self.reload_timer = max(0.0, self.reload_timer - dt)
            if self.reload_timer == 0 and self.ammo <= 0:
                self.ammo = self.ammo_max

        self.enemy_fire_timer -= dt
        if self.enemy_fire_timer <= 0:
            self._enemy_fire()
            self.enemy_fire_timer = self.enemy_fire_interval

        self.world.update(dt)

        for a, b in self.world.contacts:
            if not a.alive or not b.alive:
                continue

            pair = (a.kind, b.kind)
            if pair in (("player_bullet", "enemy"), ("enemy", "player_bullet")):
                bullet = a if a.kind == "player_bullet" else b
                enemy = b if bullet is a else a
                if bullet.alive and enemy.alive:
                    bullet.alive = False
                    enemy.hp -= 1
                    self.score += 10
                    self._add_burst(Vec2(bullet.pos), 8)
                    self._add_burst(Vec2(enemy.pos), 10)
                    if enemy.hp <= 0:
                        enemy.alive = False
                        self.score += 30
            elif pair in (("enemy_bullet", "player"), ("player", "enemy_bullet")):
                bullet = a if a.kind == "enemy_bullet" else b
                if bullet.alive:
                    bullet.alive = False
                    self.lives -= 1
                    self._add_burst(Vec2(self.player_x, self.player_y - 4), 18)
                    if self.lives <= 0:
                        self.game_state = "lose"

        for body in self.world.bodies:
            if not body.alive:
                continue
            if body.kind == "player_bullet" and body.pos.y < -40:
                body.alive = False
            elif body.kind == "enemy_bullet":
                # Enemy bullets disappear when they hit ground or go off screen
                ground_level = self.size[1] - 50
                if body.pos.y + body.radius >= ground_level or body.pos.y > self.size[1] + 40:
                    body.alive = False

        enemies_left = [b for b in self.world.bodies if b.kind == "enemy" and b.alive]
        if not enemies_left:
            self.game_state = "win"
            self._add_burst(Vec2(self.size[0] / 2, 180), 36)

        self.world.bodies = [body for body in self.world.bodies if body.alive]

        for emitter in self.emitters:
            emitter.update(dt)
        self.emitters = [e for e in self.emitters if e.particles]

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_background(surface)
        self.world.draw(surface)

        for emitter in self.emitters:
            emitter.draw(surface)

        x = int(self.player_x)
        y = int(self.player_y)
        pygame.draw.circle(surface, (110, 240, 255), (x, y), 18)

        hud = pygame.Surface((self.size[0], 62), pygame.SRCALPHA)
        pygame.draw.rect(hud, (10, 16, 28, 190), pygame.Rect(0, 0, self.size[0], 62))
        pygame.draw.line(hud, (80, 140, 255), (0, 61), (self.size[0], 61), 2)
        surface.blit(hud, (0, 0))

        if self.game_state != "playing":
            overlay = pygame.Surface(self.size, pygame.SRCALPHA)
            pygame.draw.rect(overlay, (0, 0, 0, 130), pygame.Rect(0, 0, *self.size))
            surface.blit(overlay, (0, 0))

            panel = pygame.Surface((620, 220), pygame.SRCALPHA)
            pygame.draw.rect(panel, (8, 12, 20, 235), pygame.Rect(0, 0, 620, 220), border_radius=18)
            pygame.draw.rect(panel, (120, 190, 255, 220), pygame.Rect(0, 0, 620, 220), width=2, border_radius=18)
            px = int(self.size[0] / 2 - 310)
            py = int(self.size[1] / 2 - 110)
            surface.blit(panel, (px, py))

            big_font = pygame.font.SysFont("arial", 52, bold=True)
            med_font = pygame.font.SysFont("arial", 24)
            title = "YOU WIN" if self.game_state == "win" else "GAME OVER"
            title_color = (120, 255, 160) if self.game_state == "win" else (255, 110, 110)
            title_surf = big_font.render(title, True, title_color)
            surface.blit(title_surf, (self.size[0] / 2 - title_surf.get_width() / 2, py + 28))

            score_surf = med_font.render(f"Score: {self.score}", True, (235, 240, 245))
            surface.blit(score_surf, (self.size[0] / 2 - score_surf.get_width() / 2, py + 95))

            msg = "Press R or Enter to play again"
            msg_surf = med_font.render(msg, True, (200, 210, 220))
            surface.blit(msg_surf, (self.size[0] / 2 - msg_surf.get_width() / 2, py + 135))

    def overlay_text(self) -> list[str]:
        if self.game_state == "win":
            return [
                f"You won! Score: {self.score}",
                "Press R or Enter to restart.",
            ]
        if self.game_state == "lose":
            return [
                f"Game over. Score: {self.score}",
                "Press R or Enter to restart.",
            ]
        ammo_text = "Reloading" if self.reload_timer > 0 else f"Ammo: {self.ammo}/{self.ammo_max}"
        return [
            "Move with A/D or the arrow keys.",
            "Press Space to fire.",
            f"Score: {self.score}   Lives: {self.lives}   {ammo_text}",
        ]


class ParticleScene(SceneBase):

    title = "Particle System"

    def __init__(self, size):
        self.size = size
        self.emitter = ParticleEmitter(Vec2(size[0] * 0.25, size[1] * 0.4))

    def reset(self) -> None:
        self.emitter = ParticleEmitter(Vec2(self.size[0] * 0.25, self.size[1] * 0.4))

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.emitter.burst()

    def update(self, dt: float, mouse_pos: Vec2, mouse_buttons, keys) -> None:
        self.emitter.set_pos(mouse_pos)
        self.emitter.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.emitter.draw(surface)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.emitter.pos.x), int(self.emitter.pos.y)), 10, 2)

    def overlay_text(self) -> list[str]:
        return [
            "Move the mouse to move the emitter.",
            "Left click to burst particles.",
            "Gravity, emission rate, and lifespan are visible here.",
        ]


class MassSpringScene(SceneBase):
    title = "Mass-Spring Soft Body"

    def __init__(self, size):
        self.size = size
        self.system = MassSpringSystem(origin=(180, 120), rows=6, cols=6, spacing=28)
        self.dragging = None

    def reset(self) -> None:
        self.system.reset()
        self.dragging = None

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.dragging = self.system.grab_nearest(Vec2(event.pos))
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = None

    def update(self, dt: float, mouse_pos: Vec2, mouse_buttons, keys) -> None:
        if self.dragging is not None and mouse_buttons[0]:
            self.system.drag_node(self.dragging, mouse_pos)
        self.system.update(dt, pygame.Rect(0, 0, *self.size))

    def draw(self, surface: pygame.Surface) -> None:
        self.system.draw(surface)

    def overlay_text(self) -> list[str]:
        return [
            "Drag any node to deform the soft body.",
            "Pinned corners keep the structure stable.",
            "This demonstrates a mass-spring model with verlet integration.",
        ]


class PBDScene(SceneBase):
    title = "Position-Based Dynamics Rope"

    def __init__(self, size):
        self.size = size
        self.chain = PBDChain(origin=(size[0] * 0.72, 100), segments=16, length=22)

    def reset(self) -> None:
        self.chain.reset()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.chain.grab_end(Vec2(event.pos))
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.chain.release()

    def update(self, dt: float, mouse_pos: Vec2, mouse_buttons, keys) -> None:
        self.chain.update(dt, pygame.Rect(0, 0, *self.size), mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        self.chain.draw(surface)

    def overlay_text(self) -> list[str]:
        return [
            "Left click and drag the rope end.",
            "The solver enforces fixed segment lengths repeatedly.",
            "This is the core idea behind Position-Based Dynamics.",
        ]


class RigidBodyScene(SceneBase):
    title = "Rigid Body Dynamics"

    def __init__(self, size):
        self.size = size
        self.world = RigidBodyWorld(size=size)

    def reset(self) -> None:
        self.world.reset()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.world.spawn(Vec2(event.pos), radius=18, randomize=True)
            elif event.button == 3:
                self.world.spawn(Vec2(event.pos), radius=30, randomize=True)

    def update(self, dt: float, mouse_pos: Vec2, mouse_buttons, keys) -> None:
        if keys[pygame.K_SPACE]:
            self.world.apply_explosion(Vec2(self.size[0] * 0.5, 140), 140.0)
        self.world.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.world.draw(surface)

    def overlay_text(self) -> list[str]:
        return [
            "Left click spawns a small rigid body.",
            "Right click spawns a larger rigid body.",
            "The world resolves circle-circle and circle-ground collisions.",
        ]


class KinematicsScene(SceneBase):
    title = "Forward and Inverse Kinematics"

    def __init__(self, size):
        self.size = size
        self.arm = TwoLinkArm(base=(160, size[1] - 110), length1=190, length2=145)

    def reset(self) -> None:
        self.arm.reset()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            self.arm.elbow_up = not self.arm.elbow_up

    def update(self, dt: float, mouse_pos: Vec2, mouse_buttons, keys) -> None:
        self.arm.set_target(mouse_pos)

    def draw(self, surface: pygame.Surface) -> None:
        self.arm.draw(surface)

    def overlay_text(self) -> list[str]:
        return [
            "Move the mouse to set the IK target.",
            "Press E to toggle elbow-up / elbow-down.",
            "The arm shows both forward kinematics and inverse kinematics.",
        ]
