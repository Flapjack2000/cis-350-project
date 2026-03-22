"""
Main gameplay scene.
"""
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from scene import Scene, SceneManager
from global_settings import Settings

class MapScene(Scene):
    """
    A map of the zoo displaying which minigames are to be done during the current cycle.
    """

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)

        cursor_cfg = Settings().cursor
        cursor_surface = pygame.image.load(cursor_cfg["image_path"]).convert_alpha()
        self.cursor = pygame.transform.scale(cursor_surface, cursor_cfg["size"])

    # TODO: single function for handling selection of minigame, push its scene to self.__manager

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from pause_scene import PauseScene
                self._manager.push(PauseScene(self._manager))

    def update(self, dt: float) -> None:
        pass  # TODO: leave blank but keep to fulfill abstract requirement?

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((255, 230, 230))
        screen.blit(self.cursor, pygame.mouse.get_pos())