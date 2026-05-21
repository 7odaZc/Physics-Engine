from __future__ import annotations

import pygame

from game.scenes import BallSmashScene, ParticleScene, MassSpringScene, PBDScene, RigidBodyScene, KinematicsScene


class PhysicsPlayground:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Star Shooter")
        self.size = (1200, 800)
        self.screen = pygame.display.set_mode(self.size)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 20)
        self.small_font = pygame.font.SysFont("arial", 16)

        self.scenes = [
            BallSmashScene(self.size),
            ParticleScene(self.size),
            MassSpringScene(self.size),
            PBDScene(self.size),
            RigidBodyScene(self.size),
            KinematicsScene(self.size),
        ]
        self.scene_index = 0
        self.running = True

    @property
    def scene(self):
        return self.scenes[self.scene_index]

    def switch_scene(self, index: int) -> None:
        if 0 <= index < len(self.scenes):
            self.scene_index = index
            self.scene.reset()

    def draw_ui(self) -> None:
        title = f"{self.scene.title}   (Press 1-6 to switch scenes, R to reset, ESC to quit)"
        label = self.font.render(title, True, (255, 255, 255))
        self.screen.blit(label, (18, 14))

        y = 44
        for line in self.scene.overlay_text():
            text = self.small_font.render(line, True, (220, 225, 235))
            self.screen.blit(text, (18, y))
            y += 22

        names = ["Shooter", "Particle", "Soft body", "PBD rope", "Rigid bodies", "IK/FK"]
        x = 18
        for i, name in enumerate(names):
            active = i == self.scene_index
            color = (80, 190, 255) if active else (90, 90, 100)
            rect = pygame.Rect(x, self.size[1] - 42, 115, 26)
            pygame.draw.rect(self.screen, color, rect, border_radius=10)
            txt = self.small_font.render(f"{i+1}. {name}", True, (255, 255, 255))
            self.screen.blit(txt, (rect.x + 10, rect.y + 4))
            x += 124

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            dt = min(dt, 1 / 30)

            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            mouse_buttons = pygame.mouse.get_pressed()
            keys = pygame.key.get_pressed()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.scene.reset()
                    elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6):
                        self.switch_scene(event.key - pygame.K_1)
                self.scene.handle_event(event)

            self.scene.update(dt, mouse_pos, mouse_buttons, keys)

            self.screen.fill((18, 22, 30))
            self.scene.draw(self.screen)
            self.draw_ui()
            pygame.display.flip()

        pygame.quit()
