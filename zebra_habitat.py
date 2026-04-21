import os
import math
import random

import pygame

from scene import SceneManager
from habitat_scene import HabitatScene, _IconButton, ICON_SPACING, TOOLBAR_PAD
from animal import Animal
from animal_movement import AnimalMovement

_SUBFOLDER = os.path.join("assets", "animals", "zebra")
_LAYER_FILES = [
    "zebra_hind_back_upper.png",
    "zebra_hind_back_lower.png",
    "zebra_hind_front_upper.png",
    "zebra_hind_front_lower.png",
    "zebra_tail.png",
    "zebra_body.png",
    "zebra_fore_back_upper.png",
    "zebra_fore_back_lower.png",
    "zebra_fore_front_upper.png",
    "zebra_fore_front_lower.png",
    "zebra_neck.png",
    "zebra_head.png",
]

# Layer-index aliases
_HBU, _HBL = 0, 1
_HFU, _HFL = 2, 3
_TAIL = 4
_BODY = 5
_FBU, _FBL = 6, 7
_FFU, _FFL = 8, 9
_NECK = 10
_HEAD = 11


class ZebraHabitat(HabitatScene):
    """Habitat scene for zebras in a savanna environment.

    Minigames available:
    - **Pet** (inherited from HabitatScene): hold the cursor over a zebra.
    - **Poop**: click all waste piles to clean the enclosure.
    - **Water trough**: click the trough to fill it; the zebra drinks as it passes.

    Each minigame is activated only when its checklist task is still incomplete.
    Both the poop and water-trough minigames are self-contained within this class.
    """

    BACKGROUND_FILE_DAY = "savanna_background_day.png"
    BACKGROUND_FILE_NIGHT = "savanna_background_night.png"

    _ICON_POOP = "poop_icon.png"

    # Trough geometry constants
    _TROUGH_S1 = 250  # outer size (height of walls, width of base)
    _TROUGH_S2 = 20  # wall / base thickness
    _TROUGH_COLOR = (123, 63, 0)
    _WATER_COLOR = (0, 94, 209)

    _ZEBRA_SPEED = 2.5

    def __init__(self, manager: SceneManager) -> None:
        """Initialise ZebraHabitat and the poop and water-trough minigame state.

        Args:
            manager (SceneManager): The scene manager controlling transitions.
        """
        self.BACKGROUND_FILE = (
            self.BACKGROUND_FILE_DAY
            if manager.context.is_day
            else self.BACKGROUND_FILE_NIGHT
        )
        super().__init__(manager)

        self._movement = AnimalMovement()

        incomplete = manager.context.checklist.get_incomplete_tasks()

        # Pet minigame state
        self._pet_task_active: bool = "zebra_pet" in incomplete

        # Poop minigame state
        self._poop_task_active: bool = "zebra_poop" in incomplete
        self._waste_positions: list[pygame.Vector2] = []
        self._waste_clicked: list[bool] = []
        self._poop_cleared: bool = False

        raw_waste = pygame.image.load(
            os.path.join("assets", "images", "poop_icon.png")
        ).convert_alpha()
        ww, wh = raw_waste.get_size()
        self._waste_sprite = pygame.transform.smoothscale(
            raw_waste, (int(ww * 0.12), int(wh * 0.12))
        )

        if self._poop_task_active:
            self._waste_positions = [pygame.Vector2(100, 260), pygame.Vector2(900, 650)]
            self._waste_clicked = [False, False]

        # Water minigame state
        self._water_task_active: bool = "zebra_water" in incomplete

        if self._water_task_active:
            self._init_water_minigame()

        # Rebuild toolbar now that poop task state is known
        self._build_toolbar()

    def _init_water_minigame(self) -> None:
        """Set up the water-trough minigame."""
        self._water_level: int = 25 * 3
        self._max_water_level: int = 100
        self._increment: int = 2
        self._decrement: int = 55

        # How many trough passes before the zebra stops to drink
        self._passes_until_drink: int = 1
        self._pass_counted: bool = False
        self._drink_duration: float = 1.5
        self._drink_timer: float = 0.0

        font = pygame.font.SysFont(None, 32)
        self._instruction_surf = font.render(
            "Click the trough to fill it with water!", True, (0, 0, 0)
        )

        if not (0 <= self._water_level <= self._max_water_level):
            raise ValueError("Water level must be within [0, max_water_level].")

    def create_animals(self) -> list[Animal]:
        """Return zebra Animal instances appropriate for the active minigames.

        A single zebra is used when the water-trough task is active so the
        player can track it clearly.  Two zebras roam when just visiting.

        Returns:
            list[Animal]: Zebra animals for the scene.
        """
        make = lambda x, y, direction, scale=0.45, speed=self._ZEBRA_SPEED, droppings=False: Animal(
            x=x, y=y,
            layer_files=_LAYER_FILES,
            subfolder=_SUBFOLDER,
            scale=scale,
            default_facing_left=True,
            direction=direction,
            speed=speed,
            animate_fn=ZebraHabitat._animate,
            draw_fn=self._draw_animal,
            has_droppings=droppings,
        )

        if self._water_task_active:
            return [make(120, 300, direction=1, droppings=self._poop_task_active)]

        return [
            make(120, 300, direction=1, droppings=self._poop_task_active),
            make(520, 500, direction=-1, scale=0.40, speed=self._ZEBRA_SPEED * 1.1),
        ]

    def _build_toolbar(self) -> None:
        """Extend the base toolbar with a poop button when that task is active.

        Args: none — reads task-active flags from instance state.
        """
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
        """Check whether a waste pile was clicked and advance poop minigame.

        Args:
            mouse_pos (tuple[int, int]): Position of the click.
        """
        if not self._poop_task_active or self._poop_cleared:
            return

        for i, pos in enumerate(self._waste_positions):
            if self._waste_clicked[i]:
                continue
            pile_rect = self._waste_sprite.get_rect(center=(int(pos.x), int(pos.y)))
            if pile_rect.collidepoint(mouse_pos):
                self._waste_clicked[i] = True

        if all(self._waste_clicked):
            self._poop_cleared = True
            if self._btn_poop:
                self._btn_poop.enabled = False
                self._btn_poop.greyed = True
            self._manager.context.checklist.complete_task("zebra_poop")
            from checklist_scene import ChecklistScene
            self._manager.push(
                ChecklistScene(self._manager, self._manager.context.checklist)
            )

    def _draw_waste_pile(self, screen: pygame.Surface, index: int) -> None:
        """Draw a single waste pile if it has not been clicked yet.

        Args:
            screen (pygame.Surface): Surface to draw on.
            index (int): Index into _waste_positions / _waste_clicked.
        """
        if not self._poop_task_active or self._poop_cleared:
            return
        if index >= len(self._waste_positions):
            return
        if self._waste_clicked[index]:
            return
        pos = self._waste_positions[index]
        rect = self._waste_sprite.get_rect(center=(int(pos.x), int(pos.y)))
        screen.blit(self._waste_sprite, rect)

    @staticmethod
    def _animate(animal: Animal) -> None:
        """Apply sinusoidal leg-swing animation to the zebra's limb layers.

        Args:
            animal (Animal): Zebra instance with time and layer_angles.
        """
        swing = math.sin(animal.time * 5) * 5

        animal.layer_angles[_HBU] = swing
        animal.layer_angles[_HBL] = swing * 0.8
        animal.layer_angles[_HFU] = -swing
        animal.layer_angles[_HFL] = -swing * 0.8
        animal.layer_angles[_FBU] = -swing
        animal.layer_angles[_FBL] = -swing * 0.8
        animal.layer_angles[_FFU] = swing
        animal.layer_angles[_FFL] = swing * 0.8

    def _draw_animal(self, animal: Animal, screen: pygame.Surface) -> None:
        """Render a zebra using pivot-based layer rotation.

        Args:
            animal (Animal): Zebra instance with sprite layers and angle data.
            screen (pygame.Surface): Surface to render onto.
        """
        should_flip = animal.facing_left != animal.default_facing_left
        body_width = animal.layers[_BODY].get_width() if animal.layers else 0
        body_pos = pygame.Vector2(animal.x + body_width / 2, animal.y)

        for layer, angle in zip(animal.layers, animal.layer_angles):
            pivot = pygame.Vector2(layer.get_width() // 2, layer.get_height() // 2)
            rotated_img, rotated_rect = self._movement.rotate_image(layer, angle, pivot)
            rotated_rect.center = body_pos
            if should_flip:
                rotated_img = pygame.transform.flip(rotated_img, True, False)
            screen.blit(rotated_img, rotated_rect)

    def _trough_rect(self, screen: pygame.Surface) -> pygame.Rect:
        """Return the outer bounding rect of the trough for hit-testing.

        Args:
            screen (pygame.Surface): Current display surface.

        Returns:
            pygame.Rect: Trough bounding box.
        """
        s1, s2 = self._TROUGH_S1, self._TROUGH_S2
        cx = (screen.get_width() // 2) - (s1 // 2)
        cy = (screen.get_height() // 2) - (s1 // 2) + 220
        return pygame.Rect(cx, cy, s1, s1)

    def _draw_trough(self, screen: pygame.Surface) -> None:
        """Render the water trough (walls, base, and current water level).

        Args:
            screen (pygame.Surface): Surface to draw on.
        """
        s1, s2 = self._TROUGH_S1, self._TROUGH_S2
        water_h = int(
            (s1 - s2) * (self._water_level / self._max_water_level)
        )

        trough_rect = self._trough_rect(screen)
        cx, cy = trough_rect.left, trough_rect.top

        parts_and_positions = [
            # (surface, fill_color, position)
            (pygame.Surface((s1 - s2 * 2, water_h)),
             self._WATER_COLOR,
             (cx + s2, cy + s1 - s2 - water_h)),

            (pygame.Surface((s1, s2)),
             self._TROUGH_COLOR,
             (cx, cy + s1 - s2)),

            (pygame.Surface((s2, s1)),
             self._TROUGH_COLOR,
             (cx, cy)),

            (pygame.Surface((s2, s1)),
             self._TROUGH_COLOR,
             (cx + s1 - s2, cy)),
        ]

        for surf, color, pos in parts_and_positions:
            surf.fill(color)
            screen.blit(surf, pos)

    def _draw_trough_instruction(self, screen: pygame.Surface) -> None:
        """Render the fill-water instruction text to the right of the trough.

        Args:
            screen (pygame.Surface): Surface to draw on.
        """
        trough_rect = self._trough_rect(screen)
        screen.blit(
            self._instruction_surf,
            (trough_rect.right + 20, trough_rect.top + 20),
        )

    def _increment_water(self) -> None:
        """Raise the water level by the increment amount, capped at maximum."""
        self._water_level = min(
            self._max_water_level,
            self._water_level + self._increment,
        )

    def _decrement_water(self) -> None:
        """Lower the water level by the decrement amount, floored at zero."""
        self._water_level = max(0, self._water_level - self._decrement)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle mouse and keyboard input, including poop and trough clicks.

        Args:
            events (list[pygame.event.Event]): Pygame events for this frame.
        """
        super().handle_events(events)

        screen = pygame.display.get_surface()
        trough_rect = self._trough_rect(screen) if self._water_task_active else None

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_poop_click(event.pos)
                if trough_rect and trough_rect.collidepoint(event.pos):
                    self._increment_water()

    def update(self, dt: float) -> None:
        """Advance animals, the pet minigame, and the water-trough minigame.

        Args:
            dt (float): Seconds since last frame.
        """
        if not self._water_task_active:
            super().update(dt)
            return

        zebra = self._animals[0] if self._animals else None

        # While zebra is drinking, freeze it and count down
        if self._drink_timer > 0:
            self._drink_timer -= dt
            if self._drink_timer <= 0:
                self._drink_timer = 0.0
                if zebra:
                    zebra.speed = self._ZEBRA_SPEED
            # Skip animal movement — but still update pet minigame via parent
            # We call update on animals manually with speed=0 frozen above,
            # then call pet update separately.
            return

        # Normal update (animals walk + pet progress)
        super().update(dt)

        if zebra is None:
            return

        # Trough-crossing detection
        screen = pygame.display.get_surface()
        trough_rect = self._trough_rect(screen)
        body_w = zebra.layers[0].get_width() if zebra.layers else 0
        zebra_cx = zebra.x + body_w // 2
        over_trough = trough_rect.left <= zebra_cx <= trough_rect.right

        if over_trough:
            if not self._pass_counted:
                self._pass_counted = True
                self._passes_until_drink -= 1
                if self._passes_until_drink <= 0 < self._water_level:
                    zebra.speed = 0.0
                    self._drink_timer = self._drink_duration
                    self._passes_until_drink = random.randint(1, 3)
                    self._decrement_water()
        else:
            self._pass_counted = False

    def draw(self, screen: pygame.Surface) -> None:
        """Render the habitat, poop piles, trough, instruction text, and toolbar.

        Args:
            screen (pygame.Surface): Surface to draw on.
        """
        # Background + animals + toolbar icons
        super().draw(screen)

        # Poop piles — depth-sorted: first before animals, second after
        self._draw_waste_pile(screen, 0)
        # (animals are already drawn by super; draw second pile on top)
        self._draw_waste_pile(screen, 1)

        # Poop toolbar button (owned by this subclass)
        if self._btn_poop is not None:
            self._btn_poop.draw(screen)

        if self._water_task_active:
            self._draw_trough(screen)
            self._draw_trough_instruction(screen)

            # Task complete hint once trough is full
            if self._water_level >= self._max_water_level:
                font = pygame.font.SysFont(None, 28)
                done_surf = font.render(
                    "Trough full! Great job!", True, (0, 120, 0)
                )
                screen.blit(done_surf, (20, screen.get_height() - 40))
                self._handle_water_task_complete()

    def _on_pet_complete(self) -> None:
        """Mark the zebra_pet task as done and show the checklist."""
        self._manager.context.checklist.complete_task("zebra_pet")
        from checklist_scene import ChecklistScene
        self._manager.push(
            ChecklistScene(self._manager, self._manager.context.checklist)
        )

    def _handle_water_task_complete(self) -> None:
        """Mark the water task as done and show the checklist."""
        self._water_task_active = False
        self._manager.context.checklist.complete_task("zebra_water")
        from checklist_scene import ChecklistScene
        self._manager.push(
            ChecklistScene(self._manager, self._manager.context.checklist)
        )
