import os
import math
import pygame

from math_helper import MathHelper
from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal

_SUBFOLDER = os.path.join("assets", "animals", "rattlesnake")
TAIL_PIVOT = pygame.Vector2(250, 335)
HEAD_PIVOT = pygame.Vector2(250, 220)
HISS_CYCLE = 4.0
HISS_DURATION = 0.8

# Map to store snake-specific states to avoid Animal attribute warnings
_snake_states = {}


class RattlesnakeHabitat(HabitatScene):
    """Habitat scene for a rattlesnake in a grassland environment.

    Minigames:
    - Pet: Hold the cursor over the rattlesnake.
    """

    BACKGROUND_FILE_DAY = "grassland_background_day.png"
    BACKGROUND_FILE_NIGHT = "grassland_background_night.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize grassland habitat state."""
        self.BACKGROUND_FILE = (
            self.BACKGROUND_FILE_DAY
            if manager.context.is_day
            else self.BACKGROUND_FILE_NIGHT
        )
        super().__init__(manager)

        incomplete = manager.context.checklist.get_incomplete_tasks()

        # Task activation - Pet only
        self._pet_task_active = "rattlesnake_pet" in incomplete

        self._build_toolbar()

    def create_animals(self) -> list[Animal]:
        """Return a stationary rattlesnake with procedural animation.

        Returns:
            list[Animal]: the snake
        """
        snake = Animal(
            x=300,
            y=300,
            layer_files=[
                "rattlesnake_body.png",
                "rattlesnake_tail.png",
                "rattlesnake_head.png",
                "rattlesnake_tongue.png",
            ],
            subfolder=_SUBFOLDER,
            scale=1.0,
            speed=0.0,
            animate_fn=self._animate,
            draw_fn=self._draw_animal,
            rect_size=(450, 450),
        )

        # Initialize the local state for this snake instance
        _snake_states[snake] = {
            "hissing": False,
            "tail_angle": 0.0,
            "head_angle": 0.0,
            "tongue_angle": 0.0
        }

        return [snake]

    @staticmethod
    def _animate(animal: Animal) -> None:
        """Update rattlesnake animation cycles using the state map.

        Args:
            animal (Animal): the rattlesnake to animate
        """
        if animal not in _snake_states:
            return

        state = _snake_states[animal]
        t = animal.time
        cycle = t % HISS_CYCLE

        is_hissing = cycle < HISS_DURATION
        state["hissing"] = is_hissing
        state["tail_angle"] = math.sin(t * 30) * 20 if is_hissing else 0
        state["head_angle"] = math.sin(t * 5) * 10
        state["tongue_angle"] = math.sin(t * 30 + math.pi / 4) * 15

    @staticmethod
    def _draw_animal(animal: Animal, screen: pygame.Surface) -> None:
        """Render layered snake parts using values from the state map.

        Args:
            animal (Animal): the rattlesnake to draw
            screen (pygame.Surface): the screen to draw on
        """
        if not animal.layers or animal not in _snake_states:
            return

        state = _snake_states[animal]
        body = animal.layers[0]
        tail = animal.layers[1]
        head = animal.layers[2]
        tongue = animal.layers[3]

        screen.blit(body, (int(animal.x), int(animal.y)))

        # Draw Tail
        rotated_tail, t_rect = MathHelper.rotate_image(
            tail, state["tail_angle"],
            pygame.Vector2(TAIL_PIVOT.x, TAIL_PIVOT.y)
        )
        screen.blit(
            rotated_tail,
            (int(animal.x) + t_rect.x, int(animal.y) + t_rect.y)
        )

        # Draw Head
        h_angle = state["head_angle"]
        rotated_head, h_rect = MathHelper.rotate_image(
            head, h_angle, pygame.Vector2(HEAD_PIVOT.x, HEAD_PIVOT.y)
        )
        screen.blit(
            rotated_head,
            (
                int(animal.x) + h_rect.x,
                int(animal.y) + h_rect.y
            )
        )

        # Draw Tongue (only when hissing)
        if state["hissing"]:
            tg_angle = state["tongue_angle"] + h_angle
            rotated_tongue, tg_rect = MathHelper.rotate_image(
                tongue, tg_angle, pygame.Vector2(HEAD_PIVOT.x, HEAD_PIVOT.y)
            )
            screen.blit(
                rotated_tongue,
                (
                    int(animal.x) + tg_rect.x,
                    int(animal.y) + tg_rect.y
                )
            )

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle mouse events and pausing.

        Args:
            events (list[pygame.event.Event]): the events to handle
        """

        super().handle_events(events)

    def update(self, dt: float) -> None:
        """Update game state.

        Args:
            dt (float): the time since the last frame
        """
        super().update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        """Render the scene.

        Args:
            screen (pygame.Surface): the screen to draw on
        """
        super().draw(screen)

    def _on_pet_complete(self) -> None:
        """Mark pet task complete and return to checklist."""
        self._manager.context.checklist.complete_task("rattlesnake_pet")
        from checklist_scene import ChecklistScene
        self._manager.pop()
        self._manager.push(
            ChecklistScene(self._manager, self._manager.context.checklist)
        )
