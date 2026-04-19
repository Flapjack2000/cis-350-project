import os
import math
import pygame

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal
from animal_movement import AnimalMovement

movement = AnimalMovement()

_SUBFOLDER = os.path.join("assets", "animals", "redpanda")

TAIL_PIVOT = pygame.Vector2(300, 150)  # adjust if needed


def redpanda_anim(animal, dt):
    """
    Animates the red panda by applying a sinusoidal tail motion.

    Args:
        animal (Animal): The red panda instance containing animation state.
    """
    t = animal.time

    animal.tail_angle = math.sin(t * 2) * 15


def redpanda_draw(animal, screen):
    """
    Renders a red panda using a simple two-part sprite system (body + tail).

    Args:
        animal (Animal): The red panda instance containing position and animation state.
        screen (pygame.Surface): The surface to render the red panda onto.
    """
    if not hasattr(animal, "assets_loaded"):

        animal.body = pygame.image.load(
            os.path.join(_SUBFOLDER, "red_panda.png")
        ).convert_alpha()

        animal.tail = pygame.image.load(
            os.path.join(_SUBFOLDER, "red_panda_tail.png")
        ).convert_alpha()

        animal.assets_loaded = True

    screen.blit(animal.body, (int(animal.x), int(animal.y)))

    def draw_part(img, pivot, angle):
        """
        Rotates and draws a sprite part around a pivot point.

        Args:
            img (pygame.Surface): Image to rotate and render.
            pivot (pygame.Vector2): Rotation pivot point relative to image space.
            angle (float): Rotation angle in degrees.
        """
        rotated_img, rect = movement.rotate_image(
            img,
            angle,
            (pivot.x, pivot.y),
        )

        rect.x += int(animal.x)
        rect.y += int(animal.y)

        screen.blit(rotated_img, rect)

    draw_part(
        animal.tail,
        TAIL_PIVOT,
        animal.tail_angle,
    )


class RedPandaHabitat(HabitatScene):
    """
    Habitat scene representing a red panda in a jungle environment.
    """
    BACKGROUND_FILE_DAY = "jungle_background_day.png"
    BACKGROUND_FILE_NIGHT = "jungle_background_night.png"

    def __init__(self, manager: SceneManager) -> None:
        """
        Initializes the RedPandaHabitat scene.

        Args:
            manager (SceneManager): Scene manager responsible for handling scene transitions.
        """
        self.BACKGROUND_FILE = self.BACKGROUND_FILE_DAY if manager.context.is_day else self.BACKGROUND_FILE_NIGHT
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        """
        Creates and returns the red panda animal for this habitat.
        """
        return [
            Animal(
                x=200,
                y=200,
                layer_files=[],  # not used in this simplified system
                subfolder=_SUBFOLDER,
                scale=1,
                default_facing_left=False,
                direction=1,
                speed=0,
                draw_fn=redpanda_draw,
                animate_fn=redpanda_anim,
            ),
        ]