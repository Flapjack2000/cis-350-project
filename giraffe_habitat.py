import os
import math
import pygame

from math_helper import MathHelper
from scene import SceneManager
from habitat_scene import HabitatScene, _IconButton
from animal import Animal


class GiraffeHabitat(HabitatScene):
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
    _ICON_WATER = "water_icon.png"
    _ICON_FOOD = "food_icon.png"

    _GIRAFFE_SPEED = 1.2
    _FRONT_PIVOT = pygame.Vector2(25, 15)
    _HIND_PIVOT = pygame.Vector2(25, 15)

    _STATION_S1 = 200
    _STATION_S2 = 20
    _X_OFFSET = 240
    _Y_OFFSET = 220

    _TROUGH_COLOR = (123, 63, 0)
    _WATER_COLOR = (0, 94, 209)
    _BOWL_COLOR = (80, 40, 20)
    _FOOD_COLOR = (194, 153, 115)

    def __init__(self, manager: SceneManager) -> None:
        self.BACKGROUND_FILE = (
            self.BACKGROUND_FILE_DAY
            if manager.context.is_day
            else self.BACKGROUND_FILE_NIGHT
        )

        incomplete = manager.context.checklist.get_incomplete_tasks()
        self._pet_task_active = "giraffe_pet" in incomplete

        super().__init__(manager)

        self._poop_active = "giraffe_poop" in incomplete
        self._water_active = "giraffe_water" in incomplete
        self._feed_active = "giraffe_feed" in incomplete

        self._water_level = 75
        self._feed_level = 75
        self._pass_counted = False
        self._interaction_timer = 0.0

        self._btn_water = None
        self._btn_food = None

        raw = pygame.image.load(
            os.path.join("assets", "images", self._ICON_POOP)
        ).convert_alpha()
        self._waste_sprite = pygame.transform.smoothscale(
            raw,
            (int(raw.get_width() * 0.12), int(raw.get_height() * 0.12))
        )

        self._waste_positions = [
            pygame.Vector2(200, 500),
            pygame.Vector2(800, 300)
        ] if self._poop_active else []

        self._waste_clicked = [False] * len(self._waste_positions)
        self._font = pygame.font.SysFont(None, 32)

        self._build_toolbar()

    def _build_toolbar(self) -> None:
        """Create minigame toolbar icons."""
        super()._build_toolbar()

        pad = 12
        gap = 12

        base_x = self._btn_pet.rect.right if self._btn_pet else pad

        self._btn_water = _IconButton(
            os.path.join("assets", "images", self._ICON_WATER),
            topleft=(base_x + gap, pad),
            enabled=self._water_active,
            greyed=not self._water_active,
        )

        self._btn_food = _IconButton(
            os.path.join("assets", "images", self._ICON_FOOD),
            topleft=(self._btn_water.rect.right + gap, pad),
            enabled=self._feed_active,
            greyed=not self._feed_active,
        )

    def _rebuild_animals_if_needed(self) -> None:
        """Recreate animals when habitat mode changes."""
        self._animals = self.create_animals()
        for animal in self._animals:
            animal.load(self._base_dir)

    def on_enter(self) -> None:
        super().on_enter()
        incomplete = self._manager.context.checklist.get_incomplete_tasks()
        self._pet_task_active = "giraffe_pet" in incomplete
        self._build_toolbar()

    def _get_station_rects(self):
        """Return the Rect objects that represent the food/water stations."""
        sw, sh = pygame.display.get_surface().get_size()
        w_rect = pygame.Rect(sw // 2 - self._X_OFFSET - self._STATION_S1 // 2,
                             sh // 2 + self._Y_OFFSET - self._STATION_S1 // 2,
                             self._STATION_S1, self._STATION_S1)
        f_rect = pygame.Rect(sw // 2 + self._X_OFFSET - self._STATION_S1 // 2,
                             sh // 2 + self._Y_OFFSET - self._STATION_S1 // 2,
                             self._STATION_S1, self._STATION_S1)
        return w_rect, f_rect

    def create_animals(self) -> list[Animal]:
        def make(x, y, direction):
            return Animal(
                x=x,
                y=y,
                layer_files=self._LAYER_FILES,
                subfolder=self._SUBFOLDER,
                scale=0.5,
                default_facing_left=True,
                direction=direction,
                speed=self._GIRAFFE_SPEED,
                animate_fn=self._animate,
                draw_fn=self._draw
            )

        if self._water_active or self._feed_active:
            return [make(200, 300, 1)]
        return [make(200, 300, 1), make(600, 500, -1)]

    @staticmethod
    def _animate(animal: Animal) -> None:
        swing = math.sin(animal.time * 4) * 10
        animal.layer_angles[1] = animal.layer_angles[2] = swing
        animal.layer_angles[9] = animal.layer_angles[10] = swing
        animal.layer_angles[3] = animal.layer_angles[4] = -swing
        animal.layer_angles[7] = animal.layer_angles[8] = -swing

    def _draw(self, animal: Animal, screen: pygame.Surface) -> None:
        should_flip = animal.facing_left != animal.default_facing_left
        body_pos = pygame.Vector2(
            animal.x + (animal.layers[6].get_width() / 2 if
                        animal.layers else 0),
            animal.y
        )

        for i, (layer, angle) in (
                enumerate(zip(animal.layers, animal.layer_angles))):
            name = self._LAYER_FILES[i]
            pivot = self._HIND_PIVOT if "hind" in name else (
                self._FRONT_PIVOT if "fore" in name else pygame.Vector2(
                    layer.get_width() // 2,
                    layer.get_height() // 2
                )
            )

            img, rect = MathHelper.rotate_image(layer, angle, pivot)
            rect.center = (int(body_pos.x), int(body_pos.y))

            if should_flip:
                img = pygame.transform.flip(img, True, False)

            screen.blit(img, rect)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        super().handle_events(events)
        w_rect, f_rect = self._get_station_rects()

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:

                if self._btn_water and self._btn_water.is_clicked(e.pos):
                    prev = self._water_active or self._feed_active
                    self._water_active = True
                    self._feed_active = False
                    if prev != (self._water_active or self._feed_active):
                        self._rebuild_animals_if_needed()

                elif self._btn_food and self._btn_food.is_clicked(e.pos):
                    prev = self._water_active or self._feed_active
                    self._feed_active = True
                    self._water_active = False
                    if prev != (self._water_active or self._feed_active):
                        self._rebuild_animals_if_needed()

                if self._water_active and w_rect.collidepoint(e.pos):
                    self._water_level = min(100, self._water_level + 2)
                elif self._feed_active and f_rect.collidepoint(e.pos):
                    self._feed_level = min(100, self._feed_level + 2)

                for i, p in enumerate(self._waste_positions):
                    if not self._waste_clicked[i]:
                        r = (self._waste_sprite.get_rect
                             (center=(int(p.x), int(p.y))))
                        if r.collidepoint(e.pos):
                            self._waste_clicked[i] = True

    def update(self, dt: float) -> None:
        if self._interaction_timer > 0:
            self._interaction_timer -= dt
            if self._interaction_timer <= 0 and self._animals:
                self._animals[0].speed = self._GIRAFFE_SPEED
            super().update(dt)
            return

        super().update(dt)
        if not self._animals or not (self._water_active or self._feed_active):
            return

        giraffe = self._animals[0]
        w_rect, f_rect = self._get_station_rects()

        gx = giraffe.x + (giraffe.layers[6].get_width() //
                          2 if giraffe.layers else 0)

        current_zone = None
        if self._water_active and w_rect.left <= gx <= w_rect.right:
            current_zone = "water"
        elif self._feed_active and f_rect.left <= gx <= f_rect.right:
            current_zone = "feed"

        if current_zone:
            if not self._pass_counted:
                self._pass_counted = True
                level = self._water_level if current_zone == "water" \
                    else self._feed_level
                if level > 0:
                    giraffe.speed = 0
                    self._interaction_timer = 1.5
                    if current_zone == "water":
                        self._water_level = max(0, self._water_level - 50)
                    else:
                        self._feed_level = max(0, self._feed_level - 50)
        else:
            self._pass_counted = False

    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)

        if self._btn_water:
            self._btn_water.draw(screen)
        if self._btn_food:
            self._btn_food.draw(screen)

        w_rect, f_rect = self._get_station_rects()

        if self._water_active:
            self._draw_station(screen, w_rect, self._water_level,
                               self._WATER_COLOR, self._TROUGH_COLOR)
        if self._feed_active:
            self._draw_station(screen, f_rect, self._feed_level,
                               self._FOOD_COLOR, self._BOWL_COLOR)

        if self._poop_active and all(self._waste_clicked):
            self._poop_active = False
            self._complete_task("giraffe_poop")
        if self._water_active and self._water_level >= 100:
            self._water_active = False
            self._complete_task("giraffe_water")
        if self._feed_active and self._feed_level >= 100:
            self._feed_active = False
            self._complete_task("giraffe_feed")

    def draw_ground_layer(self, screen: pygame.Surface) -> None:
        for i, pos in enumerate(self._waste_positions):
            if not self._waste_clicked[i]:
                screen.blit(
                    self._waste_sprite,
                    self._waste_sprite.get_rect(center=(int(pos.x),
                                                        int(pos.y)))
                )

    def _draw_station(self, screen, rect, level, fill_col, border_col):
        s1, s2 = self._STATION_S1, self._STATION_S2
        fill_h = int((s1 - s2) * (level / 100))
        pygame.draw.rect(screen, fill_col, (rect.x + s2, rect.y + s1 - s2 -
                                            fill_h, s1 - s2 * 2, fill_h))
        pygame.draw.rect(screen, border_col, (rect.x, rect.y + s1 - s2,
                                              s1, s2))
        pygame.draw.rect(screen, border_col, (rect.x, rect.y, s2, s1))
        pygame.draw.rect(screen, border_col, (rect.x + s1 - s2, rect.y,
                                              s2, s1))

    def _complete_task(self, task):
        self._manager.context.checklist.complete_task(task)
        from checklist_scene import ChecklistScene
        self._manager.pop()
        self._manager.push(ChecklistScene
                           (self._manager, self._manager.context.checklist))

    def _on_pet_complete(self):
        self._complete_task("giraffe_pet")
