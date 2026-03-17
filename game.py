"""
Manages the main game loop.
"""

import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from checklist import Checklist
from scene import SceneManager
from menu_scene import MenuScene
from global_settings import Settings

class Game:
    def __init__(self) -> None:
        self.running = True
        pygame.init()

        self.settings = Settings()
        self.screen = pygame.display.set_mode(self.settings.window["size"])
        pygame.display.set_caption(self.settings.window["title"])
        pygame.mouse.set_visible(False)

        self.clock = pygame.time.Clock()

        initial_tasks = ["Tiger", "Monkey", "Lions", "Zebra", "Fish", "Rattlesnake", "Meerkats"]
        self.checklist = Checklist(initial_tasks)

        self.scene_manager = SceneManager()
        self.scene_manager.push(MenuScene(self.scene_manager))

    def run(self) -> None:
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

            pygame.display.flip()

        pygame.quit()