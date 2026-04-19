import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from scene import Scene, SceneManager
from math_helper import MathHelper

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

class MapZone:
    """Represents a clickable polygonal zone on the map.
    """
    def __init__(self, name: str, edges):
        """Initializes a MapZone.

        Args:
            name (str): Name of the zone.
            edges (list[tuple]): List of edge tuples defining the polygon.
        """
        self.name = name
        self.edges = edges


def make_edges(points):
    """Convert list of points into closed polygon edges."""
    edges = []
    for i in range(len(points)):
        p1 = points[i]
        p2 = points[(i + 1) % len(points)]
        edges.append((p1, p2))
    return edges

class MapScene(Scene):
    """Scene that displays the zoo map and handles navigation via polygon zones."""
    def __init__(self, manager: SceneManager) -> None:
        """Initializes the map scene and all interactive zones.

        Args:
            manager (SceneManager): The scene manager controlling scene transitions.
        """
        super().__init__(manager)

        self.map_rect = None
        self.screen = pygame.display.get_surface()

        self.map_image = pygame.image.load(
            os.path.join("assets", "images", "zoo_map.png")
        ).convert_alpha()

        self.font = pygame.font.SysFont(None, 24)

        self.zones = [

            MapZone("rattlesnake", make_edges([
                (640, 330),
                (640, 130),
                (535, 160),
                (535, 230),
            ])),

            MapZone("meerkat", make_edges([
                (650, 330),
                (650, 130),
                (745, 150),
                (750, 230),
            ])),

            MapZone("penguin", make_edges([
                (530, 275),
                (545, 260),
                (610, 330),
                (590, 345),
            ])),

            MapZone("octopus", make_edges([
                (500, 370),
                (530, 380),
                (550, 375),
                (555, 340),
                (525, 320),
                (500, 330),
            ])),

            MapZone("giraffe", make_edges([
                (660, 345),
                (765, 245),
                (760, 450),
            ])),

            MapZone("zebra", make_edges([
                (775, 240),
                (775, 345),
                (875, 345),
                (845, 250),
            ])),

            MapZone("lion", make_edges([
                (775, 350),
                (775, 460),
                (840, 450),
                (875, 355),
            ])),

            MapZone("tiger", make_edges([
                (530, 475),
                (750, 475),
                (750, 550),
                (700, 580),
                (600, 580),
                (540, 550),
            ])),

            MapZone("red panda", make_edges([
                (530, 465),
                (750, 465),
                (640, 350),
            ])),

            MapZone("fish", make_edges([
                (515, 420),
                (515, 460),
                (460, 460),
                (430, 430),
                (410, 345),
                (430, 275),
                (465, 245),
                (515, 240),
                (515, 290),
                (480, 300),
                (460, 330),
                (460, 380),
                (480, 415),
            ])),
        ]

    def _get_map_rect(self, screen):
        """Compute the centered rectangle for the map image.

        Args:
            screen (pygame.Surface): The display surface.
        """
        return self.map_image.get_rect(center=screen.get_rect().center)

    def handle_events(self, events) -> None:
        """Handle user input events such as clicks and key presses.

        Args:
            events (list[pygame.event.Event]): List of input events.
        """
        for event in events:

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from pause_scene import PauseScene
                self._manager.push(PauseScene(self._manager))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(pygame.mouse.get_pos())

    def _handle_click(self, mouse_pos):
        """Handle a mouse click and determine if a zone was selected.

        Args:
            mouse_pos (tuple[int, int]): The (x, y) position of the mouse click.
        """
        for zone in self.zones:
            if MathHelper.is_within_polygon(mouse_pos, zone.edges):
                self._handle_action(zone.name)
                return

    def update(self, dt: float) -> None:
        """Update scene state.

        Args:
            dt (float): Time elapsed since last frame (in seconds).
        """
        pass

    def draw(self, screen):
        """Render the map scene.

        Args:
            screen (pygame.Surface): The display surface.
        """
        screen.fill((255, 230, 230))

        self.map_rect = self.map_image.get_rect(
            center=screen.get_rect().center
        )

        screen.blit(self.map_image, self.map_rect.topleft)


    def _handle_action(self, action: str) -> None:
        """Trigger the appropriate habitat scene based on zone selection.

        Args:
            action (str): Name of the selected zone.
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