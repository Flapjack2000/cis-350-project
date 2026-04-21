import os
import math
import pygame

from scene import SceneManager
from habitat_scene import HabitatScene, _IconButton, ICON_SPACING, TOOLBAR_PAD
from animal import Animal
from animal_movement import AnimalMovement

_SUBFOLDER = os.path.join("assets", "animals", "penguin")
WADDLE_SPEED = 6
WADDLE_AMPLITUDE = 10


class PenguinHabitat(HabitatScene):
    """Habitat scene for penguins in an arctic environment.

    Minigames:
    - Pet: Hold the cursor over a penguin.
    - Water: Fill the trough for the penguins.
    """

    BACKGROUND_FILE_DAY = "aquatic_background_day.png"
    BACKGROUND_FILE_NIGHT = "aquatic_background_night.png"
    _ICON_WATER = "water_icon.png"

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

        self._pet_task_active = "penguin_pet" in incomplete
        self._water_task_active = "penguin_water" in incomplete

        # Water minigame state
        self._water_level = 0.0
        self._max_water_level = 100.0
        self._trough_rect = pygame.Rect(50, 450, 200, 80)
        self._is_filling = False

        self._build_toolbar()

    def create_animals(self) -> list[Animal]:
        """Return waddling penguins."""
        return [
            Animal(
                x=100,
                y=200,
                layer_files=["penguin.png"],
                subfolder=_SUBFOLDER,
                scale=0.7,
                default_facing_left=True,
                direction=1,
                speed=0.5,
                animate_fn=self._animate,
                draw_fn=self._draw_animal,
                rect_size=(350, 350)
            ),
            Animal(
                x=500,
                y=100,
                layer_files=["penguin.png"],
                subfolder=_SUBFOLDER,
                scale=0.7,
                default_facing_left=True,
                direction=1,
                speed=0.5,
                animate_fn=self._animate,
                draw_fn=self._draw_animal,
                rect_size=(350, 350)
            )
        ]

    def _build_toolbar(self) -> None:
        """Add the water button to the toolbar."""
        super()._build_toolbar()

        if not self._water_task_active:
            self._btn_water = None
            return

        x = self._btn_pet.rect.right + ICON_SPACING
        y = TOOLBAR_PAD
        self._btn_water = _IconButton(
            self._icon_path(self._ICON_WATER),
            topleft=(x, y),
            enabled=True,
            greyed=False
        )

    @staticmethod
    def _animate(animal: Animal) -> None:
        """Apply waddle and bobbing based on movement speed."""
        t = animal.time
        speed_factor = abs(animal.direction * animal.speed)
        animal.waddle_angle = math.sin(t * WADDLE_SPEED) * WADDLE_AMPLITUDE * speed_factor
        animal.y_offset = math.sin(t * WADDLE_SPEED * 2) * 2 * speed_factor

    def _draw_animal(self, animal: Animal, screen: pygame.Surface) -> None:
        """Render penguin with waddle rotation and directional flipping."""
        if not animal.layers:
            return

        img = animal.layers[0]
        base_pivot = pygame.Vector2(img.get_width() // 2, img.get_height() - 15)
        should_flip = animal.facing_left != animal.default_facing_left

        draw_img = img
        draw_pivot = base_pivot

        if should_flip:
            draw_img = pygame.transform.flip(img, True, False)
            draw_pivot = pygame.Vector2(img.get_width() - base_pivot.x, base_pivot.y)

        rotated_img, rect = self._movement.rotate_image(
            draw_img,
            getattr(animal, "waddle_angle", 0),
            (draw_pivot.x, draw_pivot.y)
        )

        rect.x += int(animal.x)
        rect.y += int(animal.y + getattr(animal, "y_offset", 0))
        screen.blit(rotated_img, rect)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle toolbar and water interaction."""
        super().handle_events(events)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self._btn_water and self._btn_water.rect.collidepoint(event.pos):
                    self._is_filling = not self._is_filling
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self._is_filling = True
            elif event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
                self._is_filling = False

    def update(self, dt: float) -> None:
        """Update animal behavior and water level."""
        super().update(dt)

        if self._water_task_active and self._is_filling:
            self._water_level += 30 * dt
            if self._water_level >= self._max_water_level:
                self._water_level = self._max_water_level
                self._handle_water_task_complete()

    def draw(self, screen: pygame.Surface) -> None:
        """Render habitat elements and water trough."""
        super().draw(screen)

        if self._water_task_active:
            self._draw_trough(screen)

        if self._btn_water:
            self._btn_water.draw(screen)

    def _draw_trough(self, screen: pygame.Surface) -> None:
        """Render the water trough and its current fill level."""
        pygame.draw.rect(screen, (100, 100, 100), self._trough_rect)
        pygame.draw.rect(screen, (60, 60, 60), self._trough_rect, 4)

        fill_height = (self._water_level / self._max_water_level) * (self._trough_rect.height - 10)
        water_rect = pygame.Rect(
            self._trough_rect.x + 5,
            self._trough_rect.bottom - 5 - fill_height,
            self._trough_rect.width - 10,
            fill_height
        )
        if fill_height > 0:
            pygame.draw.rect(screen, (0, 150, 255), water_rect)

    def _on_pet_complete(self) -> None:
        """Mark pet task complete and return to checklist."""
        self._manager.context.checklist.complete_task("penguin_pet")
        from checklist_scene import ChecklistScene
        self._manager.push(ChecklistScene(self._manager, self._manager.context.checklist))

    def _handle_water_task_complete(self) -> None:
        """Mark water task complete and return to checklist."""
        self._water_task_active = False
        self._is_filling = False
        if self._btn_water:
            self._btn_water.enabled = False
            self._btn_water.greyed = True
        self._manager.context.checklist.complete_task("penguin_water")
        from checklist_scene import ChecklistScene
        self._manager.push(ChecklistScene(self._manager, self._manager.context.checklist))
