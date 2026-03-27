import os
import random
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from scene import Scene, SceneManager
from global_settings import Settings

# (filename, faces_right, height_px, y_position, speed)
_FISH_INFO = [
    ("moorishidol.png",      False, 180, 30,  0.60),
    ("sailfintang.png",      False, 240, 310, 0.80),
    ("clownfish.png",        True,  100, 140, 0.50),
    ("discus.png",           False, 125, 400, 0.70),
    ("yellowtang.png",       True,  125, 60,  0.90),
    ("yellowperch.png",      False, 180, 250, 0.65),
    ("africanjewelfish.png", False, 220, 185, 0.75),
]

_SUBFOLDER = os.path.join("assets", "animals", "fish")


class _Fish:
    """Represents a single fish in the aquarium habitat.
    """
    def __init__(self, img_path: str, faces_right: bool, size_px: int,
                 x: float, y: float, speed: float, screen_width: int) -> None:
        """Initialize a fish with a sprite, position, speed, and movement direction.

        Args:
            img_path (str): Path to the fish sprite image.
            faces_right (bool): Whether the fish faces right by default.
            size_px (int): Vertical size of the fish sprite in pixels.
            x (float): Initial x-coordinate on the screen.
            y (float): Initial y-coordinate on the screen.
            speed (float): Horizontal movement speed.
            screen_width (int): Width of the screen to determine respawn bounds.
        """
        raw = pygame.image.load(img_path).convert_alpha()
        w, h = raw.get_size()
        scale = size_px / h
        self.base_img = pygame.transform.smoothscale(raw, (int(w * scale), size_px))
        self.faces_right = faces_right
        self.x = x
        self.y = y
        self.home_y = y
        self.speed = speed
        self.screen_width = screen_width
        self.moving_right = random.choice([True, False])

    @property
    def width(self) -> int:
        """Return the width of the fish sprite in pixels."""
        return self.base_img.get_width()

    def _respawn(self) -> None:
        """Respawn the fish at the left or right edge, randomly choosing a direction."""
        self.moving_right = random.choice([True, False])
        self.x = -self.width if self.moving_right else float(self.screen_width)
        self.y = self.home_y

    def update(self) -> None:
        """Update the fish's position, moving it across the screen and respawning if it exits."""
        if self.moving_right:
            self.x += self.speed
            if self.x >= self.screen_width:
                self._respawn()
        else:
            self.x -= self.speed
            if self.x + self.width <= 0:
                self._respawn()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the fish on the provided surface, applying horizontal flipping if needed.

        Args:
            surface (pygame.Surface): The Pygame surface to draw the fish on.
        """
        should_flip = self.moving_right != self.faces_right
        img = pygame.transform.flip(self.base_img, should_flip, False)
        surface.blit(img, (int(self.x), int(self.y)))

# Unlike the others, FishHabitat inherits directly from Scene instead of HabitatScene
class FishHabitat(Scene):
    """A scene representing the aquarium habitat with multiple swimming fish.
    """
    BACKGROUND_FILE = "aquarium_background.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize the FishHabitat scene.

        Args:
            manager (SceneManager): The scene manager controlling scene transitions.
        """
        super().__init__(manager)
        self._background: pygame.Surface | None = None
        self._fish: list[_Fish] = []
        self._base_dir = os.path.dirname(os.path.abspath(__file__))

    def on_enter(self) -> None:
        """Called when entering the FishHabitat scene.
        """
        super().on_enter()
        bg_path = os.path.join(self._base_dir, "assets", "images", self.BACKGROUND_FILE)
        screen_size = Settings().window["size"]
        if os.path.exists(bg_path):
            bg = pygame.image.load(bg_path).convert()
            self._background = pygame.transform.smoothscale(bg, screen_size)
        else:
            self._background = None

        screen_width = screen_size[0]
        fish_dir = os.path.join(self._base_dir, _SUBFOLDER)
        margin_x = 60
        x_gap = (screen_width - margin_x * 2) // 4

        self._fish = []
        for i, (fname, faces_right, size_px, y, speed) in enumerate(_FISH_INFO):
            path = os.path.join(fish_dir, fname)
            x = margin_x + (i % 4) * x_gap
            self._fish.append(_Fish(path, faces_right, size_px, x, y, speed, screen_width))

    def on_exit(self) -> None:
        """Called when exiting the FishHabitat scene.
        """
        super().on_exit()
        self._background = None
        self._fish = []

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle keyboard events within the FishHabitat scene.

        Args:
            events (list[pygame.event.Event]): List of Pygame events to process.
        """
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from pause_scene import PauseScene
                self._manager.push(PauseScene(self._manager))

    def update(self, dt: float) -> None:
        """Update all fish positions in the aquarium.

        Args:
            dt (float): Time delta since the last update (unused here but consistent with other scenes).
        """
        for fish in self._fish:
            fish.update()

    def draw(self, screen: pygame.Surface) -> None:
        """Render the aquarium background and all fish onto the screen.

        Args:
            screen (pygame.Surface): The Pygame surface to draw the scene on.
        """
        if self._background:
            screen.blit(self._background, (0, 0))
        else:
            screen.fill((30, 100, 180))

        for fish in self._fish:
            fish.draw(screen)