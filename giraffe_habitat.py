import os
import math
import pygame

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal
from animal_movement import AnimalMovement

movement = AnimalMovement()

_SUBFOLDER = os.path.join("assets", "animals", "giraffe")

_LAYER_FILES = [
    "giraffe_neck.png",
    "giraffe_hind_back_upper.png",
    "giraffe_hind_back_lower.png",
    "giraffe_hind_front_upper.png",
    "giraffe_hind_front_lower.png",
    "giraffe_tail.png",
    "giraffe_body.png",
    "giraffe_fore_back_upper.png",
    "giraffe_fore_back_lower.png",
    "giraffe_fore_front_upper.png",
    "giraffe_fore_front_lower.png",
    "giraffe_head.png",
]

FRONT_LEG_PIVOT = pygame.Vector2(25, 15)
HIND_LEG_PIVOT = pygame.Vector2(25, 15)


def giraffe_walk(animal, dt):
    """
    This function modifies the `layer_angles` of the animal to simulate a walking gait.
    Each leg group is animated with opposite phase to create a natural alternating step cycle.

    Args:
        animal (Animal): The giraffe animal instance containing animation state and layer angles.
    """
    t = animal.time
    swing = math.sin(t * 4) * 10

    HBU, HBL = 1, 2
    HFU, HFL = 3, 4

    FBU, FBL = 7, 8
    FFU, FFL = 9, 10

    animal.layer_angles[HBU] = swing
    animal.layer_angles[HBL] = swing * 0.9

    animal.layer_angles[HFU] = -swing
    animal.layer_angles[HFL] = -swing * 0.9

    animal.layer_angles[FBU] = -swing
    animal.layer_angles[FBL] = -swing * 0.9

    animal.layer_angles[FFU] = swing
    animal.layer_angles[FFL] = swing * 0.9


def giraffe_draw(animal, screen):
    """
    Renders the giraffe by drawing each sprite layer with appropriate rotation and pivot points.

    Args:
        animal (Animal): The giraffe instance containing sprite layers, angles, and position data.
        screen (pygame.Surface): The surface to render the giraffe onto.
    """
    should_flip = animal.facing_left != animal.default_facing_left
    body_width = animal.layers[6].get_width() if animal.layers else 0
    body_pos = pygame.Vector2(animal.x + body_width / 2, animal.y)

    offsets = [(0, 0)] * len(animal.layers)

    pivots = []

    for i, layer in enumerate(animal.layers):
        name = animal.layer_files[i]

        if "hind_back_upper" in name or "hind_front_upper" in name:
            pivots.append(HIND_LEG_PIVOT)
        elif "fore_back_upper" in name or "fore_front_upper" in name:
            pivots.append(FRONT_LEG_PIVOT)
        else:
            pivots.append(
                pygame.Vector2(
                    layer.get_width() // 2,
                    layer.get_height() // 2
                )
            )

    for i, (layer, angle) in enumerate(zip(animal.layers, animal.layer_angles)):
        offset = pygame.Vector2(offsets[i])

        if should_flip:
            offset.x = -offset.x

        world_pos = body_pos + offset

        rotated_img, rotated_rect = movement.rotate_image(
            layer,
            angle,
            pivots[i]
        )

        rotated_rect.center = world_pos

        if should_flip:
            rotated_img = pygame.transform.flip(rotated_img, True, False)

        screen.blit(rotated_img, rotated_rect)


class GiraffeHabitat(HabitatScene):
    """Habitat scene representing giraffes in a savanna environment."""
    BACKGROUND_FILE = "savanna_background_day.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize the GiraffeHabitat scene.

        Args:
            manager (SceneManager): The scene manager controlling scene transitions.
        """
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        """Create and return a list of giraffe Animal instances for this habitat.

        Returns:
            list[Animal]: The giraffe animals in the scene, each with its sprite layers, position, and movement parameters.
        """
        return [
            Animal(
                x=200, y=500,
                layer_files=_LAYER_FILES,
                subfolder=_SUBFOLDER,
                scale=0.5,
                default_facing_left=True,
                direction=1,
                speed=0.8,
                draw_fn=giraffe_draw,
                animate_fn=giraffe_walk,
            ),
            Animal(
                x=600, y=300,
                layer_files=_LAYER_FILES,
                subfolder=_SUBFOLDER,
                scale=0.5,
                default_facing_left=True,
                direction=-1,
                speed=1.4,
                draw_fn=giraffe_draw,
                animate_fn=giraffe_walk,
            ),
        ]