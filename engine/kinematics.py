from __future__ import annotations

import math
import pygame


Vec2 = pygame.math.Vector2


class TwoLinkArm:
    def __init__(self, base=(160, 560), length1=180, length2=150):
        self.base = Vec2(base)
        self.length1 = float(length1)
        self.length2 = float(length2)
        self.theta1 = -0.8
        self.theta2 = 1.2
        self.elbow_up = True
        self.target = Vec2(500, 300)

    def reset(self) -> None:
        self.theta1 = -0.8
        self.theta2 = 1.2
        self.elbow_up = True

    def set_target(self, target: Vec2) -> None:
        self.target.update(target)
        self.solve_ik(target)

    def solve_ik(self, target: Vec2) -> None:
        delta = Vec2(target) - self.base
        dist = delta.length()

        max_reach = self.length1 + self.length2 - 0.001
        min_reach = abs(self.length1 - self.length2) + 0.001
        dist = max(min_reach, min(max_reach, dist))

        cos_angle2 = (dist * dist - self.length1 * self.length1 - self.length2 * self.length2) / (2 * self.length1 * self.length2)
        cos_angle2 = max(-1.0, min(1.0, cos_angle2))
        angle2 = math.acos(cos_angle2)
        if self.elbow_up:
            angle2 = -angle2

        k1 = self.length1 + self.length2 * math.cos(angle2)
        k2 = self.length2 * math.sin(angle2)
        angle1 = math.atan2(delta.y, delta.x) - math.atan2(k2, k1)

        self.theta1 = angle1
        self.theta2 = angle2

    def fk(self):
        elbow = self.base + Vec2(math.cos(self.theta1), math.sin(self.theta1)) * self.length1
        end = elbow + Vec2(math.cos(self.theta1 + self.theta2), math.sin(self.theta1 + self.theta2)) * self.length2
        return self.base, elbow, end

    def draw(self, surface: pygame.Surface) -> None:
        base, elbow, end = self.fk()

        pygame.draw.line(surface, (240, 240, 255), base, elbow, 10)
        pygame.draw.line(surface, (180, 220, 255), elbow, end, 10)
        pygame.draw.circle(surface, (255, 120, 120), (int(base.x), int(base.y)), 14)
        pygame.draw.circle(surface, (120, 255, 160), (int(elbow.x), int(elbow.y)), 12)
        pygame.draw.circle(surface, (255, 230, 100), (int(end.x), int(end.y)), 14)

        pygame.draw.circle(surface, (255, 100, 100), (int(self.target.x), int(self.target.y)), 8, 2)
