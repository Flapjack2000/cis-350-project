import os
import random
import pygame
from scene import Scene, SceneManager
from global_settings import Settings
from habitat_scene import _IconButton, ICON_SPACING, TOOLBAR_PAD

_FISH_INFO = [
    ("moorishidol.png", False, 180, 30, 0.60),
    ("sailfintang.png", False, 240, 310, 0.80),
    ("clownfish.png", True, 100, 140, 0.50),
    ("discus.png", False, 125, 400, 0.70),
    ("yellowtang.png", True, 125, 60, 0.90),
    ("yellowperch.png", False, 180, 250, 0.65),
    ("africanjewelfish.png", False, 220, 185, 0.75),
]

_SUBFOLDER = os.path.join("assets", "animals", "fish")


class _Fish:
    """Represents a single fish in the aquarium habitat."""

    def __init__(self, img_path: str, faces_right: bool, size_px: int,
                 x: float, y: float, speed: float, screen_width: int) -> None:
        raw = pygame.image.load(img_path).convert_alpha()
        w, h = raw.get_size()
        scale = size_px / h
        self.base_img = (
            pygame.transform.smoothscale(
                raw,
                (int(w * scale),
                 size_px
                 )
            )
        )

        self.faces_right = faces_right
        self.x = x
        self.y = y
        self.home_y = y
        self.speed = speed
        self.screen_width = screen_width
        self.moving_right = random.choice([True, False])

    @property
    def width(self) -> int:
        return self.base_img.get_width()

    def _respawn(self) -> None:
        self.moving_right = random.choice([True, False])
        self.x = -self.width if self.moving_right else float(self.screen_width)
        self.y = self.home_y

    def update(self, dt: float) -> None:
        move = self.speed * dt * 60
        if self.moving_right:
            self.x += move
            if self.x >= self.screen_width:
                self._respawn()
        else:
            self.x -= move
            if self.x + self.width <= 0:
                self._respawn()

    def draw(self, surface: pygame.Surface) -> None:
        should_flip = self.moving_right != self.faces_right
        img = pygame.transform.flip(self.base_img, should_flip, False)
        surface.blit(img, (int(self.x), int(self.y)))


