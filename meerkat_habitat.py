import os
import math
import random

import pygame

from math_helper import MathHelper
from scene import SceneManager
from habitat_scene import HabitatScene, _IconButton
from animal import Animal


class MeerkatHabitat(HabitatScene):
    """Meerkat habitat with pet, poop, water, and feed minigames."""

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
    _ICON_WATER = "water_icon.png"
    _ICON_FOOD = "food_icon.png"

    _SPEED = 4

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
        super().__init__(manager)

        incomplete = manager.context.checklist.get_incomplete_tasks()

        self._pet_task_active = "meerkat_pet" in incomplete
        self._poop_active = "meerkat_poop" in incomplete
        self._water_active = "meerkat_water" in incomplete
        self._feed_active = "meerkat_feed" in incomplete

        self._water_level = 75
        self._feed_level = 75
        self._pass_counted = False
        self._interaction_timer = 0.0

        self._water_passes = 0
        self._water_threshold = random.randint(1, 3)
        self._feed_passes = 0
        self._feed_threshold = random.randint(1, 3)

        self._btn_water = None
        self._btn_food = None

        raw = pygame.image.load(
            os.path.join("assets", "images", "poop_icon.png")
        ).convert_alpha()
        w, h = raw.get_size()
        self._waste_sprite = pygame.transform.smoothscale(
            raw,
            (int(w * 0.12), int(h * 0.12))
        )

        self._waste_positions = (
            [
                pygame.Vector2(850, 450),
                pygame.Vector2(200, 500)
            ]
            if self._poop_active
            else []
        )
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

    def _get_station_rects(self) -> tuple[pygame.Rect, pygame.Rect]:
        """Return the Rect objects that represent the food/water stations."""
        sw, sh = pygame.display.get_surface().get_size()
        w_rect = pygame.Rect(
            sw // 2 - self._X_OFFSET - self._STATION_S1 // 2,
            sh // 2 + self._Y_OFFSET - self._STATION_S1 // 2,
            self._STATION_S1,
            self._STATION_S1
        )
        f_rect = pygame.Rect(
            sw // 2 + self._X_OFFSET - self._STATION_S1 // 2,
            sh // 2 + self._Y_OFFSET - self._STATION_S1 // 2,
            self._STATION_S1,
            self._STATION_S1
        )
        return w_rect, f_rect

    def create_animals(self) -> list[Animal]:
        """


        Returns:
            list[Animal]:
        """

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
                draw_fn=self._draw_animal,
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
                draw_fn=self._draw_animal,
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
                draw_fn=self._draw_animal,
            )

        if self._water_active or self._feed_active:
            return [v3(700, 230, 1, droppings=self._poop_active)]

        return [
            v1(200, 350),
            v2(500, 250),
            v3(700, 150, 1),
            v3(850, 450, -1, droppings=self._poop_active),
        ]

    @staticmethod
    def _animate(animal: Animal):
        """Animate a meerkat.

        Args:
            animal (Animal): The meerkat to animate.
        """
        t = animal.time
        swing = math.sin(t * 10) * 10

        animal.layer_angles[0] = swing
        animal.layer_angles[1] = -swing
        animal.layer_angles[4] = -swing
        animal.layer_angles[5] = swing
        animal.layer_angles[2] = math.sin(t * 3) * 6
        animal.layer_angles[6] = math.sin(t * 4) * 2

    @staticmethod
    def _draw_animal(animal: Animal, screen: pygame.Surface):
        """Draw a meerkat on the screen.

        Args:
            animal (Animal): the animal to render
            screen (pygame.Surface): the screen to render on
        """
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

        for i, (layer, angle) in (
                enumerate(zip(animal.layers, animal.layer_angles))
        ):
            name = animal.layer_files[i]

            img, rect = MathHelper.rotate_image(
                layer,
                angle,
                pygame.Vector2(
                    layer.get_width() // 2,
                    layer.get_height() // 2
                ),
            )

            pos = body_pos
            if ("1_" in name or "2_" in name) and "head" in name:
                pos = pygame.Vector2(body_pos.x, body_pos.y + head_bob)

            rect.center = (int(pos.x), int(pos.y))

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
                    self._water_active = not self._water_active
                    now = self._water_active or self._feed_active
                    if prev != now:
                        self._rebuild_animals_if_needed()

                elif self._btn_food and self._btn_food.is_clicked(e.pos):
                    prev = self._water_active or self._feed_active
                    self._feed_active = not self._feed_active
                    now = self._water_active or self._feed_active
                    if prev != now:
                        self._rebuild_animals_if_needed()

                if self._water_active and w_rect.collidepoint(e.pos):
                    self._water_level = min(100, self._water_level + 2)
                elif self._feed_active and f_rect.collidepoint(e.pos):
                    self._feed_level = min(100, self._feed_level + 2)

                for i, p in enumerate(self._waste_positions):
                    if not self._waste_clicked[i]:
                        r = self._waste_sprite.get_rect(center=(int(p.x),
                                                                int(p.y)))
                        if r.collidepoint(e.pos):
                            self._waste_clicked[i] = True

    def update(self, dt: float) -> None:
        if self._interaction_timer > 0:
            self._interaction_timer -= dt
            if self._interaction_timer <= 0 and self._animals:
                self._animals[0].speed = self._SPEED
            super().update(dt)
            return

        super().update(dt)
        if not self._animals or not (self._water_active or self._feed_active):
            return

        meerkat = self._animals[0]
        w_rect, f_rect = self._get_station_rects()
        body_w = meerkat.layers[0].get_width() if meerkat.layers else 0
        mx = meerkat.x + body_w // 2

        current_zone = None
        if self._water_active and w_rect.left <= mx <= w_rect.right:
            current_zone = "water"
        elif self._feed_active and f_rect.left <= mx <= f_rect.right:
            current_zone = "feed"

        if current_zone:
            if not self._pass_counted:
                self._pass_counted = True
                if current_zone == "water":
                    self._water_passes += 1
                    should_stop = self._water_passes >= self._water_threshold
                else:
                    self._feed_passes += 1
                    should_stop = self._feed_passes >= self._feed_threshold

                level = self._water_level if (
                        current_zone == "water") else self._feed_level

                if should_stop and level > 0:
                    meerkat.speed = 0
                    self._interaction_timer = 1.5
                    if current_zone == "water":
                        self._water_level = max(0, self._water_level - 40)
                        self._water_passes = 0
                        self._water_threshold = random.randint(1, 3)
                    else:
                        self._feed_level = max(0, self._feed_level - 40)
                        self._feed_passes = 0
                        self._feed_threshold = random.randint(1, 3)
                else:
                    meerkat.speed = self._SPEED
        else:
            self._pass_counted = False

    def draw(self, screen: pygame.Surface) -> None:
        """


        Args:
            screen (pygame.Surface): the screen to draw on
        """

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
            self._complete_task("meerkat_poop")
        if self._water_active and self._water_level >= 100:
            self._water_active = False
            self._complete_task("meerkat_water")
        if self._feed_active and self._feed_level >= 100:
            self._feed_active = False
            self._complete_task("meerkat_feed")

    def draw_ground_layer(self, screen: pygame.Surface) -> None:
        """Use the ground layer to draw in the animal waste
        behind the animals.

        Args:
            screen (pygame.Surface): the screen to draw on
        """
        for i, pos in enumerate(self._waste_positions):
            if not self._waste_clicked[i]:
                screen.blit(
                    self._waste_sprite,
                    self._waste_sprite.get_rect(
                        center=(
                            int(pos.x),
                            int(pos.y)
                        )
                    )
                )

    def _draw_station(self, screen, rect, level, fill_col, border_col):
        s1, s2 = self._STATION_S1, self._STATION_S2
        fill_h = int((s1 - s2) * (level / 100))
        pygame.draw.rect(screen, fill_col, (rect.x + s2,
                                            rect.y + s1 - s2 - fill_h,
                                            s1 - s2 * 2, fill_h))
        pygame.draw.rect(screen, border_col,
                         (rect.x, rect.y + s1 - s2, s1, s2))
        pygame.draw.rect(screen, border_col,
                         (rect.x, rect.y, s2, s1))
        pygame.draw.rect(screen, border_col,
                         (rect.x + s1 - s2, rect.y, s2, s1))

    def _complete_task(self, task):
        self._manager.context.checklist.complete_task(task)
        from checklist_scene import ChecklistScene
        self._manager.pop()
        (self._manager.push
         (ChecklistScene(self._manager, self._manager.context.checklist)))

    def _on_pet_complete(self):
        self._complete_task("meerkat_pet")
