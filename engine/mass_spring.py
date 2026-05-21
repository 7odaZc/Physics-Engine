from __future__ import annotations

from dataclasses import dataclass
import math
import pygame


Vec2 = pygame.math.Vector2


@dataclass
class Node:
    pos: Vec2
    prev: Vec2
    pinned: bool = False
    pin_pos: Vec2 | None = None
    radius: int = 5


@dataclass
class Spring:
    a: int
    b: int
    rest: float
    stiffness: float = 1.0
    damping: float = 0.02


class MassSpringSystem:
    def __init__(self, origin=(180, 120), rows=6, cols=6, spacing=26):
        self.origin = Vec2(origin)
        self.rows = rows
        self.cols = cols
        self.spacing = spacing
        self.gravity = Vec2(0, 700)
        self.damping = 0.995
        self.iterations = 8
        self.nodes: list[Node] = []
        self.springs: list[Spring] = []
        self.build()

    def build(self) -> None:
        self.nodes.clear()
        self.springs.clear()

        for y in range(self.rows):
            for x in range(self.cols):
                pos = self.origin + Vec2(x * self.spacing, y * self.spacing)
                self.nodes.append(Node(pos=Vec2(pos), prev=Vec2(pos)))

        def idx(x: int, y: int) -> int:
            return y * self.cols + x

        for y in range(self.rows):
            for x in range(self.cols):
                if x + 1 < self.cols:
                    self.springs.append(Spring(idx(x, y), idx(x + 1, y), self.spacing, 1.0, 0.02))
                if y + 1 < self.rows:
                    self.springs.append(Spring(idx(x, y), idx(x, y + 1), self.spacing, 1.0, 0.02))
                if x + 1 < self.cols and y + 1 < self.rows:
                    self.springs.append(Spring(idx(x, y), idx(x + 1, y + 1), self.spacing * math.sqrt(2), 0.85, 0.02))
                if x - 1 >= 0 and y + 1 < self.rows:
                    self.springs.append(Spring(idx(x, y), idx(x - 1, y + 1), self.spacing * math.sqrt(2), 0.85, 0.02))

        # Pin top corners to make a stable soft body.
        self.nodes[idx(0, 0)].pinned = True
        self.nodes[idx(0, 0)].pin_pos = Vec2(self.nodes[idx(0, 0)].pos)
        self.nodes[idx(self.cols - 1, 0)].pinned = True
        self.nodes[idx(self.cols - 1, 0)].pin_pos = Vec2(self.nodes[idx(self.cols - 1, 0)].pos)

    def reset(self) -> None:
        self.build()

    def _integrate(self, dt: float) -> None:
        dt2 = dt * dt
        for node in self.nodes:
            if node.pinned and node.pin_pos is not None:
                node.pos.update(node.pin_pos)
                node.prev.update(node.pin_pos)
                continue

            current = Vec2(node.pos)
            velocity = (node.pos - node.prev) * self.damping
            node.pos += velocity + self.gravity * dt2
            node.prev = current

    def _satisfy_spring(self, spring: Spring) -> None:
        a = self.nodes[spring.a]
        b = self.nodes[spring.b]
        delta = b.pos - a.pos
        dist = delta.length()
        if dist == 0:
            return
        diff = (dist - spring.rest) / dist
        correction = delta * 0.5 * spring.stiffness * diff

        if not a.pinned:
            a.pos += correction
        if not b.pinned:
            b.pos -= correction

    def _constrain_bounds(self, surface_rect: pygame.Rect) -> None:
        left, top, right, bottom = surface_rect.left, surface_rect.top, surface_rect.right, surface_rect.bottom
        for node in self.nodes:
            if node.pinned:
                continue
            node.pos.x = max(left + 5, min(right - 5, node.pos.x))
            node.pos.y = max(top + 5, min(bottom - 5, node.pos.y))

    def update(self, dt: float, surface_rect: pygame.Rect) -> None:
        self._integrate(dt)
        for _ in range(self.iterations):
            for spring in self.springs:
                self._satisfy_spring(spring)
            self._constrain_bounds(surface_rect)

    def grab_nearest(self, mouse_pos: Vec2, radius: float = 22.0) -> int | None:
        nearest = None
        best = radius
        for i, node in enumerate(self.nodes):
            dist = (node.pos - mouse_pos).length()
            if dist < best:
                best = dist
                nearest = i
        return nearest

    def drag_node(self, index: int, pos: Vec2) -> None:
        node = self.nodes[index]
        node.pos.update(pos)
        node.prev.update(pos)

    def draw(self, surface: pygame.Surface) -> None:
        for spring in self.springs:
            a = self.nodes[spring.a].pos
            b = self.nodes[spring.b].pos
            pygame.draw.line(surface, (80, 200, 120), a, b, 2)

        for node in self.nodes:
            color = (245, 90, 90) if node.pinned else (255, 240, 200)
            pygame.draw.circle(surface, color, (int(node.pos.x), int(node.pos.y)), node.radius)
