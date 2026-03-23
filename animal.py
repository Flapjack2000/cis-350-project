import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from typing import Callable


class Animal:
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
        animate_fn: Callable[["Animal", float], None] | None = None, # a function that takes in an Animal and dt
    ) -> None:
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
        self._animate_fn = animate_fn
        self.time: float = 0.0  # elapsed seconds, available to animate_fn

    def load(self, base_dir: str) -> None:
        """Load sprite layers from disk. Called by HabitatScene.on_enter()."""
        folder = os.path.join(base_dir, self.subfolder)
        self.layers = []
        for filename in self.layer_files:
            img = pygame.image.load(os.path.join(folder, filename)).convert_alpha()
            self.layers.append(
                pygame.transform.scale(
                    img,
                    (int(img.get_width() * self.scale), int(img.get_height() * self.scale)),
                )
            )
        self.layer_angles = [0.0] * len(self.layers)

    def update(self, screen_width: int, dt: float = 0.0) -> None:
        """Advance position, bounce off screen edges, and run animation."""
        self.time += dt
        self.x += self.speed * self.direction
        width = max((layer.get_width() for layer in self.layers), default=0)

        if self.x > screen_width - width:
            self.x = screen_width - width
            self.direction = -1
        elif self.x < 0:
            self.x = 0
            self.direction = 1

        self.facing_left = self.direction < 0

        if self._animate_fn:
            self._animate_fn(self, dt)

    def draw(self, screen: pygame.Surface) -> None:
        """Blit all layers at the animal's current position, with per-layer rotation."""
        should_flip = self.facing_left != self.default_facing_left
        for layer, angle in zip(self.layers, self.layer_angles):
            if should_flip:
                layer = pygame.transform.flip(layer, True, False)
            if angle:
                layer = pygame.transform.rotate(layer, angle)
            screen.blit(layer, (self.x, self.y))