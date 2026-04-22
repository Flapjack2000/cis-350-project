import os
import pygame
from pygame import Rect
from abc import abstractmethod
from scene import Scene, SceneManager
from animal import Animal

PET_RATE = 0.4
DECAY_RATE = 0.05
ICON_SCALE = 0.18
ICON_SPACING = 12
TOOLBAR_PAD = 12


class _IconButton:
    """Clickable icon button.

    Args:
        image_path: Path to icon image.
        topleft: Top-left position.
        scale: Scale factor.
        enabled: Whether clickable.
        greyed: Whether dimmed.
    """
    rect: Rect

    def __init__(
            self,
            image_path: str,
            topleft: tuple[int, int],
            scale: float = ICON_SCALE,
            enabled: bool = True,
            greyed: bool = False,
    ) -> None:
        raw = pygame.image.load(image_path).convert_alpha()
        w, h = raw.get_size()
        self._image_normal = pygame.transform.smoothscale(
            raw, (int(w * scale), int(h * scale))
        )

        grey = self._image_normal.copy()
        grey.set_alpha(120)
        self._image_grey = grey

        self.rect = self._image_normal.get_rect(topleft=topleft)
        self.enabled = enabled
        self.greyed = greyed

    def is_clicked(self, mouse_pos: tuple[int, int]) -> bool:
        """Check if clicked.

        Args:
            mouse_pos: Mouse position.

        Returns:
            bool
        """
        return self.enabled and self.rect.collidepoint(mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw button.

        Args:
            screen: Target surface.
        """
        img = (
            self._image_grey
            if (self.greyed or not self.enabled)
            else self._image_normal
        )
        screen.blit(img, self.rect)


class HabitatScene(Scene):
    """Base habitat scene with animals, toolbar, and pet minigame."""

    BACKGROUND_FILE: str = ""

    _ICON_HEART = "heart_icon.png"
    _ICON_CHECKLIST = "checklist_icon.png"
    _ICON_MAP = "map_icon.png"

    def __init__(self, manager: SceneManager) -> None:
        """Init scene state.

        Args:
            manager: Scene manager.
        """
        super().__init__(manager)

        self._background: pygame.Surface | None = None
        self._animals: list[Animal] = []
        self._base_dir = os.path.dirname(os.path.abspath(__file__))

        self._petting = False
        self._pet_progress = 0.0
        self._pet_complete = False
        self._pet_task_active = False

        self._btn_pet: _IconButton | None = None
        self._btn_checklist: _IconButton | None = None
        self._btn_map: _IconButton | None = None

    @abstractmethod
    def create_animals(self) -> list[Animal]:
        """Create animals.

        Returns:
            list[Animal]
        """

    def on_enter(self) -> None:
        """Load background, animals, toolbar."""
        super().on_enter()

        bg_path = os.path.abspath(
            os.path.join(
                self._base_dir,
                "assets",
                "images",
                self.BACKGROUND_FILE
            )
        )
        self._background = (
            pygame.image.load(bg_path).convert()
            if os.path.exists(bg_path) else None
        )

        self._animals = self.create_animals()
        for animal in self._animals:
            animal.load(self._base_dir)

        self._petting = False
        self._pet_progress = 0.0
        self._pet_complete = False

        self._build_toolbar()

    def on_exit(self) -> None:
        """Clear scene."""
        super().on_exit()
        self._background = None
        self._animals = []

    @staticmethod
    def _icon_path(filename: str) -> str:
        return os.path.join(
            "assets",
            "images",
            filename
        )

    def _build_toolbar(self) -> None:
        """Build toolbar buttons."""
        pad = TOOLBAR_PAD
        gap = ICON_SPACING

        self._btn_pet = _IconButton(
            self._icon_path(self._ICON_HEART),
            topleft=(pad, pad),
            enabled=(
                    self._pet_task_active
                    and not self._pet_complete
            ),
            greyed=(
                    not self._pet_task_active or self._pet_complete
            ),
        )

        surf = pygame.display.get_surface()
        screen_w = surf.get_width() if surf else 1280

        self._btn_map = _IconButton(self._icon_path(self._ICON_MAP), (0, pad))
        self._btn_checklist = (
            _IconButton(
                self._icon_path(
                    self._ICON_CHECKLIST
                ),
                (0, pad)
            )
        )

        if self._btn_map and self._btn_checklist:
            map_x = screen_w - pad - self._btn_map.rect.width
            chk_x = map_x - gap - self._btn_checklist.rect.width

            self._btn_map.rect.topleft = (map_x, pad)
            self._btn_checklist.rect.topleft = (chk_x, pad)

    @abstractmethod
    def _on_pet_complete(self) -> None:
        """Handle pet completion."""

    @staticmethod
    def _animal_rect(animal: Animal) -> pygame.Rect:
        """Get approximate hitbox.

        Args:
            animal: Animal.

        Returns:
            pygame.Rect
        """
        if animal.rect_size:
            w, h = animal.rect_size
            return pygame.Rect(int(animal.x), int(animal.y), w, h)

        if animal.layers:
            w = max(lay.get_width() for lay in animal.layers)
            h = max(lay.get_height() for lay in animal.layers)
        else:
            w, h = 64, 64

        return pygame.Rect(int(animal.x), int(animal.y - h / 2), w, h)

    def _mouse_over_any_animal(self, mouse_pos: tuple[int, int]) -> bool:
        """Check hover on any animal.

        Args:
            mouse_pos: Mouse position.

        Returns:
            bool
        """
        return (
            any(
                self._animal_rect(a).collidepoint(mouse_pos)
                for a in self._animals
            )
        )

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle input.

        Args:
            events: Event list.
        """
        mouse_pos = pygame.mouse.get_pos()

        for e in events:
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self._handle_escape()

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self._handle_click(mouse_pos)

    def _handle_click(self, mouse_pos: tuple[int, int]) -> None:
        if self._btn_map and self._btn_map.is_clicked(mouse_pos):
            self._manager.pop()
            return

        if self._btn_checklist and self._btn_checklist.is_clicked(mouse_pos):
            from checklist_scene import ChecklistScene
            self._manager.push(
                ChecklistScene(
                    self._manager,
                    self._manager.context.checklist
                )
            )
            return

        if self._btn_pet and self._btn_pet.is_clicked(mouse_pos):
            if not self._petting:
                self._petting = True
                self._pet_progress = 0.0

    def _handle_escape(self) -> None:
        from pause_scene import PauseScene
        self._manager.push(PauseScene(self._manager))

    def update(self, dt: float) -> None:
        """Update animals and pet minigame.

        Args:
            dt: Delta time.
        """
        screen_width = pygame.display.get_surface().get_width()

        for animal in self._animals:
            animal.update(screen_width, dt)

        if self._petting:
            mouse_pos = pygame.mouse.get_pos()

            if self._mouse_over_any_animal(mouse_pos):
                self._pet_progress = min(
                    100.0,
                    self._pet_progress + PET_RATE
                )
            else:
                self._pet_progress = max(
                    0.0,
                    self._pet_progress - DECAY_RATE
                )

            if self._pet_progress >= 100.0:
                self._pet_progress = 0.0
                self._pet_complete = True
                self._petting = False

                if self._btn_pet:
                    self._btn_pet.enabled = False
                    self._btn_pet.greyed = True

                self._on_pet_complete()

    def draw(self, screen: pygame.Surface) -> None:
        """Render scene.

        Args:
            screen: Surface.
        """
        if self._background:
            screen.blit(
                pygame.transform.scale(self._background, screen.get_size()),
                (0, 0),
            )
        else:
            screen.fill((180, 160, 120))

        for animal in sorted(self._animals, key=lambda a: a.y):
            animal.draw(screen)

        for btn in (self._btn_pet, self._btn_checklist, self._btn_map):
            if btn:
                btn.draw(screen)

        if self._petting and self._btn_pet:
            self._draw_pet_bar(screen)

    def _draw_pet_bar(self, screen: pygame.Surface) -> None:
        """Draw progress bar.

        Args:
            screen: Surface.
        """
        if self._btn_pet:
            bar_w, bar_h = 220, 18
            bar_x = (screen.get_width() - bar_w) // 2
            bar_y = self._btn_pet.rect.bottom + 8

            pygame.draw.rect(
                screen,
                (60, 60, 60),
                (bar_x, bar_y, bar_w, bar_h),
                border_radius=4
            )

            fill_w = int(bar_w * (self._pet_progress / 100.0))
            pygame.draw.rect(
                screen,
                (240, 100, 160),
                (bar_x, bar_y, fill_w, bar_h),
                border_radius=4
            )
