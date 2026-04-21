import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from abc import abstractmethod
from scene import Scene, SceneManager
from animal import Animal


PET_RATE   = 0.4
DECAY_RATE = 0.05
ICON_SCALE = 0.18


class HabitatScene(Scene):
    """Abstract base class for habitat scenes containing multiple animals."""
    BACKGROUND_FILE: str = ""

    def __init__(self, manager: SceneManager) -> None:
        """Initialize the habitat scene with background and animal containers.

        Args:
            manager (SceneManager): The scene manager controlling scene transitions.
        """
        super().__init__(manager)
        self._background: pygame.Surface | None = None
        self._animals: list[Animal] = []
        self._base_dir: str = os.path.dirname(os.path.abspath(__file__))

        self.petting      = False
        self.pet_progress = 0.0
        self.pet_complete = False

        raw = pygame.image.load(
            os.path.join("assets", "images", "heart_icon.png")
        ).convert_alpha()
        w, h = raw.get_size()
        self.heart_icon = pygame.transform.smoothscale(
            raw, (int(w * ICON_SCALE), int(h * ICON_SCALE))
        )
        self.heart_icon_rect = self.heart_icon.get_rect(topleft=(20, 20))

        self.waste_active = False
        self.waste_cleared = False
        self.waste_positions: list[pygame.Vector2] = []
        self.waste_clicked: list[bool] = []

        raw_waste = pygame.image.load(
            os.path.join("assets", "images", "poop.png")
        ).convert_alpha()
        w, h = raw_waste.get_size()
        self.waste_icon = pygame.transform.smoothscale(raw_waste, (int(w * 0.12), int(h * 0.12)))

    @abstractmethod
    def create_animals(self) -> list[Animal]:
        """Create and return a list of animals for this habitat.

        Returns:
            list[Animal]: The animals present in this habitat scene.
        """
        pass

    def _animal_rect(self, animal: Animal) -> pygame.Rect:
        """
        Compute a bounding box for an animal based on its sprite layers.

        Args:
            animal (Animal): Animal to compute hitbox for.

        Returns:
            pygame.Rect: Approximate screen-space hitbox.
        """
        if animal.rect_size is not None:
            w, h = animal.rect_size
            return pygame.Rect(int(animal.x), int(animal.y), w, h)
        elif animal.layers:
            w = max(l.get_width() for l in animal.layers)
            h = max(l.get_height() for l in animal.layers)
        else:
            w, h = 64, 64

        return pygame.Rect(int(animal.x), int(animal.y - h / 2), w, h)

    def _mouse_over_any_animal(self, mouse_pos: tuple) -> bool:
        """
        Check if mouse is currently over any animal.

        Args:
            mouse_pos (tuple): Current mouse position.

        Returns:
            bool: True if hovering over at least one animal.
        """
        return any(
            self._animal_rect(a).collidepoint(mouse_pos)
            for a in self._animals
        )

    def on_enter(self) -> None:
        """Called when entering the habitat scene. Loads animals and sprites."""
        super().on_enter()
        bg_path = os.path.abspath(
            os.path.join(self._base_dir, "assets", "images", self.BACKGROUND_FILE)
        )
        self._background = (
            pygame.image.load(bg_path).convert()
            if os.path.exists(bg_path) else None
        )
        self._animals = self.create_animals()
        for animal in self._animals:
            animal.load(self._base_dir)

        self.petting      = False
        self.pet_progress = 0.0
        self.pet_complete = False

        self.waste_active = any(a.has_droppings for a in self._animals)
        self.waste_cleared = False
        if self.waste_active:
            self.waste_positions = [pygame.Vector2(100, 260), pygame.Vector2(900, 650)]
            self.waste_clicked = [False, False]

    def on_exit(self) -> None:
        """Called when exiting the habitat scene. Clears background and animal lists."""
        super().on_exit()
        self._background = None
        self._animals    = []


    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle Pygame events within the habitat scene.

        Args:
            events (list[pygame.event.Event]): The list of events to process.
        """
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.handle_escape()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.heart_icon_rect.collidepoint(mouse_pos):
                    self.petting      = True
                    self.pet_progress = 0.0
                if self.waste_active and not self.waste_cleared:
                    for i, pos in enumerate(self.waste_positions):
                        if not self.waste_clicked[i]:
                            rect = self.waste_icon.get_rect(center=(int(pos.x), int(pos.y)))
                            if rect.collidepoint(mouse_pos):
                                self.waste_clicked[i] = True
                    if all(self.waste_clicked):
                        self.waste_cleared = True
                        self.waste_active = False
                        #FIXME if self._manager.context.checklist.complete_task("Clean Enclosure"):
                        from checklist_scene import ChecklistScene
                        self._manager.push(ChecklistScene(self._manager, self._manager.context.checklist))

    def handle_escape(self) -> None:
        """Handle the ESC key being pressed and pause."""
        from pause_scene import PauseScene
        self._manager.push(PauseScene(self._manager))

    def update(self, dt: float) -> None:
        """Update all animals in the habitat.

        Args:
            dt (float): Time delta since the last update in seconds.
        """
        screen_width = pygame.display.get_surface().get_width()
        for animal in self._animals:
            animal.update(screen_width, dt)

        if self.petting:
            mouse_pos = pygame.mouse.get_pos()
            if self._mouse_over_any_animal(mouse_pos):
                self.pet_progress += PET_RATE
            else:
                self.pet_progress -= DECAY_RATE

            self.pet_progress = max(0.0, min(100.0, self.pet_progress))

            if self.pet_progress >= 100.0:
                self.pet_progress = 0.0
                self.pet_complete = True
                self.petting = False
                #FIXME if self._manager.context.checklist.complete_task("Pet Animal"):
                from checklist_scene import ChecklistScene
                self._manager.push(ChecklistScene(self._manager, self._manager.context.checklist))


    def draw(self, screen: pygame.Surface) -> None:
        """Render the habitat background and all animals onto the screen.

        Args:
            screen (pygame.Surface): The Pygame surface to draw the scene on.
        """
        if self._background:
            screen.blit(
                pygame.transform.scale(self._background, screen.get_size()),
                (0, 0)
            )
        else:
            screen.fill((180, 160, 120))

        if self.waste_active and not self.waste_cleared:
            if not self.waste_clicked[0]:
                rect = self.waste_icon.get_rect(center=(int(self.waste_positions[0].x), int(self.waste_positions[0].y)))
                screen.blit(self.waste_icon, rect)

        for animal in sorted(self._animals, key=lambda a: a.y):
            animal.draw(screen)

        if self.waste_active and not self.waste_cleared:
            if not self.waste_clicked[1]:
                rect = self.waste_icon.get_rect(center=(int(self.waste_positions[1].x), int(self.waste_positions[1].y)))
                screen.blit(self.waste_icon, rect)

        screen.blit(self.heart_icon, self.heart_icon_rect)

        if self.petting:
            bar_w, bar_h = 220, 18
            bar_x = (screen.get_width() - bar_w) // 2
            bar_y = self.heart_icon_rect.bottom - 50

            pygame.draw.rect(
                screen, (60, 60, 60),
                (bar_x, bar_y, bar_w, bar_h),
                border_radius=4
            )
            fill_w = int(bar_w * (self.pet_progress / 100.0))
            pygame.draw.rect(
                screen, (240, 100, 160),
                (bar_x, bar_y, fill_w, bar_h),
                border_radius=4
            )