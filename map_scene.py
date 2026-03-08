"""
Main gameplay scene.
"""
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from scene import Scene, SceneManager

class MapScene(Scene):
    """The core gameplay scene: clock, day/night cycle, movement, etc."""

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)

        cursor_surface = pygame.image.load("assets/images/cat_cursor.png").convert_alpha()
        self.cursor = pygame.transform.scale(cursor_surface, (64, 64))

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from pause_scene import PauseScene
                self.manager.push(PauseScene(self.manager))

    def update(self, dt: float) -> None:
        pass  # TODO: game logic

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((255, 230, 230))
        screen.blit(self.cursor, pygame.mouse.get_pos())