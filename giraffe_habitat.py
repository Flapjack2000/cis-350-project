import os
import math
import random
import pygame

from scene import SceneManager
from habitat_scene import HabitatScene, _IconButton, ICON_SPACING, TOOLBAR_PAD
from animal import Animal
from animal_movement import AnimalMovement


class GiraffeHabitat(HabitatScene):
    """Giraffe habitat with pet, poop, and water minigames."""

    BACKGROUND_FILE_DAY = "savanna_background_day.png"
    BACKGROUND_FILE_NIGHT = "savanna_background_night.png"

    _SUBFOLDER = os.path.join("assets", "animals", "giraffe")

    _LAYER_FILES = [
        "giraffe_neck.png",
        "giraffe_hind_back_upper.png",
        "giraffe_hind_back_lower.png",
        "giraffe_hind_front_upper.png",
        "giraffe_hind_front_lower.png",
        "giraffe_tail.png",
        "giraffe_body.png",
        "giraffe_fore_back_upper.png",
        "giraffe_fore_back_lower.png",
        "giraffe_fore_front_upper.png",
        "giraffe_fore_front_lower.png",
        "giraffe_head.png",
    ]

    _ICON_POOP = "poop_icon.png"

    _TROUGH_S1 = 250
    _TROUGH_S2 = 20
    _TROUGH_COLOR = (123, 63, 0)
    _WATER_COLOR = (0, 94, 209)

    _GIRAFFE_SPEED = 1.2

    _FRONT_PIVOT = pygame.Vector2(25, 15)
    _HIND_PIVOT = pygame.Vector2(25, 15)

    def __init__(self, manager: SceneManager) -> None:
        """Init habitat state."""
        self.BACKGROUND_FILE = (
            self.BACKGROUND_FILE_DAY
            if manager.context.is_day
            else self.BACKGROUND_FILE_NIGHT
        )
        super().__init__(manager)

        self._movement = AnimalMovement()
        incomplete = manager.context.checklist.get_incomplete_tasks()

        self._pet_task_active = "giraffe_pet" in incomplete

        self._poop_task_active = "giraffe_poop" in incomplete
        self._poop_cleared = False
        self._waste_positions = []
        self._waste_clicked = []

        raw = pygame.image.load(
            os.path.join("assets", "images", "poop_icon.png")
        ).convert_alpha()
        w, h = raw.get_size()
        self._waste_sprite = pygame.transform.smoothscale(
            raw, (int(w * 0.12), int(h * 0.12))
        )

        if self._poop_task_active:
            self._waste_positions = [pygame.Vector2(200, 500), pygame.Vector2(800, 600)]
            self._waste_clicked = [False, False]

        self._water_task_active = "giraffe_water" in incomplete
        if self._water_task_active:
            self._init_water()

        self._build_toolbar()

    def _init_water(self) -> None:
        """Init water minigame."""
        self._water_level = 75
        self._max_water_level = 100
        self._increment = 2
        self._decrement = 55

        self._passes_until_drink = 1
        self._pass_counted = False
        self._drink_timer = 0.0
        self._drink_duration = 1.5

        font = pygame.font.SysFont(None, 32)
        self._instruction_surf = font.render(
            "Click the trough to fill it with water!", True, (0, 0, 0)
        )

    def create_animals(self) -> list[Animal]:
        """Create giraffe instances."""

        def make(x, y, direction, speed=None, droppings=False):
            return Animal(
                x=x,
                y=y,
                layer_files=self._LAYER_FILES,
                subfolder=self._SUBFOLDER,
                scale=0.5,
                default_facing_left=True,
                direction=direction,
                speed=speed or self._GIRAFFE_SPEED,
                animate_fn=self._animate,
                draw_fn=self._draw,
                has_droppings=droppings,
            )

        if self._water_task_active:
            return [make(200, 300, 1, droppings=self._poop_task_active)]

        return [
            make(200, 300, 1, droppings=self._poop_task_active),
            make(600, 500, -1),
        ]

    @staticmethod
    def _animate(animal):
        """Animate giraffe walk."""
        t = animal.time
        swing = math.sin(t * 4) * 10

        hbu, hbl = 1, 2
        hfu, hfl = 3, 4
        fbu, fbl = 7, 8
        ffu, ffl = 9, 10

        animal.layer_angles[hbu] = swing
        animal.layer_angles[hbl] = swing * 0.9
        animal.layer_angles[hfu] = -swing
        animal.layer_angles[hfl] = -swing * 0.9
        animal.layer_angles[fbu] = -swing
        animal.layer_angles[fbl] = -swing * 0.9
        animal.layer_angles[ffu] = swing
        animal.layer_angles[ffl] = swing * 0.9

    def _draw(self, animal, screen):
        """Draw giraffe with layered rotation."""
        should_flip = animal.facing_left != animal.default_facing_left
        body_w = animal.layers[6].get_width() if animal.layers else 0
        body_pos = pygame.Vector2(animal.x + body_w / 2, animal.y)

        pivots = []
        for i, layer in enumerate(animal.layers):
            name = animal.layer_files[i]
            if "hind_back_upper" in name or "hind_front_upper" in name:
                pivots.append(self._HIND_PIVOT)
            elif "fore_back_upper" in name or "fore_front_upper" in name:
                pivots.append(self._FRONT_PIVOT)
            else:
                pivots.append(
                    pygame.Vector2(layer.get_width() // 2, layer.get_height() // 2)
                )

        for layer, angle, pivot in zip(animal.layers, animal.layer_angles, pivots):
            img, rect = self._movement.rotate_image(layer, angle, pivot)
            rect.center = body_pos
            if should_flip:
                img = pygame.transform.flip(img, True, False)
            screen.blit(img, rect)

    def _build_toolbar(self):
        super()._build_toolbar()
        if not self._poop_task_active:
            self._btn_poop = None
            return

        x = self._btn_pet.rect.right + ICON_SPACING
        self._btn_poop = _IconButton(
            self._icon_path(self._ICON_POOP),
            topleft=(x, TOOLBAR_PAD),
            enabled=not self._poop_cleared,
            greyed=self._poop_cleared,
        )

    def _handle_poop_click(self, pos):
        if not self._poop_task_active or self._poop_cleared:
            return

        for i, p in enumerate(self._waste_positions):
            if not self._waste_clicked[i]:
                rect = self._waste_sprite.get_rect(center=(int(p.x), int(p.y)))
                if rect.collidepoint(pos):
                    self._waste_clicked[i] = True

        if all(self._waste_clicked):
            self._poop_cleared = True
            if self._btn_poop:
                self._btn_poop.enabled = False
                self._btn_poop.greyed = True
            self._manager.context.checklist.complete_task("giraffe_poop")
            from checklist_scene import ChecklistScene
            self._manager.push(ChecklistScene(self._manager, self._manager.context.checklist))

    def _trough_rect(self, screen):
        s1 = self._TROUGH_S1
        cx = (screen.get_width() // 2) - (s1 // 2)
        cy = (screen.get_height() // 2) - (s1 // 2) + 220
        return pygame.Rect(cx, cy, s1, s1)

    def handle_events(self, events):
        super().handle_events(events)
        screen = pygame.display.get_surface()
        trough = self._trough_rect(screen) if self._water_task_active else None

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self._handle_poop_click(e.pos)
                if trough and trough.collidepoint(e.pos):
                    self._water_level = min(self._max_water_level, self._water_level + self._increment)

    def update(self, dt):
        if not self._water_task_active:
            super().update(dt)
            return

        giraffe = self._animals[0] if self._animals else None

        if self._drink_timer > 0:
            self._drink_timer -= dt
            if self._drink_timer <= 0 and giraffe:
                giraffe.speed = self._GIRAFFE_SPEED
            return

        super().update(dt)

        if not giraffe:
            return

        screen = pygame.display.get_surface()
        rect = self._trough_rect(screen)

        body_w = giraffe.layers[0].get_width() if giraffe.layers else 0
        cx = giraffe.x + body_w // 2

        if rect.left <= cx <= rect.right:
            if not self._pass_counted:
                self._pass_counted = True
                self._passes_until_drink -= 1
                if self._passes_until_drink <= 0 < self._water_level:
                    giraffe.speed = 0
                    self._drink_timer = self._drink_duration
                    self._passes_until_drink = random.randint(1, 3)
                    self._water_level = max(0, self._water_level - self._decrement)
        else:
            self._pass_counted = False

    def draw(self, screen):
        super().draw(screen)

        for i, pos in enumerate(self._waste_positions):
            if not self._waste_clicked[i]:
                rect = self._waste_sprite.get_rect(center=(int(pos.x), int(pos.y)))
                screen.blit(self._waste_sprite, rect)

        if self._btn_poop:
            self._btn_poop.draw(screen)

        if self._water_task_active:
            self._draw_trough(screen)
            self._draw_trough_instruction(screen)

            if self._water_level >= self._max_water_level:
                self._manager.context.checklist.complete_task("giraffe_water")
                from checklist_scene import ChecklistScene
                self._manager.push(ChecklistScene(self._manager, self._manager.context.checklist))
                self._water_task_active = False

    def _draw_trough(self, screen):
        s1, s2 = self._TROUGH_S1, self._TROUGH_S2
        water_h = int((s1 - s2) * (self._water_level / self._max_water_level))
        rect = self._trough_rect(screen)
        cx, cy = rect.left, rect.top

        parts = [
            (pygame.Surface((s1 - s2 * 2, water_h)), self._WATER_COLOR, (cx + s2, cy + s1 - s2 - water_h)),
            (pygame.Surface((s1, s2)), self._TROUGH_COLOR, (cx, cy + s1 - s2)),
            (pygame.Surface((s2, s1)), self._TROUGH_COLOR, (cx, cy)),
            (pygame.Surface((s2, s1)), self._TROUGH_COLOR, (cx + s1 - s2, cy)),
        ]

        for surf, color, pos in parts:
            surf.fill(color)
            screen.blit(surf, pos)

    def _draw_trough_instruction(self, screen):
        rect = self._trough_rect(screen)
        screen.blit(self._instruction_surf, (rect.right + 20, rect.top + 20))

    def _on_pet_complete(self):
        self._manager.context.checklist.complete_task("giraffe_pet")
        from checklist_scene import ChecklistScene
        self._manager.push(ChecklistScene(self._manager, self._manager.context.checklist))
