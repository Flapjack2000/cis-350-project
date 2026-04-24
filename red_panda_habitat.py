import os
import math
import pygame

from math_helper import MathHelper
from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal

_SUBFOLDER = os.path.join("assets", "animals", "redpanda")
TAIL_PIVOT = pygame.Vector2(300, 150)


class RedPandaHabitat(HabitatScene):
    """Simple red panda habitat with pet + poop minigames."""

    BACKGROUND_FILE_DAY = "jungle_background_day.png"
    BACKGROUND_FILE_NIGHT = "jungle_background_night.png"
    _ICON_POOP = "poop_icon.png"

    def __init__(self, manager: SceneManager) -> None:
        """
        Initializes the RedPandaHabitat scene.

        Args:
            manager (SceneManager): Scene manager responsible for
            handling scene transitions.
        """
        self.BACKGROUND_FILE = (
            self.BACKGROUND_FILE_DAY
            if manager.context.is_day
            else self.BACKGROUND_FILE_NIGHT
        )

        super().__init__(manager)

        incomplete = manager.context.checklist.get_incomplete_tasks()

        self._pet_task_active = "red_panda_pet" in incomplete
        self._poop_active = "red_panda_poop" in incomplete

        raw = pygame.image.load(
            os.path.join("assets", "images", self._ICON_POOP)
        ).convert_alpha()

        self._waste_sprite = pygame.transform.smoothscale(
            raw,
            (int(raw.get_width() * 0.12), int(raw.get_height() * 0.12))
        )

        self._waste_positions = [
            pygame.Vector2(200, 300),
            pygame.Vector2(700, 500)
        ] if self._poop_active else []

        self._waste_clicked = [False] * len(self._waste_positions)

    def on_enter(self) -> None:
        """Refresh task state when entering the scene."""
        super().on_enter()
        incomplete = self._manager.context.checklist.get_incomplete_tasks()
        self._pet_task_active = "red_panda_pet" in incomplete

    def create_animals(self) -> list[Animal]:
        """Creates and returns the red panda animal for this habitat.

        Returns:
            list[Animal]: the red panda
        """
        return [
            Animal(
                x=200,
                y=200,
                layer_files=["red_panda.png", "red_panda_tail.png"],
                subfolder=_SUBFOLDER,
                scale=1,
                speed=0,
                animate_fn=self._animate,
                draw_fn=self._draw,
                rect_size=(400, 400),
            )
        ]

    @staticmethod
    def _animate(animal: Animal) -> None:
        """
        Animates the red panda by applying a sinusoidal tail motion.

        Args:
            animal (Animal): The red panda instance containing animation state.
        """
        animal.tail_angle = math.sin(animal.time * 2) * 15

    @staticmethod
    def _draw(animal: Animal, screen: pygame.Surface) -> None:
        """
        Renders a red panda using a simple two-part sprite
        system (body + tail).

        Args:
            animal (Animal): The red panda instance containing
            position and animation state.
            screen (pygame.Surface): The surface to render the red panda onto.
        """
        if not animal.layers:
            return

        body = animal.layers[0]
        tail = animal.layers[1]

        screen.blit(body, (int(animal.x), int(animal.y)))

        angle = getattr(animal, "tail_angle", 0)
        rotated_tail, rect = MathHelper.rotate_image(
            tail,
            angle,
            pygame.Vector2(TAIL_PIVOT.x, TAIL_PIVOT.y)
        )

        rect.x += int(animal.x)
        rect.y += int(animal.y)

        screen.blit(rotated_tail, rect)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle clicks for the droppings minigame."""
        super().handle_events(events)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, pos in enumerate(self._waste_positions):
                    if not self._waste_clicked[i]:
                        rect = self._waste_sprite.get_rect(
                            center=(int(pos.x), int(pos.y))
                        )
                        if rect.collidepoint(event.pos):
                            self._waste_clicked[i] = True

    def update(self, dt: float) -> None:
        """Update animal state and minigame progress."""
        super().update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        """Render background, animals, poop piles, and toolbar."""
        super().draw(screen)

        for i, pos in enumerate(self._waste_positions):
            if not self._waste_clicked[i]:
                screen.blit(
                    self._waste_sprite,
                    self._waste_sprite.get_rect(
                        center=(int(pos.x), int(pos.y))
                    )
                )

        if self._poop_active and all(self._waste_clicked):
            self._poop_active = False
            self._manager.context.checklist.complete_task("red_panda_poop")

            from checklist_scene import ChecklistScene
            self._manager.pop()
            self._manager.push(
                ChecklistScene(
                    self._manager,
                    self._manager.context.checklist
                )
            )

    def _on_pet_complete(self) -> None:
        """Mark pet task complete and return to checklist."""
        self._manager.context.checklist.complete_task("red_panda_pet")

        from checklist_scene import ChecklistScene
        self._manager.pop()
        self._manager.push(
            ChecklistScene(
                self._manager,
                self._manager.context.checklist
            )
        )
