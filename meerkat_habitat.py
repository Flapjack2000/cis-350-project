import os
import math
import pygame
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal
from animal_movement import AnimalMovement

movement = AnimalMovement()

_SUBFOLDER = os.path.join("assets", "animals", "meerkat")

_LAYERS_V1 = ["1_meerkat_body.png", "1_meerkat_head.png"]
_LAYERS_V2 = ["2_meerkat_body.png", "2_meerkat_head.png"]

_LAYERS_V3 = [
    "3_meerkat_hind_back.png",
    "3_meerkat_hind_front.png",
    "3_meerkat_tail.png",
    "3_meerkat_body.png",
    "3_meerkat_fore_hind.png",
    "3_meerkat_fore_front.png",
    "3_meerkat_head.png",
]

HB = 0
HF = 1
TAIL = 2
BODY = 3
FH = 4
FF = 5
HEAD = 6


def meerkat_v3_walk(animal, dt):
    """
    Animates the running meerkat model by applying sinusoidal motion to limbs, tail, and head.

    Args:
        animal (Animal): The meerkat instance containing animation state and layer angles.
    """
    t = animal.time
    swing = math.sin(t * 10) * 10

    animal.layer_angles[HB] = swing
    animal.layer_angles[HF] = -swing

    animal.layer_angles[FH] = -swing
    animal.layer_angles[FF] = swing

    animal.layer_angles[TAIL] = math.sin(t * 3) * 6

    animal.layer_angles[HEAD] = math.sin(t * 4) * 2


def meerkat_draw(animal, screen):
    """
    Renders a meerkat using layered sprites with optional animation offsets and flipping.

    Args:
        animal (Animal): The meerkat instance containing sprite layers, position, and animation data.
        screen (pygame.Surface): The surface onto which the meerkat is drawn.
    """
    should_flip = animal.facing_left != animal.default_facing_left
    body_width = animal.layers[0].get_width() if animal.layers else 0
    body_pos = pygame.Vector2(animal.x + body_width / 2, animal.y)

    t = animal.time

    if "1_" in animal.layer_files[0]:
        phase = 0
    elif "2_" in animal.layer_files[0]:
        phase = math.pi
    else:
        phase = 0

    head_bob = math.sin(t * 4 + phase) * 5

    for i, (layer, angle) in enumerate(zip(animal.layers, animal.layer_angles)):
        name = animal.layer_files[i]

        rotated_img, rotated_rect = movement.rotate_image(
            layer,
            angle,
            pygame.Vector2(layer.get_width() // 2, layer.get_height() // 2)
        )

        pos = body_pos

        if ("1_" in name or "2_" in name) and "head" in name:
            pos = pygame.Vector2(body_pos.x, body_pos.y + head_bob)

        rotated_rect.center = pos

        if should_flip:
            rotated_img = pygame.transform.flip(rotated_img, True, False)

        screen.blit(rotated_img, rotated_rect)


class MeerkatHabitat(HabitatScene):
    """Habitat scene representing meerkats in a grassland environment.

    Handles creating multiple meerkat animals with different sprite layers
    and manages their movement within the scene.
    """
    BACKGROUND_FILE_DAY = "grassland_background_day.png"
    BACKGROUND_FILE_NIGHT = "grassland_background_night.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize the MeerkatHabitat scene.

        Args:
            manager (SceneManager): The scene manager controlling scene transitions.
        """
        self.BACKGROUND_FILE = self.BACKGROUND_FILE_DAY if manager.context.is_day else self.BACKGROUND_FILE_NIGHT
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        """Create and return a list of meerkat Animal instances for this habitat.

        Returns:
            list[Animal]: The meerkat animals in the scene, each with its sprite layers, position, and movement parameters.
        """
        return [
            Animal(
                x=200, y=350,
                layer_files=_LAYERS_V1,
                subfolder=_SUBFOLDER,
                scale=0.65,
                speed=0,
                animate_fn=None,
                draw_fn=meerkat_draw,
            ),
            Animal(
                x=500, y=250,
                layer_files=_LAYERS_V2,
                subfolder=_SUBFOLDER,
                scale=0.65,
                speed=0,
                animate_fn=None,
                draw_fn=meerkat_draw,
            ),

            Animal(
                x=700, y=150,
                layer_files=_LAYERS_V3,
                subfolder=_SUBFOLDER,
                scale=0.75,
                direction=1,
                speed=4,
                animate_fn=meerkat_v3_walk,
                draw_fn=meerkat_draw,
            ),
            Animal(
                x=850, y=450,
                layer_files=_LAYERS_V3,
                subfolder=_SUBFOLDER,
                scale=0.75,
                direction=-1,
                speed=4,
                animate_fn=meerkat_v3_walk,
                draw_fn=meerkat_draw,
                has_droppings=True,
            ),
        ]