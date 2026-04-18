import os
from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal
import math
import pygame
from animal_movement import AnimalMovement

movement = AnimalMovement()

_SUBFOLDER = os.path.join("assets", "animals", "tiger")

_LAYER_FILES = [
    "tiger_hind_back_lower.png",
    "tiger_hind_back_upper.png",
    "tiger_hind_back_paw.png",
    "tiger_hind_front_lower.png",
    "tiger_hind_front_upper.png",
    "tiger_hind_front_paw.png",
    "tiger_tail.png",
    "tiger_body.png",
    "tiger_neck.png",
    "tiger_head.png",
    "tiger_fore_back_lower.png",
    "tiger_fore_back_upper.png",
    "tiger_fore_back_paw.png",
    "tiger_fore_front_lower.png",
    "tiger_fore_front_upper.png",
    "tiger_fore_front_paw.png",
]

BODY_INDEX = 7

FRONT_LEG_PIVOT = pygame.Vector2(25, 15)
HIND_LEG_PIVOT = pygame.Vector2(25, 15)


def tiger_walk(animal, dt):
    """
    Animates a tiger's walking motion by applying sinusoidal rotation to its limb layers.

    Args:
        animal (Animal): The tiger instance containing animation state and layer angle data.
    """
    t = animal.time
    swing = math.sin(t * 6) * 15

    HBL, HBU = 0, 1
    HFL, HFU = 3, 4
    FBL, FBU = 10, 11
    FFL, FFU = 13, 14
    PAW_OFF = 1

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


def tiger_draw(animal, screen):
    """
    Renders a tiger using layered sprite animation with pivot-based rotation.

    Args:
        animal (Animal): The tiger instance containing sprite layers, position, and animation state.
        screen (pygame.Surface): The surface to render the tiger onto.
    """
    should_flip = animal.facing_left != animal.default_facing_left
    body_width = animal.layers[7].get_width() if animal.layers else 0
    body_pos = pygame.Vector2(animal.x + body_width / 2, animal.y)

    offsets = [(0, 0)] * len(animal.layers)

    pivots = []

    for i, layer in enumerate(animal.layers):
        name = _LAYER_FILES[i]
        if "hind_back_upper" in name or "hind_front_upper" in name:
            pivots.append(HIND_LEG_PIVOT)
        elif "fore_back_upper" in name or "fore_front_upper" in name:
            pivots.append(FRONT_LEG_PIVOT)
        else:
            pivots.append(
                pygame.Vector2(layer.get_width() // 2,
                               layer.get_height() // 2)
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


class TigerHabitat(HabitatScene):
    """Habitat scene representing tigers in a jungle environment.

    Handles creating tiger animals with layered sprites,
    movement, and rendering within the scene.
    """
    BACKGROUND_FILE = "jungle_background_day.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize the TigerHabitat scene.

        Args:
            manager (SceneManager): The object controlling scene transitions.
        """
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        """Return a list of tiger Animal instances for this habitat.

        Returns:
            list[Animal]: The tiger animals in the scene,
            each with its sprite layers, position, and movement settings.
        """
        return [
            Animal(
                x=200, y=300,
                layer_files=_LAYER_FILES,
                subfolder=_SUBFOLDER,
                scale=0.4,
                default_facing_left=False,
                direction=1,
                speed=1.0,
                draw_fn=tiger_draw,
                animate_fn=tiger_walk,
            ),
            Animal(
                x=600, y=500,
                layer_files=_LAYER_FILES,
                subfolder=_SUBFOLDER,
                scale=0.4,
                default_facing_left=False,
                direction=-1,
                speed=1.4,
                draw_fn=tiger_draw,
                animate_fn=tiger_walk,
            ),
        ]