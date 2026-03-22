import pygame
import os

class Animal:
    HABITAT_BACKGROUNDS = {
        "Jungle": "jungle_background.png",
        "Savanna": "savanna_background.png",
        "Grassland": "grassland_background.png",
        "Aquarium": "aquarium_background.png",
    }

    def __init__(self, x, y, scale, layer_files, subfolder=None):
        self.x = x
        self.y = y

        self.speed = 1
        self.direction = 1
        self.facing_left = False
        self.default_facing_left = False

        self.scale = scale

        base = os.path.dirname(__file__)

        if subfolder:
            base = os.path.join(base, subfolder)

        self.layers = [
            self.load_and_scale(os.path.join(base, file))
            for file in layer_files
        ]

    def load_and_scale(self, path):
        img = pygame.image.load(path).convert_alpha()
        width = int(img.get_width() * self.scale)
        height = int(img.get_height() * self.scale)
        return pygame.transform.scale(img, (width, height))

    def update(self, screen_width):
        self.move(screen_width)

    def move(self, screen_width):
        self.x += self.speed * self.direction

        width = max(layer.get_width() for layer in self.layers)

        if self.x > screen_width - width:
            self.x = screen_width - width
            self.direction = -1

        elif self.x < 0:
            self.x = 0
            self.direction = 1

        self.facing_left = self.direction < 0

    def draw(self, screen):
        for layer in self.layers:
            should_flip = self.facing_left != self.default_facing_left

            if should_flip:
                layer = pygame.transform.flip(layer, True, False)
            screen.blit(layer, (self.x, self.y))

    @classmethod
    def get_background_path(cls):
        filename = cls.HABITAT_BACKGROUNDS.get(cls.HABITAT_NAME)

        if not filename:
            return None

        # 👇 FIXED PATH (this is important)
        base = os.path.dirname(__file__)  # assets/animals
        return os.path.abspath(os.path.join(base, "..", "images", filename))