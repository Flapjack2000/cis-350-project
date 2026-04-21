import os
import math
import pygame

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal
from animal_movement import AnimalMovement

_SUBFOLDER = os.path.join("assets", "animals", "octopus")
TENTACLE_PIVOT = pygame.Vector2(100, 400)


class OctopusHabitat(HabitatScene):
    """Habitat scene for an octopus in an aquatic environment.

    Minigames:
    - Pet: Hold the cursor over the octopus.
    """

    BACKGROUND_FILE_DAY = "aquatic_background_day.png"
    BACKGROUND_FILE_NIGHT = "aquatic_background_night.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize aquatic habitat state."""
        self.BACKGROUND_FILE = (
            self.BACKGROUND_FILE_DAY
            if manager.context.is_day
            else self.BACKGROUND_FILE_NIGHT
        )
        super().__init__(manager)

        self._movement = AnimalMovement()
        incomplete = manager.context.checklist.get_incomplete_tasks()

        # Task activation - Pet only
        self._pet_task_active = "octopus_pet" in incomplete

        self._build_toolbar()

    def create_animals(self) -> list[Animal]:
        """Return a stationary octopus with tentacle animation."""
        return [
            Animal(
                x=200,
                y=200,
                layer_files=["octopus_body.png", "octopus_tentacle.png"],
                subfolder=_SUBFOLDER,
                scale=1.0,
                speed=0.0,
                animate_fn=self._animate,
                draw_fn=self._draw_animal,
                rect_size=(500, 500)
            )
        ]

    @staticmethod
    def _animate(animal: Animal) -> None:
        """Apply sinusoidal tentacle motion."""
        animal.tentacle_angle = math.sin(animal.time * 3) * 25

    def _draw_animal(self, animal: Animal, screen: pygame.Surface) -> None:
        """Render octopus layers (body and tentacle) with pivots."""
        if not animal.layers:
            return

        body = animal.layers[0]
        tentacle = animal.layers[1]

        screen.blit(body, (int(animal.x), int(animal.y)))

        angle = getattr(animal, "tentacle_angle", 0)
        rotated_tentacle, rect = self._movement.rotate_image(
            tentacle, angle, (TENTACLE_PIVOT.x, TENTACLE_PIVOT.y)
        )

        rect.x += int(animal.x)
        rect.y += int(animal.y)
        screen.blit(rotated_tentacle, rect)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle standard habitat input."""
        super().handle_events(events)

    def update(self, dt: float) -> None:
        """Update animal state and petting progress."""
        super().update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        """Render background, octopus, and toolbar."""
        super().draw(screen)

    def _on_pet_complete(self) -> None:
        """Mark pet task complete and return to checklist."""
        self._manager.context.checklist.complete_task("octopus_pet")
        from checklist_scene import ChecklistScene
        self._manager.push(
            ChecklistScene(self._manager, self._manager.context.checklist)
        )
