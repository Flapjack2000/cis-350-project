import os
import math
import random
import pygame
from scene import SceneManager
from habitat_scene import HabitatScene, _IconButton
from animal import Animal
from animal_movement import AnimalMovement

_SUBFOLDER = os.path.join("assets", "animals", "penguin")
WADDLE_SPEED = 6
WADDLE_AMPLITUDE = 10


class PenguinHabitat(HabitatScene):
    """Habitat scene for penguins with pet, water, and feed minigames."""

    BACKGROUND_FILE_DAY = "aquatic_background_day.png"
    BACKGROUND_FILE_NIGHT = "aquatic_background_night.png"

    _STATION_S1 = 200
    _STATION_S2 = 20
    _X_OFFSET = 240
    _Y_OFFSET = 220

    _TROUGH_COLOR = (100, 100, 100)
    _WATER_COLOR = (0, 150, 255)
    _BOWL_COLOR = (60, 60, 60)
    _FOOD_COLOR = (200, 200, 200)

    _ICON_WATER = "water_icon.png"
    _ICON_FOOD = "food_icon.png"

    def __init__(self, manager: SceneManager) -> None:
        self.BACKGROUND_FILE = (
            self.BACKGROUND_FILE_DAY
            if manager.context.is_day
            else self.BACKGROUND_FILE_NIGHT
        )
        super().__init__(manager)

        self._movement = AnimalMovement()
        incomplete = manager.context.checklist.get_incomplete_tasks()

        self._pet_task_active = "penguin_pet" in incomplete
        self._water_active = "penguin_water" in incomplete
        self._feed_active = "penguin_feed" in incomplete

        self._water_level = 75 if self._water_active else 100
        self._feed_level = 75 if self._feed_active else 100

        self._pass_counted = False
        self._interaction_timer = 0.0

        self._water_passes = 0
        self._water_threshold = random.randint(1, 3)
        self._feed_passes = 0
        self._feed_threshold = random.randint(1, 3)

        self._font = pygame.font.SysFont(None, 32)

        self._btn_water = None
        self._btn_food = None

        self._build_toolbar()

    def _build_toolbar(self) -> None:
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

    def _get_station_rects(self):
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
        if self._water_active or self._feed_active:
            return [
                Animal(
                    x=100, y=200,
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

        return [
            Animal(
                x=100, y=200,
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
                x=500, y=100,
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

    @staticmethod
    def _animate(animal: Animal) -> None:
        t = animal.time
        speed_factor = abs(animal.direction * animal.speed)

        animal.waddle_angle = math.sin(t * WADDLE_SPEED) * WADDLE_AMPLITUDE * (
            1.0 if speed_factor > 0 else 0.2
        )
        animal.y_offset = math.sin(t * WADDLE_SPEED * 2) * 2 * speed_factor

    def _draw_animal(self, animal: Animal, screen: pygame.Surface) -> None:
        if not animal.layers:
            return

        img = animal.layers[0]
        base_pivot = pygame.Vector2(img.get_width() // 2,
                                    img.get_height() - 15)
        should_flip = animal.facing_left != animal.default_facing_left

        draw_img = img
        draw_pivot = base_pivot

        if should_flip:
            draw_img = pygame.transform.flip(img, True, False)
            draw_pivot = pygame.Vector2(img.get_width() -
                                        base_pivot.x, base_pivot.y)

        rotated_img, rect = self._movement.rotate_image(
            draw_img,
            getattr(animal, "waddle_angle", 0),
            (draw_pivot.x, draw_pivot.y)
        )

        rect.x += int(animal.x)
        rect.y += int(animal.y + getattr(animal, "y_offset", 0))
        screen.blit(rotated_img, rect)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        super().handle_events(events)
        w_rect, f_rect = self._get_station_rects()

        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:

                if self._btn_water and self._btn_water.is_clicked(e.pos):
                    prev = self._water_active or self._feed_active
                    self._water_active = (
                            "penguin_water" in
                            self._manager.context.checklist.
                            get_incomplete_tasks()
                    )
                    self._feed_active = False
                    if prev != (self._water_active or self._feed_active):
                        self._rebuild_animals_if_needed()

                elif self._btn_food and self._btn_food.is_clicked(e.pos):
                    prev = self._water_active or self._feed_active
                    self._feed_active = (
                            "penguin_feed" in
                            self._manager.context.checklist.
                            get_incomplete_tasks()
                    )
                    self._water_active = False
                    if prev != (self._water_active or self._feed_active):
                        self._rebuild_animals_if_needed()

                if self._water_active and w_rect.collidepoint(e.pos):
                    self._water_level = min(100, self._water_level + 2)
                elif self._feed_active and f_rect.collidepoint(e.pos):
                    self._feed_level = min(100, self._feed_level + 2)

    def update(self, dt: float) -> None:
        if self._interaction_timer > 0:
            self._interaction_timer -= dt
            if self._interaction_timer <= 0 and self._animals:
                self._animals[0].speed = 0.5
            super().update(dt)
            return

        super().update(dt)

        if not self._animals or not (self._water_active or self._feed_active):
            return

        penguin = self._animals[0]
        w_rect, f_rect = self._get_station_rects()
        px = penguin.x + (penguin.layers[0].get_width() //
                          2 if penguin.layers else 0)

        current_zone = None
        if self._water_active and w_rect.left <= px <= w_rect.right:
            current_zone = "water"
        elif self._feed_active and f_rect.left <= px <= f_rect.right:
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
                    penguin.speed = 0
                    self._interaction_timer = 2.0
                    if current_zone == "water":
                        self._water_level = max(0, self._water_level - 35)
                        self._water_passes = 0
                        self._water_threshold = random.randint(1, 3)
                    else:
                        self._feed_level = max(0, self._feed_level - 35)
                        self._feed_passes = 0
                        self._feed_threshold = random.randint(1, 3)
                else:
                    penguin.speed = 0.5
        else:
            self._pass_counted = False

        if self._water_active and self._water_level >= 100:
            self._water_active = False
            self._complete_task("penguin_water")

        if self._feed_active and self._feed_level >= 100:
            self._feed_active = False
            self._complete_task("penguin_feed")

    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)

        if self._btn_water:
            self._btn_water.draw(screen)
        if self._btn_food:
            self._btn_food.draw(screen)

        w_rect, f_rect = self._get_station_rects()

        if self._water_active:
            self._draw_station(screen, w_rect,
                               self._water_level,
                               self._WATER_COLOR,
                               self._TROUGH_COLOR)
        if self._feed_active:
            self._draw_station(screen, f_rect,
                               self._feed_level,
                               self._FOOD_COLOR,
                               self._BOWL_COLOR)

        if self._water_active or self._feed_active:
            if self._water_active and self._feed_active:
                raw_txt = ("Refill the water and "
                           "food stations for the penguins!")
            elif self._water_active:
                raw_txt = "Refill the water trough for the penguins!"
            else:
                raw_txt = "Refill the food bowl for the penguins!"

            words, lines, line = raw_txt.split(' '), [], ''
            for word in words:
                if self._font.size(line + word)[0] < 180:
                    line += (word + ' ')
                else:
                    lines.append(line)
                    line = word + ' '
            lines.append(line)

            y_off = w_rect.top + 20
            for ln in lines:
                surf = self._font.render(ln.strip(), True, (0, 0, 0))
                screen.blit(surf, (40, y_off))
                y_off += surf.get_height() + 4

    def _draw_station(self, screen, rect, level, fill_col, border_col):
        s1, s2 = self._STATION_S1, self._STATION_S2
        fill_h = int((s1 - s2) * (level / 100))
        (pygame.draw.rect
         (screen, fill_col, (rect.x + s2, rect.y + s1 - s2 - fill_h,
                             s1 - s2 * 2, fill_h)))
        (pygame.draw.rect
         (screen, border_col, (rect.x, rect.y + s1 - s2, s1, s2)))
        (pygame.draw.rect
         (screen, border_col, (rect.x, rect.y, s2, s1)))
        (pygame.draw.rect
         (screen, border_col, (rect.x + s1 - s2, rect.y, s2, s1)))

    def _complete_task(self, task):
        self._manager.context.checklist.complete_task(task)
        from checklist_scene import ChecklistScene
        self._manager.pop()
        self._manager.push(ChecklistScene
                           (self._manager, self._manager.context.checklist))

    def _on_pet_complete(self):
        self._complete_task("penguin_pet")
