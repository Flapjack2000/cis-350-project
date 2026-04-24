"""
Manages the main game loop.
"""

import pygame
from checklist import Checklist
from scene import SceneManager, GameContext
from menu_scene import MenuScene
from global_settings import Settings
from audio_player import AudioPlayer


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
        cursor_surface = pygame.image.load(
            cursor_cfg["image_path"]
        ).convert_alpha()
        self.cursor = pygame.transform.scale(
            cursor_surface,
            cursor_cfg["size"]
        )

        initial_tasks = [

            "zebra_pet",
            "zebra_poop",
            "zebra_feed",
            "zebra_water",

            "giraffe_pet",
            "giraffe_poop",
            "giraffe_feed",
            "giraffe_water",

            "tiger_pet",
            "tiger_poop",
            "tiger_feed",
            "tiger_water",

            "lion_pet",
            "lion_poop",
            "lion_feed",
            "lion_water",

            "meerkat_pet",
            "meerkat_poop",
            "meerkat_feed",
            "meerkat_water",

            "red_panda_pet",
            "red_panda_poop",

            "penguin_pet",
            "penguin_feed",
            "penguin_water",

            "rattlesnake_pet",

            "octopus_pet",

            "fish_feed",
        ]
        self.checklist = Checklist(initial_tasks)

        self.audio = AudioPlayer()

        context = GameContext(
            checklist=self.checklist,
            cursor=self.cursor,
            music_player=self.audio
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
            self.scene_manager.context.music_player.update_sounds(dt)
            pygame.display.flip()

        pygame.quit()
