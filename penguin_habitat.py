import os
import math
import pygame

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal
from animal_movement import AnimalMovement

movement = AnimalMovement()

_SUBFOLDER = os.path.join("assets", "animals", "penguin")

WADDLE_SPEED = 6
WADDLE_AMPLITUDE = 10


def penguin_anim(animal, dt):
    """
    Animates a penguin using a waddle motion and subtle vertical bobbing.

    Args:
        animal (Animal): The penguin instance containing animation state variables.
    """
    t = animal.time

    speed_factor = abs(animal.direction * animal.speed)

    animal.waddle_angle = math.sin(t * WADDLE_SPEED) * WADDLE_AMPLITUDE * speed_factor

    animal.y_offset = math.sin(t * WADDLE_SPEED * 2) * 2 * speed_factor


def penguin_draw(animal, screen):
    """
    Renders a penguin using a single sprite with rotation and flipping.

    Args:
        animal (Animal): The penguin instance containing position and animation state.
        screen (pygame.Surface): The surface to render the penguin onto.
    """
    if not hasattr(animal, "assets_loaded"):

        img = pygame.image.load(
            os.path.join(_SUBFOLDER, "penguin.png")
        ).convert_alpha()

        if animal.scale != 1:
            img = pygame.transform.scale(
                img,
                (
                    int(img.get_width() * animal.scale),
                    int(img.get_height() * animal.scale),
                )
            )

        animal.img = img
        animal.assets_loaded = True

    img = animal.img

    animal.body_width = img.get_width()

    base_pivot = pygame.Vector2(
        img.get_width() // 2,
        img.get_height() - 15
    )

    should_flip = animal.facing_left != animal.default_facing_left

    draw_img = img
    draw_pivot = base_pivot

    if should_flip:
        draw_img = pygame.transform.flip(img, True, False)

        draw_pivot = pygame.Vector2(
            img.get_width() - base_pivot.x,
            base_pivot.y
        )

    rotated_img, rect = movement.rotate_image(
        draw_img,
        animal.waddle_angle,
        (draw_pivot.x, draw_pivot.y),
    )

    rect.x += int(animal.x)
    rect.y += int(animal.y + animal.y_offset)
    screen.blit(rotated_img, rect)


class PenguinHabitat(HabitatScene):
    """
    Habitat scene representing penguins in an aquatic environment.

    Attributes:
        BACKGROUND_FILE (str): Background image used for the aquatic environment.
    """
    BACKGROUND_FILE_DAY = "aquatic_background_day.png"
    BACKGROUND_FILE_NIGHT = "aquatic_background_night.png"

    def __init__(self, manager: SceneManager) -> None:
        """
        Initializes the PenguinHabitat scene.

        Args:
            manager (SceneManager): Scene manager responsible for handling scene transitions.
        """
        self.BACKGROUND_FILE = self.BACKGROUND_FILE_DAY if manager.context.is_day else self.BACKGROUND_FILE_NIGHT
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        """
        Creates and returns penguin animals for this habitat.

        Returns:
            list[Animal]: A list of initialized penguin Animal instances.
        """
        return [
            Animal(
                x=100, y=200,
                layer_files=[],
                subfolder=_SUBFOLDER,
                scale=0.7,
                default_facing_left=True,
                direction=1,
                speed=0.5,
                draw_fn=penguin_draw,
                animate_fn=penguin_anim,
            ),
            Animal(
                x=500, y=100,
                layer_files=[],
                subfolder=_SUBFOLDER,
                scale=0.7,
                default_facing_left=True,
                direction=1,
                speed=0.5,
                draw_fn=penguin_draw,
                animate_fn=penguin_anim,
            ),
        ]