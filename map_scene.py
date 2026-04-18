"""
Main gameplay scene.
"""
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from scene import Scene, SceneManager
from global_settings import Settings
from button import Button
from fish_habitat import FishHabitat
from giraffe_habitat import GiraffeHabitat
from lion_habitat import LionHabitat
from rattlesnake_habitat import RattlesnakeHabitat
from tiger_habitat import TigerHabitat
from zebra_habitat import ZebraHabitat
from meerkat_habitat import MeerkatHabitat
from red_panda_habitat import RedPandaHabitat
from penguin_habitat import PenguinHabitat
from octopus_habitat import OctopusHabitat

class MapScene(Scene):
    """
    A map of the zoo displaying which minigames are to be done during the current cycle.
    """

    def __init__(self, manager: SceneManager) -> None:
        """Initialize the MapScene with buttons for each habitat minigame.

        Args:
            manager (SceneManager): The scene manager controlling scene transitions.
        """
        super().__init__(manager)

        screen_width, screen_height = Settings().window["size"]
        bw, bh = 200, 60
        group_width = bw + 250
        bx = (screen_width - group_width) // 2
        start_y = screen_height // 2 - 140

        self.buttons = {
            "zebra": Button(bx, start_y + 80 * 0, text="Zebra", width=bw, height=bh, enabled=True),
            "meerkat": Button(bx, start_y + 80 * 1, text="Meerkats", width=bw, height=bh, enabled=True),
            "rattlesnake": Button(bx, start_y + 80 * 2, text="Rattlesnake", width=bw, height=bh, enabled=True),
            "lion": Button(bx + 250, start_y + 80 * 0, text="Lion", width=bw, height=bh, enabled=True),
            "tiger": Button(bx + 250, start_y + 80 * 1, text="Tiger", width=bw, height=bh, enabled=True),
            "giraffe": Button(bx + 250, start_y + 80 * 2, text="Giraffe", width=bw, height=bh, enabled=True),
            "fish": Button(bx, start_y + 80 * 3, text="Fish", width=bw, height=bh, enabled=True),
            "octopus": Button(bx + 250, start_y + 80 * 3, text="Octopus", width=bw, height=bh, enabled=True),
            "penguin": Button(bx, start_y + 80 * 4, text="Penguin", width=bw, height=bh, enabled=True),
            "red panda": Button(bx + 250, start_y + 80 * 4, text="Red Panda", width=bw, height=bh, enabled=True),
        }

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle keyboard and mouse input events for the map.

        Args:
            events (list[pygame.event.Event]): A list of pygame events to process.
        """
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from pause_scene import PauseScene
                self._manager.push(PauseScene(self._manager))
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, button in self.buttons.items():
                    if button.is_clicked(mouse_pos, (True,)):
                        self._handle_action(name)

    def update(self, dt: float) -> None:
        """Update the state of all habitat buttons.

        Args:
            dt (float): Time delta since the last frame.
        """
        for button in self.buttons.values():
            button.update(pygame.mouse.get_pos())

    def draw(self, screen: pygame.Surface) -> None:
        """Render the map scene and all buttons on the screen.

        Args:
            screen (pygame.Surface): The surface to draw the scene on.
        """
        screen.fill((255, 230, 230))
        for button in self.buttons.values():
            button.draw(screen)

    def _handle_action(self, action: str) -> None:
        """Push the corresponding habitat scene onto the scene manager stack.

        Args:
            action (str): The action identifier corresponding to a habitat.
        """
        if action == "zebra":
            self._manager.push(ZebraHabitat(self._manager))
        elif action == "meerkat":
            self._manager.push(MeerkatHabitat(self._manager))
        elif action == "rattlesnake":
            self._manager.push(RattlesnakeHabitat(self._manager))
        elif action == "lion":
            self._manager.push(LionHabitat(self._manager))
        elif action == "tiger":
            self._manager.push(TigerHabitat(self._manager))
        elif action == "giraffe":
            self._manager.push(GiraffeHabitat(self._manager))
        elif action == "fish":
            self._manager.push(FishHabitat(self._manager))
        elif action == "red panda":
            self._manager.push(RedPandaHabitat(self._manager))
        elif action == "octopus":
            self._manager.push(OctopusHabitat(self._manager))
        elif action == "penguin":
            self._manager.push(PenguinHabitat(self._manager))