class FishHabitat(Scene):
    """Aquarium scene with fish feeding minigame
    and navigation buttons on the right."""

    BACKGROUND_FILE = "aquarium_background.png"
    FEED_RATE = 40.0
    DECAY_RATE = 10.0
    ICON_SCALE = 0.2

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)

        self._background = None
        self._fish = []
        self._base_dir = os.path.dirname(os.path.abspath(__file__))

        self.feeding = False
        self.feed_progress = 0.0

        incomplete = self._manager.context.checklist.get_incomplete_tasks()
        self._feed_task_active = "fish_feed" in incomplete

        # Food Icon Setup (Left Side)
        raw_icon = pygame.image.load(
            os.path.join("assets", "images", "fish_food.png")
        ).convert_alpha()
        w, h = raw_icon.get_size()
        self.feed_icon = pygame.transform.smoothscale(
            raw_icon,
            (int(w * self.ICON_SCALE), int(h * self.ICON_SCALE))
        )
        self.feed_icon_grey = self.feed_icon.copy()
        self.feed_icon_grey.set_alpha(120)
        self.feed_icon_rect = (
            self.feed_icon.get_rect(
                topleft=(TOOLBAR_PAD, TOOLBAR_PAD)
            )
        )

        # Cursor Setup
        bottle = pygame.transform.rotate(raw_icon, 180)
        self.feed_bottle = pygame.transform.smoothscale(
            bottle,
            (int(w * self.ICON_SCALE * 1.1),
             int(h * self.ICON_SCALE * 1.1))
        )

        # Map is furthest right
        map_path = os.path.join("assets", "images", "map_icon.png")
        self._btn_map = (
            _IconButton(map_path, (0, 0))  # Position updated in on_enter
        )

        # Checklist is to the left of map
        check_path = os.path.join("assets", "images", "checklist_icon.png")
        self._btn_checklist = (
            _IconButton(check_path, (0, 0))  # Position updated in on_enter
        )

    def on_enter(self) -> None:
        super().on_enter()
        bg_path = os.path.join(
            self._base_dir,
            "assets",
            "images",
            self.BACKGROUND_FILE
        )
        screen_size = Settings().window["size"]
        screen_w = screen_size[0]

        # Update button positions for current screen width
        map_x = screen_w - self._btn_map.rect.width - TOOLBAR_PAD
        self._btn_map.rect.topleft = (map_x, TOOLBAR_PAD)

        checklist_x = map_x - self._btn_checklist.rect.width - ICON_SPACING
        self._btn_checklist.rect.topleft = (checklist_x, TOOLBAR_PAD)

        if os.path.exists(bg_path):
            bg = pygame.image.load(bg_path).convert()
            self._background = pygame.transform.smoothscale(bg, screen_size)
        else:
            self._background = None

        fish_dir = os.path.join(self._base_dir, _SUBFOLDER)
        margin_x = 60
        x_gap = (screen_w - margin_x * 2) // 4

        self._fish = []
        for i, (
                fname,
                faces_right,
                size_px,
                y,
                speed
        ) in enumerate(_FISH_INFO):
            path = os.path.join(fish_dir, fname)
            x = margin_x + (i % 4) * x_gap
            self._fish.append(
                _Fish(path, faces_right, size_px, x, y, speed, screen_w)
            )

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from pause_scene import PauseScene
                self._manager.push(PauseScene(self._manager))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if (
                        self._feed_task_active
                        and self.feed_icon_rect.collidepoint(mouse_pos)
                ):
                    self.feeding = True

                if self._btn_checklist.rect.collidepoint(mouse_pos):
                    from checklist_scene import ChecklistScene
                    self._manager.push(
                        ChecklistScene(
                            self._manager,
                            self._manager.context.checklist
                        )
                    )

                if self._btn_map.rect.collidepoint(mouse_pos):
                    from map_scene import MapScene
                    self._manager.push(MapScene(self._manager))

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.feeding = False

    def update(self, dt: float) -> None:
        for fish in self._fish:
            fish.update(dt)

        if self.feeding:
            if pygame.mouse.get_pressed()[0]:
                self.feed_progress += self.FEED_RATE * dt
            else:
                self.feed_progress -= self.DECAY_RATE * dt

            self.feed_progress = max(0.0, min(100.0, self.feed_progress))

            if self.feed_progress >= 100.0:
                self._handle_feed_complete()
        elif self.feed_progress > 0:
            self.feed_progress -= self.DECAY_RATE * dt
            self.feed_progress = max(0.0, self.feed_progress)

    def _handle_feed_complete(self) -> None:
        self.feed_progress = 100.0
        self.feeding = False
        self._feed_task_active = False
        self._manager.context.checklist.complete_task("fish_feed")
        from checklist_scene import ChecklistScene
        self._manager.pop()
        self._manager.push(
            ChecklistScene(
                self._manager,
                self._manager.context.checklist
            )
        )

    def draw(self, screen: pygame.Surface) -> None:
        if self._background:
            screen.blit(self._background, (0, 0))
        else:
            screen.fill((30, 100, 180))

        for fish in self._fish:
            fish.draw(screen)

        # Draw Interface
        icon = (
            self.feed_icon if self._feed_task_active else self.feed_icon_grey
        )
        screen.blit(icon, self.feed_icon_rect)
        self._btn_checklist.draw(screen)
        self._btn_map.draw(screen)

        if self.feeding:
            mouse_pos = pygame.mouse.get_pos()
            cursor_rect = self.feed_bottle.get_rect(center=mouse_pos)
            screen.blit(self.feed_bottle, cursor_rect)
            self._draw_progress_bar(screen)

    def _draw_progress_bar(self, screen: pygame.Surface) -> None:
        bar_w, bar_h = 220, 18
        screen_w = screen.get_width()
        bar_x = (screen_w - bar_w) // 2
        bar_y = TOOLBAR_PAD

        pygame.draw.rect(
            screen,
            (60, 60, 60),
            (bar_x, bar_y, bar_w, bar_h),
            border_radius=4
        )
        fill_w = int(bar_w * (self.feed_progress / 100))
        pygame.draw.rect(
            screen,
            (80, 220, 120),
            (bar_x, bar_y, fill_w, bar_h),
            border_radius=4
        )
