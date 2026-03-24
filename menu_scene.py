"""
Main menu scene.
"""
import os

from fish_habitat import FishHabitat
from giraffe_habitat import GiraffeHabitat
from lion_habitat import LionHabitat
from rattlesnake_habitat import RattlesnakeHabitat
from tiger_habitat import TigerHabitat

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from scene import Scene, SceneManager
from global_settings import Settings
from button import Button
from map_scene import MapScene
from zebra_habitat import ZebraHabitat
from meerkat_habitat import MeerkatHabitat

class MenuScene(Scene):
    """The main menu: Start Game / Settings / Quit."""

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)

        screen_width, screen_height = Settings().window["size"]
        bw, bh = 200, 60
        bx = (screen_width - bw) // 2
        start_y = screen_height // 2 - 140

        self.buttons = {
            "start":       Button(bx,       start_y + 80 * 0, text="Start Game",  width=bw, height=bh, enabled=True),
            "settings":    Button(bx,       start_y + 80 * 1, text="Settings",    width=bw, height=bh, enabled=False),
            "zebra":       Button(bx,       start_y + 80 * 2, text="Zebra",       width=bw, height=bh, enabled=True),
            "meerkat":     Button(bx,       start_y + 80 * 3, text="Meerkats",    width=bw, height=bh, enabled=True),
            "rattlesnake": Button(bx,       start_y + 80 * 4, text="Rattlesnake", width=bw, height=bh, enabled=True),
            "lion":        Button(bx + 250, start_y + 80 * 2, text="Lion",        width=bw, height=bh, enabled=True),
            "tiger":       Button(bx + 250, start_y + 80 * 3, text="Tiger",       width=bw, height=bh, enabled=True),
            "giraffe":     Button(bx + 250, start_y + 80 * 4, text="Giraffe",     width=bw, height=bh, enabled=True),
            "fish":        Button(bx + 250, start_y + 80 * 5, text="Fish",        width=bw, height=bh, enabled=True),
            "quit":        Button(bx,       start_y + 80 * 5, text="Quit",        width=bw, height=bh, enabled=True),
        }
        self.title_font = pygame.font.Font(None, 72)

    def on_enter(self) -> None:
        for button in self.buttons.values():
            button.hovered = False

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, button in self.buttons.items():
                    if button.is_clicked(mouse_pos, (True,)):
                        self._handle_action(name)

    def update(self, dt: float) -> None:
        for button in self.buttons.values():
            button.update(pygame.mouse.get_pos())

    def draw(self, screen: pygame.Surface) -> None:
        screen.fill((255, 230, 230))
        title = self.title_font.render("Zoo Game", True, (150, 100, 100))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, 150)))
        for button in self.buttons.values():
            button.draw(screen)

    def _handle_action(self, action: str) -> None:
        if action == "start":
            self._manager.pop()
            self._manager.push(MapScene(self._manager))
        elif action == "quit":
            self._manager.exit_all()

        # TODO: quick testing, move functionality to map_scene later
        elif action == "zebra":
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