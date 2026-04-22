import os
import pygame
from typing import Callable


class Animal:
    """Represents an animated animal with multiple
    sprite layers that can move and be drawn.
    """

    def __init__(
            self,
            x: int,
            y: int,
            layer_files: list[str],
            subfolder: str,
            scale: float = 1.0,
            default_facing_left: bool = False,
            direction: int = 1,
            speed: float = 1.0,
            draw_fn: Callable[["Animal", pygame.Surface], None] | None = None,

            # a function that takes in an Animal and dt
            animate_fn: Callable[["Animal"], None] | None = None,
            rect_size: tuple[int, int] | None = None,
            has_droppings: bool = False,
    ) -> None:
        """Initialize an Animal instance.

        Args:
            x (int): Initial x-coordinate of the animal.
            y (int): Initial y-coordinate of the animal.
            layer_files (list[str]):
                Filenames of sprite layers for this animal.
            subfolder (str):
                Subfolder under base directory where sprites are located.
            scale (float, optional):
                Scaling factor for sprite images. Defaults to 1.0.
            default_facing_left (bool, optional):
                Whether the animal faces left by default. Defaults to False.
            direction (int, optional):
                Initial hori. direction (1 = right, -1 = left). Default = 1.
            speed (float, optional):
                Horizontal movement speed. Defaults to 1.0.
            animate_fn (Callable[[Animal, float], None] | None, optional):
                Custom animation function called each update. Defaults to None.
        """
        self.x: float = x
        self.y: float = y
        self.layer_files = layer_files
        self.subfolder = subfolder
        self.scale = scale
        self.default_facing_left = default_facing_left
        self.direction = direction
        self.speed = speed
        self.facing_left: bool = direction < 0
        self.layers: list[pygame.Surface] = []
        self.layer_angles: list[float] = []  # per-layer rotation in degrees
        self._draw_fn = draw_fn
        self._animate_fn = animate_fn
        self.time: float = 0.0  # elapsed seconds, available to animate_fn
        self.rect_size = rect_size  # optional (w, h) override for hit-testing
        self.has_droppings = has_droppings  # optional for droppings minigame

    def load(self, base_dir: str) -> None:
        """Load sprite layers from disk. Called by HabitatScene.on_enter().

        Args:
            base_dir (str):
                Base directory containing the animal's sprite subfolder.
        """
        folder = os.path.join(base_dir, self.subfolder)
        self.layers = []
        for filename in self.layer_files:
            img = pygame.image.load(
                os.path.join(folder, filename)
            ).convert_alpha()
            self.layers.append(
                pygame.transform.scale(
                    img,
                    (
                        int(img.get_width() * self.scale),
                        int(img.get_height() * self.scale)
                    ),
                )
            )
        self.layer_angles = [0.0] * len(self.layers)

    def update(self, screen_width: int, dt: float = 0.0) -> None:
        """Advance the animal's position,
        handle screen-edge bouncing, and run custom animation.

        Args:
            screen_width (int): Width of the screen to handle edge collisions.
            dt (float, optional):
                Time delta since last update in seconds. Defaults to 0.0.
        """
        self.time += dt
        self.x += self.speed * self.direction

        body_width = getattr(self, "body_width", None)

        if body_width is None:
            body_width = self.layers[0].get_width() if self.layers else 0

        if self.x > screen_width - body_width:
            self.x = screen_width - body_width
            self.direction = -1
        elif self.x < 0:
            self.x = 0
            self.direction = 1

        self.facing_left: bool = self.direction < 0

        if self._animate_fn:
            self._animate_fn(self)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw all sprite layers at the current position,
        applying rotation and horizontal flipping.

        Args:
            screen (pygame.Surface):
                The Pygame surface to draw the animal on.
        """
        if self._draw_fn:
            self._draw_fn(self, screen)
            return

        should_flip = self.facing_left != self.default_facing_left
        for layer, angle in zip(self.layers, self.layer_angles):
            if should_flip:
                layer = pygame.transform.flip(layer, True, False)
            if angle:
                layer = pygame.transform.rotate(layer, angle)
            screen.blit(layer, (self.x, self.y))
