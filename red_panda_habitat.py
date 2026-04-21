import os
import math
import pygame

from scene import SceneManager
from habitat_scene import HabitatScene, _IconButton, ICON_SPACING, TOOLBAR_PAD
from animal import Animal
from animal_movement import AnimalMovement

_SUBFOLDER = os.path.join("assets", "animals", "redpanda")
TAIL_PIVOT = pygame.Vector2(300, 150)


class RedPandaHabitat(HabitatScene):
    """Habitat scene for red pandas in a jungle environment.

    Minigames:
    - Pet: Hold the cursor over the red panda.
    - Poop: Click all waste piles to clean the enclosure.
    """

    BACKGROUND_FILE_DAY = "jungle_background_day.png"
    BACKGROUND_FILE_NIGHT = "jungle_background_night.png"
    _ICON_POOP = "poop_icon.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize habitat state and task-based minigames."""
        self.BACKGROUND_FILE = (
            self.BACKGROUND_FILE_DAY
            if manager.context.is_day
            else self.BACKGROUND_FILE_NIGHT
        )
        super().__init__(manager)

        self._movement = AnimalMovement()
        incomplete = manager.context.checklist.get_incomplete_tasks()

        # Task activation
        self._pet_task_active = "red_panda_pet" in incomplete
        self._poop_task_active = "red_panda_poop" in incomplete

        # Poop minigame state
        self._waste_positions: list[pygame.Vector2] = []
        self._waste_clicked: list[bool] = []
        self._poop_cleared = False

        raw_waste = pygame.image.load(
            os.path.join("assets", "images", self._ICON_POOP)
        ).convert_alpha()
        ww, wh = raw_waste.get_size()
        self._waste_sprite = pygame.transform.smoothscale(
            raw_waste, (int(ww * 0.12), int(wh * 0.12))
        )

        if self._poop_task_active:
            self._waste_positions = [
                pygame.Vector2(500, 300),
                pygame.Vector2(1000, 520),
                pygame.Vector2(950, 220),
                pygame.Vector2(200, 320)
            ]
            self._waste_clicked = [False] * len(self._waste_positions)

        self._build_toolbar()

    def create_animals(self) -> list[Animal]:
        """Return a stationary red panda with tail-wag animation."""
        return [
            Animal(
                x=400,
                y=350,
                layer_files=["red_panda.png", "red_panda_tail.png"],
                subfolder=_SUBFOLDER,
                scale=1.0,
                speed=0.0,
                animate_fn=self._animate,
                draw_fn=self._draw_animal,
                rect_size=(250, 200)
            )
        ]

    def _build_toolbar(self) -> None:
        """Add the poop cleaning button to the toolbar."""
        super()._build_toolbar()

        if not self._poop_task_active:
            self._btn_poop = None
            return

        x = self._btn_pet.rect.right + ICON_SPACING
        y = TOOLBAR_PAD
        self._btn_poop = _IconButton(
            self._icon_path(self._ICON_POOP),
            topleft=(x, y),
            enabled=not self._poop_cleared,
            greyed=self._poop_cleared,
        )

    def _handle_poop_click(self, mouse_pos: tuple[int, int]) -> None:
        """Check for collisions with waste piles."""
        if not self._poop_task_active or self._poop_cleared:
            return

        for i, pos in enumerate(self._waste_positions):
            if self._waste_clicked[i]:
                continue
            rect = self._waste_sprite.get_rect(topleft=(pos.x, pos.y))
            if rect.collidepoint(mouse_pos):
                self._waste_clicked[i] = True

        if all(self._waste_clicked):
            self._poop_cleared = True
            if self._btn_poop:
                self._btn_poop.enabled = False
                self._btn_poop.greyed = True
            self._manager.context.checklist.complete_task("red_panda_poop")
            from checklist_scene import ChecklistScene
            self._manager.push(
                ChecklistScene(self._manager, self._manager.context.checklist)
            )

    @staticmethod
    def _animate(animal: Animal) -> None:
        """Apply sinusoidal tail motion."""
        animal.tail_angle = math.sin(animal.time * 2) * 15

    def _draw_animal(self, animal: Animal, screen: pygame.Surface) -> None:
        """Render red panda layers (body and tail) with pivots."""
        if not animal.layers:
            return

        body = animal.layers[0]
        tail = animal.layers[1]

        screen.blit(body, (int(animal.x), int(animal.y)))

        angle = getattr(animal, "tail_angle", 0)
        rotated_tail, rect = self._movement.rotate_image(
            tail, angle, (TAIL_PIVOT.x, TAIL_PIVOT.y)
        )

        rect.x += int(animal.x)
        rect.y += int(animal.y)
        screen.blit(rotated_tail, rect)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle standard and minigame input."""
        super().handle_events(events)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_poop_click(event.pos)

    def update(self, dt: float) -> None:
        """Update animal state and minigame progress."""
        super().update(dt)

    def draw(self, screen: pygame.Surface) -> None:
        """Render background, animals, poop piles, and toolbar."""
        super().draw(screen)

        if self._poop_task_active and not self._poop_cleared:
            for i, pos in enumerate(self._waste_positions):
                if not self._waste_clicked[i]:
                    screen.blit(self._waste_sprite, (pos.x, pos.y))

        if self._btn_poop:
            self._btn_poop.draw(screen)

    def _on_pet_complete(self) -> None:
        """Mark pet task complete and return to checklist."""
        self._manager.context.checklist.complete_task("red_panda_pet")
        from checklist_scene import ChecklistScene
        self._manager.pop()
        self._manager.push(
            ChecklistScene(self._manager, self._manager.context.checklist)
        )
