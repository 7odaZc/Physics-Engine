from __future__ import annotations

from dataclasses import dataclass
import pygame


Vec2 = pygame.math.Vector2


@dataclass
class SegmentPoint:
    pos: Vec2
    prev: Vec2
    pinned: bool = False


class PBDChain:
    def __init__(self, origin=(560, 110), segments=14, length=24):
        self.origin = Vec2(origin)
        self.segments = segments
        self.length = length
        self.gravity = Vec2(0, 800)
        self.iterations = 12
        self.points: list[SegmentPoint] = []
        self._dragging_end = False
        self.build()

    def build(self) -> None:
        self.points = []
        for i in range(self.segments + 1):
            p = self.origin + Vec2(0, i * self.length)
            self.points.append(SegmentPoint(pos=Vec2(p), prev=Vec2(p)))
        self.points[0].pinned = True

    def reset(self) -> None:
        self.build()
        self._dragging_end = False

    def set_end_target(self, pos: Vec2) -> None:
        end = self.points[-1]
        end.pos.update(pos)
        end.prev.update(pos)

    def grab_end(self, mouse_pos: Vec2) -> bool:
        if (self.points[-1].pos - mouse_pos).length() < 30:
            self._dragging_end = True
            return True
        return False

    def release(self) -> None:
        self._dragging_end = False

    def update(self, dt: float, surface_rect: pygame.Rect, mouse_pos: Vec2 | None = None) -> None:
        dt2 = dt * dt
        for idx, point in enumerate(self.points):
            if point.pinned:
                point.pos.update(self.origin)
                point.prev.update(self.origin)
                continue

            current = Vec2(point.pos)
            velocity = point.pos - point.prev
            point.pos += velocity + self.gravity * dt2
            point.prev = current

        if self._dragging_end and mouse_pos is not None:
            self.set_end_target(mouse_pos)

        for _ in range(self.iterations):
            self._satisfy_constraints()
            self._keep_in_bounds(surface_rect)

    def _satisfy_constraints(self) -> None:
        for i in range(len(self.points) - 1):
            a = self.points[i]
            b = self.points[i + 1]
            delta = b.pos - a.pos
            dist = delta.length()
            if dist == 0:
                continue
            diff = (dist - self.length) / dist
            correction = delta * 0.5 * diff
            if not a.pinned:
                a.pos += correction
            if not b.pinned:
                b.pos -= correction

    def _keep_in_bounds(self, rect: pygame.Rect) -> None:
        for p in self.points:
            p.pos.x = max(rect.left + 4, min(rect.right - 4, p.pos.x))
            p.pos.y = max(rect.top + 4, min(rect.bottom - 4, p.pos.y))

    def draw(self, surface: pygame.Surface) -> None:
        for i in range(len(self.points) - 1):
            a = self.points[i].pos
            b = self.points[i + 1].pos
            pygame.draw.line(surface, (120, 170, 255), a, b, 4)

        for i, p in enumerate(self.points):
            color = (255, 220, 120) if i == len(self.points) - 1 else (220, 240, 255)
            if p.pinned:
                color = (255, 120, 120)
            pygame.draw.circle(surface, color, (int(p.pos.x), int(p.pos.y)), 6)
