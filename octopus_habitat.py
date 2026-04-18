import os
import math
import pygame

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal
from animal_movement import AnimalMovement

movement = AnimalMovement()

_SUBFOLDER = os.path.join("assets", "animals", "octopus")

TENTACLE_PIVOT = pygame.Vector2(100, 400)


def octopus_anim(animal, dt):
    """
    Animates the octopus by applying a sinusoidal motion to its tentacle.

    Args:
        animal (Animal): The octopus instance containing animation state variables.
    """
    t = animal.time
    animal.tentacle_angle = math.sin(t * 3) * 25

def octopus_draw(animal, screen):
    """
    Renders an octopus using a simple two-part sprite system (body + tentacle).

    Args:
        animal (Animal): The octopus instance containing position and animation state.
        screen (pygame.Surface): The surface to render the octopus onto.
    """
    if not hasattr(animal, "assets_loaded"):

        animal.body = pygame.image.load(
            os.path.join(_SUBFOLDER, "octopus_body.png")
        ).convert_alpha()

        animal.tentacle = pygame.image.load(
            os.path.join(_SUBFOLDER, "octopus_tentacle.png")
        ).convert_alpha()

        animal.assets_loaded = True

    screen.blit(animal.body, (int(animal.x), int(animal.y)))

    def draw_part(img, pivot, angle):
        """
        Rotates and renders a tentacle segment around a pivot point.

        Args:
            img (pygame.Surface): Image to rotate and draw.
            pivot (pygame.Vector2): Pivot point for rotation.
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
        animal.tentacle,
        TENTACLE_PIVOT,
        animal.tentacle_angle,
    )


class OctopusHabitat(HabitatScene):
    """
    Habitat scene representing an octopus in an aquatic environment.
    """
    BACKGROUND_FILE = "aquatic_background_day.png"

    def __init__(self, manager: SceneManager) -> None:
        """
        Initializes the OctopusHabitat scene.

        Args:
            manager (SceneManager): Scene manager responsible for handling scene transitions.
        """
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        """
        Creates and returns the octopus animal for this habitat.
        """
        return [
            Animal(
                x=200,
                y=200,
                layer_files=[],
                subfolder=_SUBFOLDER,
                scale=1,
                default_facing_left=False,
                direction=1,
                speed=0,
                draw_fn=octopus_draw,
                animate_fn=octopus_anim,
            ),
        ]