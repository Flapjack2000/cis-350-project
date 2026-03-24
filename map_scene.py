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

class MapScene(Scene):
    """
    A map of the zoo displaying which minigames are to be done during the current cycle.
    """

    def __init__(self, manager: SceneManager) -> None:
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
            "fish": Button(bx + 125, start_y + 80 * 3, text="Fish", width=bw, height=bh, enabled=True),
        }

    def handle_events(self, events: list[pygame.event.Event]) -> None:
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
        for button in self.buttons.values():
            button.update(pygame.mouse.get_pos())

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((255, 230, 230))
        for button in self.buttons.values():
            button.draw(screen)

    def _handle_action(self, action: str) -> None:
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