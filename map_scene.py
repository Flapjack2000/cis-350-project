import os
import pygame
from scene import Scene, SceneManager
from global_settings import Settings
from math_helper import MathHelper
from habitat_scene import _IconButton, TOOLBAR_PAD
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
    """Represents a clickable polygonal zone on the map."""

    def __init__(self, name: str, points: list[tuple[int, int]]):
        """
        Initializes a MapZone and generates edges for collision detection.

        Args:
            name (str): Name of the zone.
            points (list): List of (x, y) coordinates defining the polygon.
        """
        self.name = name
        self.edges = []
        for i in range(len(points)):
            p1 = points[i]
            p2 = points[(i + 1) % len(points)]
            self.edges.append((p1, p2))


class MapScene(Scene):
    """Scene that displays the zoo map and handles navigation via polygon zones."""

    HABITAT_MAP = {
        "rattlesnake": RattlesnakeHabitat,
        "meerkat": MeerkatHabitat,
        "penguin": PenguinHabitat,
        "octopus": OctopusHabitat,
        "giraffe": GiraffeHabitat,
        "zebra": ZebraHabitat,
        "lion": LionHabitat,
        "tiger": TigerHabitat,
        "red panda": RedPandaHabitat,
        "fish": FishHabitat,
    }

    def __init__(self, manager: SceneManager) -> None:
        """
        Initializes the map scene, UI elements, and interactive zones.

        Args:
            manager (SceneManager): The scene manager controlling transitions.
        """
        super().__init__(manager)

        self._screen_size = Settings().window["size"]
        self.map_image = pygame.image.load(
            os.path.join("assets", "images", "zoo_map.png")
        ).convert_alpha()

        self.map_rect = self.map_image.get_rect(
            center=(self._screen_size[0] // 2, self._screen_size[1] // 2)
        )

        self._init_buttons()
        self._init_zones()

    def _init_buttons(self) -> None:
        """Sets up the navigation buttons in the top right of the screen."""
        icon_path = os.path.join("assets", "images", "checklist_icon.png")
        self._btn_checklist = _IconButton(icon_path, (0, 0))

        # Position checklist icon in the top right
        margin = TOOLBAR_PAD
        btn_x = self._screen_size[0] - self._btn_checklist.rect.width - margin
        btn_y = margin
        self._btn_checklist.rect.topleft = (btn_x, btn_y)

    def _init_zones(self) -> None:
        """Defines all interactive polygon areas for the habitats."""
        self.zones = [
            MapZone("rattlesnake", [
                (640, 330), (640, 130), (535, 160), (535, 230)
            ]),
            MapZone("meerkat", [
                (650, 330), (650, 130), (745, 150), (750, 230)
            ]),
            MapZone("penguin", [
                (530, 275), (545, 260), (610, 330), (590, 345)
            ]),
            MapZone("octopus", [
                (500, 370), (530, 380), (550, 375),
                (555, 340), (525, 320), (500, 330)
            ]),
            MapZone("giraffe", [
                (660, 345), (765, 245), (760, 450)
            ]),
            MapZone("zebra", [
                (775, 240), (775, 345), (875, 345), (845, 250)
            ]),
            MapZone("lion", [
                (775, 350), (775, 460), (840, 450), (875, 355)
            ]),
            MapZone("tiger", [
                (530, 475), (750, 475), (750, 550),
                (700, 580), (600, 580), (540, 550)
            ]),
            MapZone("red panda", [
                (530, 465), (750, 465), (640, 350)
            ]),
            MapZone("fish", [
                (515, 420), (515, 460), (460, 460), (430, 430),
                (410, 345), (430, 275), (465, 245), (515, 240),
                (515, 290), (480, 300), (460, 330), (460, 380),
                (480, 415)
            ]),
        ]

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """
        Processes mouse clicks for navigation and habitat entry.

        Args:
            events (list): List of pygame events.
        """
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from pause_scene import PauseScene
                self._manager.push(PauseScene(self._manager))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos

                # UI Button check
                if self._btn_checklist.rect.collidepoint(mouse_pos):
                    from checklist_scene import ChecklistScene
                    self._manager.push(
                        ChecklistScene(self._manager, self._manager.context.checklist)
                    )
                    return

                # Map Zone check
                for zone in self.zones:
                    if MathHelper.is_within_polygon(mouse_pos, zone.edges):
                        self._navigate_to_habitat(zone.name)
                        return

    def _navigate_to_habitat(self, name: str) -> None:
        """
        Pushes the corresponding habitat scene based on the zone name.

        Args:
            name (str): The identifier of the clicked zone.
        """
        habitat_class = self.HABITAT_MAP.get(name)
        if habitat_class:
            self._manager.push(habitat_class(self._manager))

    def update(self, dt: float) -> None:
        """Update logic for the map scene."""
        pass

    def draw(self, screen: pygame.Surface) -> None:
        """
        Renders the map and UI elements.

        Args:
            screen (pygame.Surface): The main display surface.
        """
        screen.fill((255, 230, 230))

        # Render background map
        screen.blit(self.map_image, self.map_rect.topleft)

        # Render UI overlay
        self._btn_checklist.draw(screen)
