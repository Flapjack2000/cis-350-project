import os
import math
import random
import pygame

from scene import SceneManager
from habitat_scene import HabitatScene, _IconButton, ICON_SPACING, TOOLBAR_PAD
from animal import Animal
from animal_movement import AnimalMovement


class MeerkatHabitat(HabitatScene):
    """Meerkat habitat with pet, poop, and water minigames."""

    BACKGROUND_FILE_DAY = "grassland_background_day.png"
    BACKGROUND_FILE_NIGHT = "grassland_background_night.png"

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

    _ICON_POOP = "poop_icon.png"

    _TROUGH_S1 = 250
    _TROUGH_S2 = 20
    _TROUGH_COLOR = (123, 63, 0)
    _WATER_COLOR = (0, 94, 209)

    _SPEED = 4

    def __init__(self, manager: SceneManager) -> None:
        self.BACKGROUND_FILE = (
            self.BACKGROUND_FILE_DAY
            if manager.context.is_day
            else self.BACKGROUND_FILE_NIGHT
        )
        super().__init__(manager)

        self._movement = AnimalMovement()
        incomplete = manager.context.checklist.get_incomplete_tasks()

        self._pet_task_active = "meerkat_pet" in incomplete

        self._poop_task_active = "meerkat_poop" in incomplete
        self._poop_cleared = False
        self._waste_positions = []
        self._waste_clicked = []

        raw = pygame.image.load(os.path.join("assets", "images", "poop_icon.png")).convert_alpha()
        w, h = raw.get_size()
        self._waste_sprite = pygame.transform.smoothscale(raw, (int(w * 0.12), int(h * 0.12)))

        if self._poop_task_active:
            self._waste_positions = [pygame.Vector2(850, 450)]
            self._waste_clicked = [False]

        self._water_task_active = "meerkat_water" in incomplete
        if self._water_task_active:
            self._init_water()

        self._build_toolbar()

    def _init_water(self):
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
        def v3(x, y, direction, droppings=False):
            return Animal(
                x=x,
                y=y,
                layer_files=self._LAYERS_V3,
                subfolder=self._SUBFOLDER,
                scale=0.75,
                direction=direction,
                speed=self._SPEED,
                animate_fn=self._animate,
                draw_fn=self._draw,
                has_droppings=droppings,
            )

        def v1(x, y):
            return Animal(
                x=x,
                y=y,
                layer_files=self._LAYERS_V1,
                subfolder=self._SUBFOLDER,
                scale=0.65,
                speed=0,
                animate_fn=None,
                draw_fn=self._draw,
            )

        def v2(x, y):
            return Animal(
                x=x,
                y=y,
                layer_files=self._LAYERS_V2,
                subfolder=self._SUBFOLDER,
                scale=0.65,
                speed=0,
                animate_fn=None,
                draw_fn=self._draw,
            )

        if self._water_task_active:
            return [v3(700, 230, 1, droppings=self._poop_task_active)]

        return [
            v1(200, 350),
            v2(500, 250),
            v3(700, 150, 1),
            v3(850, 450, -1, droppings=self._poop_task_active),
        ]

    @staticmethod
    def _animate(animal):
        t = animal.time
        swing = math.sin(t * 10) * 10

        animal.layer_angles[0] = swing
        animal.layer_angles[1] = -swing
        animal.layer_angles[4] = -swing
        animal.layer_angles[5] = swing
        animal.layer_angles[2] = math.sin(t * 3) * 6
        animal.layer_angles[6] = math.sin(t * 4) * 2

    def _draw(self, animal, screen):
        should_flip = animal.facing_left != animal.default_facing_left
        body_w = animal.layers[0].get_width() if animal.layers else 0
        body_pos = pygame.Vector2(animal.x + body_w / 2, animal.y)

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

            img, rect = self._movement.rotate_image(
                layer,
                angle,
                pygame.Vector2(layer.get_width() // 2, layer.get_height() // 2),
            )

            pos = body_pos
            if ("1_" in name or "2_" in name) and "head" in name:
                pos = pygame.Vector2(body_pos.x, body_pos.y + head_bob)

            rect.center = pos

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

        rect = self._waste_sprite.get_rect(center=(850, 450))
        if rect.collidepoint(pos):
            self._poop_cleared = True
            if self._btn_poop:
                self._btn_poop.enabled = False
                self._btn_poop.greyed = True
            self._manager.context.checklist.complete_task("meerkat_poop")
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

        meerkat = self._animals[0]

        if self._drink_timer > 0:
            self._drink_timer -= dt
            if self._drink_timer <= 0:
                meerkat.speed = self._SPEED
            return

        super().update(dt)

        screen = pygame.display.get_surface()
        rect = self._trough_rect(screen)

        body_w = meerkat.layers[0].get_width() if meerkat.layers else 0
        cx = meerkat.x + body_w // 2

        if rect.left <= cx <= rect.right:
            if not self._pass_counted:
                self._pass_counted = True
                self._passes_until_drink -= 1
                if self._passes_until_drink <= 0 < self._water_level:
                    meerkat.speed = 0
                    self._drink_timer = self._drink_duration
                    self._passes_until_drink = random.randint(1, 3)
                    self._water_level = max(0, self._water_level - self._decrement)
        else:
            self._pass_counted = False

    def draw(self, screen):
        super().draw(screen)

        if not self._poop_cleared and self._poop_task_active:
            rect = self._waste_sprite.get_rect(center=(850, 450))
            screen.blit(self._waste_sprite, rect)

        if self._btn_poop:
            self._btn_poop.draw(screen)

        if self._water_task_active:
            self._draw_trough(screen)
            self._draw_trough_instruction(screen)

            if self._water_level >= self._max_water_level:
                self._manager.context.checklist.complete_task("meerkat_water")
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
        self._manager.context.checklist.complete_task("meerkat_pet")
        from checklist_scene import ChecklistScene
        self._manager.push(ChecklistScene(self._manager, self._manager.context.checklist))
