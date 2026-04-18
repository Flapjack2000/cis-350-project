import os
import math
import pygame

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal
from animal_movement import AnimalMovement

movement = AnimalMovement()

ASSET_FOLDER = os.path.join("assets", "animals", "rattlesnake")

HISS_CYCLE = 4.0
HISS_DURATION = 0.8

SHOW_PIVOTS = False


def load_img(name, scale):
    """
    Loads an image from the rattlesnake asset folder and applies scaling if needed.

    Args:
        name (str): Filename of the image to load.
        scale (float): Scaling factor applied to the image (1.0 = no scaling).
    """
    img = pygame.image.load(os.path.join(ASSET_FOLDER, name)).convert_alpha()
    if scale != 1.0:
        img = pygame.transform.scale(
            img,
            (int(img.get_width() * scale), int(img.get_height() * scale)),
        )
    return img


def rattlesnake_animate(animal, dt):
    """
    Updates rattlesnake animation state including tail, head, tongue motion, and hissing behavior.

    Args:
        animal (Animal): The rattlesnake instance containing animation state variables.
    """
    t = animal.time

    animal.tail_angle = math.sin(t * 30) * 20
    animal.head_angle = math.sin(t * 5) * 10
    animal.tongue_angle = math.sin(t * 30 + math.pi / 4) * 15

    cycle = t % HISS_CYCLE
    animal.hissing = cycle < HISS_DURATION


def rattlesnake_draw(animal, screen):
    """
    Renders a rattlesnake using a layered sprite system with procedural animation.

    Args:
        animal (Animal): The rattlesnake instance containing position, assets, and animation state.
        screen (pygame.Surface): The surface to render the snake onto.
    """
    if not hasattr(animal, "assets_loaded"):

        animal.body = load_img("rattlesnake_body.png", animal.scale)

        animal.parts = {

            "tail": {
                "img": load_img("rattlesnake_tail.png", animal.scale),
                "pivot": pygame.Vector2(250, 335) * animal.scale,
            },

            "head": {
                "img": load_img("rattlesnake_head.png", animal.scale),
                "pivot": pygame.Vector2(250, 220) * animal.scale,
            },

            "tongue": {
                "img": load_img("rattlesnake_tongue.png", animal.scale),

                # IMPORTANT:
                # Tongue pivot will temporarily inherit head pivot
                "pivot": pygame.Vector2(250, 220) * animal.scale,
            },
        }

        animal.assets_loaded = True

    screen.blit(animal.body, (int(animal.x), int(animal.y)))

    def draw_part(img, pivot, angle):
        """
        Draws a rotated snake body part around a pivot point.

        Args:
            img (pygame.Surface): The image to rotate and draw.
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

        if SHOW_PIVOTS:
            pygame.draw.circle(
                screen,
                (255, 0, 0),
                (int(animal.x + pivot.x), int(animal.y + pivot.y)),
                5,
            )

    tail_angle = animal.tail_angle
    head_angle = animal.head_angle
    tongue_angle = animal.tongue_angle

    if animal.hissing:
        draw_part(
            animal.parts["tail"]["img"],
            animal.parts["tail"]["pivot"],
            tail_angle,
        )
    else:
        draw_part(
            animal.parts["tail"]["img"],
            animal.parts["tail"]["pivot"],
            0,
        )

    draw_part(
        animal.parts["head"]["img"],
        animal.parts["head"]["pivot"],
        head_angle,
    )

    if animal.hissing:

        head_pivot = animal.parts["head"]["pivot"]

        tongue_pivot = head_pivot

        draw_part(
            animal.parts["tongue"]["img"],
            tongue_pivot,

            tongue_angle + head_angle,
        )


class RattlesnakeHabitat(HabitatScene):
    """Habitat scene representing rattlesnakes in a grassland environment.

    Handles creating rattlesnake animals with layered sprites and optional
    animation (head bobbing and tail rattling) within the scene.
    """
    BACKGROUND_FILE = "grassland_background_day.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize the RattlesnakeHabitat scene.

        Args:
            manager (SceneManager): The scene manager controlling scene transitions.
        """
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        """Create and return a list of rattlesnake Animal instances for this habitat.

        Returns:
            list[Animal]: The rattlesnake animals in the scene, each with its sprite layers, position, and optional animation function.
        """
        snake = Animal(
            x=300,
            y=300,
            layer_files=[],
            subfolder=ASSET_FOLDER,
            scale=1.0,
            default_facing_left=False,
            direction=0,
            speed=0,
            draw_fn=rattlesnake_draw,
            animate_fn=rattlesnake_animate,
        )

        snake.hissing = False
        snake.tail_angle = 0
        snake.head_angle = 0
        snake.tongue_angle = 0

        return [snake]