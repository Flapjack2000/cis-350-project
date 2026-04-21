import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import math
import pygame

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal
from animal_movement import AnimalMovement

movement = AnimalMovement()

_SUBFOLDER = os.path.join("assets", "animals", "lion")

_LAYERS_BASE = [
    "lion_hind_back_upper.png",
    "lion_hind_back_lower.png",
    "lion_hind_back_paw.png",
    "lion_hind_front_upper.png",
    "lion_hind_front_lower.png",
    "lion_hind_front_paw.png",
    "lion_tail.png",
    "lion_body.png",
    "lion_fore_back_upper.png",
    "lion_fore_back_lower.png",
    "lion_fore_back_paw.png",
    "lion_fore_front_upper.png",
    "lion_fore_front_lower.png",
    "lion_fore_front_paw.png",
    "lion_neck.png",
]

_LAYERS_MALE   = _LAYERS_BASE + ["lion_mane.png", "lion_head.png"]
_LAYERS_FEMALE = _LAYERS_BASE + ["lion_head.png"]

FRONT_LEG_PIVOT = pygame.Vector2(25, 15)
HIND_LEG_PIVOT = pygame.Vector2(25, 15)


def lion_walk(animal, dt):
    """
    Animates a lion's walking motion by applying sinusoidal rotation to limb segments.

    Args:
        animal (Animal): The lion instance containing animation state and layer angle data.
    """
    t = animal.time
    swing = math.sin(t * 6) * 10

    HBU, HBL = 0, 1
    HFU, HFL = 3, 4

    FBU, FBL = 8, 9
    FFU, FFL = 11, 12

    PAW_OFF = 2

    animal.layer_angles[HBU] = swing
    animal.layer_angles[HBL] = swing
    animal.layer_angles[HBU + PAW_OFF] = swing

    animal.layer_angles[HFU] = -swing
    animal.layer_angles[HFL] = -swing
    animal.layer_angles[HFU + PAW_OFF] = -swing

    animal.layer_angles[FBU] = -swing
    animal.layer_angles[FBL] = -swing
    animal.layer_angles[FBU + PAW_OFF] = -swing

    animal.layer_angles[FFU] = swing
    animal.layer_angles[FFL] = swing
    animal.layer_angles[FFU + PAW_OFF] = swing


def lion_draw(animal, screen):
    """
    Renders a lion by drawing layered sprite components with rotation and pivot-based animation.

    Args:
        animal (Animal): The lion instance containing sprite layers, position, and animation state.
        screen (pygame.Surface): The surface onto which the lion is rendered.
    """
    should_flip = animal.facing_left != animal.default_facing_left
    body_width = animal.layers[8].get_width() if animal.layers else 0
    body_pos = pygame.Vector2(animal.x + body_width / 2 , animal.y)

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


class LionHabitat(HabitatScene):
    """Habitat scene representing lions in a savanna environment.

    Handles creating male and female lion animals with multiple sprite layers
    and manages their movement within the scene.
    """
    BACKGROUND_FILE_DAY = "savanna_background_day.png"
    BACKGROUND_FILE_NIGHT = "savanna_background_night.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize the LionHabitat scene.

        Args:
            manager (SceneManager): The scene manager controlling scene transitions.
        """
        self.BACKGROUND_FILE = self.BACKGROUND_FILE_DAY if manager.context.is_day else self.BACKGROUND_FILE_NIGHT
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        """Create and return a list of lion Animal instances for this habitat.

        Returns:
            list[Animal]: The lion animals in the scene, each with its sprite layers, position, and movement parameters.
        """
        return [
            Animal(
                x=200, y=500,
                layer_files=_LAYERS_MALE,
                subfolder=_SUBFOLDER,
                scale=0.45,
                default_facing_left=True,
                direction=1,
                speed=1.0,
                draw_fn=lion_draw,
                animate_fn=lion_walk,
            ),
            Animal(
                x=600, y=200,
                layer_files=_LAYERS_FEMALE,
                subfolder=_SUBFOLDER,
                scale=0.45,
                default_facing_left=True,
                direction=-1,
                speed=1.4,
                draw_fn=lion_draw,
                animate_fn=lion_walk,
                has_droppings=True,
            ),
        ]