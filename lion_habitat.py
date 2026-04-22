import os
import math
import pygame

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal
from animal_movement import AnimalMovement


class LionHabitat(HabitatScene):
    """Lion habitat with pet, poop, water, and feed minigames."""

    BACKGROUND_FILE_DAY = "savanna_background_day.png"
    BACKGROUND_FILE_NIGHT = "savanna_background_night.png"

    _SUBFOLDER = os.path.join("assets", "animals", "lion")

    _LAYERS_BASE = [
        "lion_hind_back_upper.png",
        "lion_hind_back_lower.png",
        "lion_hind_back_paw.png",
        "lion_hind_front_upper.png",
        "lion_hind_front_lower.png",
        "lion_hind_front_paw.png",
        "lion_tail.png",
        "lion_body.png",
        "lion_fore_back_upper.png",
        "lion_fore_back_lower.png",
        "lion_fore_back_paw.png",
        "lion_fore_front_upper.png",
        "lion_fore_front_lower.png",
        "lion_fore_front_paw.png",
        "lion_neck.png",
    ]

    _LAYERS_MALE = _LAYERS_BASE + ["lion_mane.png", "lion_head.png"]
    _LAYERS_FEMALE = _LAYERS_BASE + ["lion_head.png"]

    _ICON_POOP = "poop_icon.png"

    _SPEED = 1.2

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
        super().__init__(manager)

        self._movement = AnimalMovement()
        incomplete = manager.context.checklist.get_incomplete_tasks()

        self._pet_task_active = "lion_pet" in incomplete
        self._poop_active = "lion_poop" in incomplete
        self._water_active = "lion_water" in incomplete
        self._feed_active = "lion_feed" in incomplete

        self._water_level = 75
        self._feed_level = 75
        self._pass_counted = False
        self._interaction_timer = 0.0

        raw = pygame.image.load(
            os.path.join("assets", "images", "poop_icon.png")
        ).convert_alpha()
        w, h = raw.get_size()
        self._waste_sprite = pygame.transform.smoothscale(
            raw,
            (int(w * 0.12), int(h * 0.12))
        )

        self._waste_positions = [
            pygame.Vector2(200, 500),
            pygame.Vector2(800, 600)
        ] if self._poop_active else []

        self._waste_clicked = [False] * len(self._waste_positions)

        self._font = pygame.font.SysFont(None, 32)
        self._build_toolbar()

    def _get_station_rects(self):
        sw, sh = pygame.display.get_surface().get_size()
        w_rect = pygame.Rect(sw // 2 - self._X_OFFSET - self._STATION_S1 // 2,
                             sh // 2 + self._Y_OFFSET - self._STATION_S1 // 2,
                             self._STATION_S1, self._STATION_S1)
        f_rect = pygame.Rect(sw // 2 + self._X_OFFSET - self._STATION_S1 // 2,
                             sh // 2 + self._Y_OFFSET - self._STATION_S1 // 2,
                             self._STATION_S1, self._STATION_S1)
        return w_rect, f_rect

    def create_animals(self) -> list[Animal]:
        def make(x, y, layers, direction, speed=None, droppings=False):
            return Animal(
                x=x,
                y=y,
                layer_files=layers,
                subfolder=self._SUBFOLDER,
                scale=0.45,
                default_facing_left=True,
                direction=direction,
                speed=speed or self._SPEED,
                animate_fn=self._animate,
                draw_fn=self._draw,
                has_droppings=droppings,
            )

        if self._water_active or self._feed_active:
            return [
                make(
                    600,
                    200,
                    self._LAYERS_FEMALE,
                    -1,
                    droppings=self._poop_active
                )
            ]

        return [
            make(
                600,
                200,
                self._LAYERS_FEMALE,
                -1,
                droppings=self._poop_active
            ),
            make(200, 500, self._LAYERS_MALE, 1),
        ]

    @staticmethod
    def _animate(animal):
        t = animal.time
        swing = math.sin(t * 6) * 10

        hbu, hbl = 0, 1
        hfu, hfl = 3, 4
        fbu, fbl = 8, 9
        ffu, ffl = 11, 12
        paw = 2

        animal.layer_angles[hbu] = swing
        animal.layer_angles[hbl] = swing
        animal.layer_angles[hbu + paw] = swing

        animal.layer_angles[hfu] = -swing
        animal.layer_angles[hfl] = -swing
        animal.layer_angles[hfu + paw] = -swing

        animal.layer_angles[fbu] = -swing
        animal.layer_angles[fbl] = -swing
        animal.layer_angles[fbu + paw] = -swing

        animal.layer_angles[ffu] = swing
        animal.layer_angles[ffl] = swing
        animal.layer_angles[ffu + paw] = swing

    def _draw(self, animal, screen):
        should_flip = animal.facing_left != animal.default_facing_left
        body_w = animal.layers[7].get_width() if animal.layers else 0
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
                    pygame.Vector2(
                        layer.get_width() // 2,
                        layer.get_height() // 2
                    )
                )

        for layer, angle, pivot in (
                zip(animal.layers, animal.layer_angles, pivots)
        ):
            img, rect = self._movement.rotate_image(layer, angle, pivot)
            rect.center = body_pos
            if should_flip:
                img = pygame.transform.flip(img, True, False)
            screen.blit(img, rect)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        super().handle_events(events)
        w_rect, f_rect = self._get_station_rects()
        for e in events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self._water_active and w_rect.collidepoint(e.pos):
                    self._water_level = min(100, self._water_level + 2)
                elif self._feed_active and f_rect.collidepoint(e.pos):
                    self._feed_level = min(100, self._feed_level + 2)

                for i, p in enumerate(self._waste_positions):
                    if not self._waste_clicked[i]:
                        r = self._waste_sprite.get_rect(
                            center=(
                                int(p.x),
                                int(p.y)
                            )
                        )
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

        lion = self._animals[0]
        w_rect, f_rect = self._get_station_rects()
        body_w = lion.layers[0].get_width() if lion.layers else 0
        lx = lion.x + body_w // 2

        current_zone = None
        if self._water_active and w_rect.left <= lx <= w_rect.right:
            current_zone = "water"
        elif self._feed_active and f_rect.left <= lx <= f_rect.right:
            current_zone = "feed"

        if current_zone:
            if not self._pass_counted:
                self._pass_counted = True
                level = (
                    self._water_level
                    if current_zone == "water"
                    else self._feed_level
                )
                if level > 0:
                    lion.speed = 0
                    self._interaction_timer = 1.5
                    if current_zone == "water":
                        self._water_level = max(0, self._water_level - 40)
                    else:
                        self._feed_level = max(0, self._feed_level - 40)
        else:
            self._pass_counted = False

    def draw(self, screen: pygame.Surface) -> None:
        super().draw(screen)
        w_rect, f_rect = self._get_station_rects()

        if self._water_active:
            self._draw_station(
                screen,
                w_rect,
                self._water_level,
                self._WATER_COLOR,
                self._TROUGH_COLOR
            )
        if self._feed_active:
            self._draw_station(
                screen,
                f_rect,
                self._feed_level,
                self._FOOD_COLOR,
                self._BOWL_COLOR
            )

        if self._water_active or self._feed_active:
            raw_txt = (
                "Click the trough to fill it with water!"
                if self._water_active
                else "Click the bowl to fill it with food!"
            )
            if self._water_active and self._feed_active:
                raw_txt = "Click the stations to refill them!"

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

        if self._poop_active and all(self._waste_clicked):
            self._poop_active = False
            self._complete_task("lion_poop")
        if self._water_active and self._water_level >= 100:
            self._water_active = False
            self._complete_task("lion_water")
        if self._feed_active and self._feed_level >= 100:
            self._feed_active = False
            self._complete_task("lion_feed")

    def draw_ground_layer(self, screen: pygame.Surface) -> None:
        """Use the ground layer to draw in the animal waste
        behind the animals."""
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
        pygame.draw.rect(
            screen,
            fill_col,
            (rect.x + s2, rect.y + s1 - s2 - fill_h, s1 - s2 * 2, fill_h)
        )
        pygame.draw.rect(
            screen,
            border_col,
            (rect.x, rect.y + s1 - s2, s1, s2)
        )
        pygame.draw.rect(
            screen,
            border_col,
            (rect.x, rect.y, s2, s1)
        )
        pygame.draw.rect(
            screen,
            border_col,
            (rect.x + s1 - s2, rect.y, s2, s1)
        )

    def _complete_task(self, task):
        self._manager.context.checklist.complete_task(task)
        from checklist_scene import ChecklistScene
        self._manager.pop()
        self._manager.push(
            ChecklistScene(
                self._manager,
                self._manager.context.checklist
            )
        )

    def _on_pet_complete(self):
        self._complete_task("lion_pet")
