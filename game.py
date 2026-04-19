"""
Manages the main game loop.
"""

import pygame
from checklist import Checklist
from scene import SceneManager, GameContext
from menu_scene import MenuScene
from global_settings import Settings

from checklist_scene import ChecklistScene

class Game:
    """Manage the logic of running the game."""

    def __init__(self) -> None:
        """Initialize the screen, checklist, settings, and scene manager."""

        self.running = True
        pygame.init()

        self.settings = Settings()
        self.screen = pygame.display.set_mode(self.settings.window["size"])
        pygame.display.set_caption(self.settings.window["title"])
        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()

        cursor_cfg = self.settings.cursor
        cursor_surface = pygame.image.load(cursor_cfg["image_path"]).convert_alpha()
        self.cursor = pygame.transform.scale(cursor_surface, cursor_cfg["size"])

        initial_tasks = [
            "tiger",
            "lions",
            "zebra",
            "fish",
            "rattlesnake",
            "meerkat",
            "giraffe",
            "octopus",
            "penguin",
            "red panda"
        ]
        self.checklist = Checklist(initial_tasks)

        context = GameContext(
            checklist=self.checklist,
            cursor=self.cursor
        )
        self.scene_manager = SceneManager(context)
        self.scene_manager.push(MenuScene(self.scene_manager))

    def run(self) -> None:
        """Run the game loop of the current scene."""

        while self.running and not self.scene_manager.is_empty:
            dt = self.clock.tick(self.settings.time["fps"]) / 1000.0

            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False

            scene = self.scene_manager.current
            if scene:
                scene.handle_events(events)
                scene.update(dt)
                scene.draw(self.screen)

            self.screen.blit(self.cursor, pygame.mouse.get_pos())

            pygame.display.flip()

        pygame.quit()
