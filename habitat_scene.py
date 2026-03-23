import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from abc import abstractmethod
from scene import Scene, SceneManager
from animal import Animal

class HabitatScene(Scene):
    BACKGROUND_FILE: str = ""

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)
        self._background: pygame.Surface | None = None
        self._animals: list[Animal] = []
        self._base_dir: str = os.path.dirname(os.path.abspath(__file__))

    @abstractmethod
    def create_animals(self) -> list[Animal]:
        pass

    def on_enter(self) -> None:
        super().on_enter()
        bg_path = os.path.abspath(
            os.path.join(self._base_dir, "assets", "images", self.BACKGROUND_FILE)
        )
        self._background = pygame.image.load(bg_path).convert() if os.path.exists(bg_path) else None
        self._animals = self.create_animals()
        for animal in self._animals:
            animal.load(self._base_dir)

    def on_exit(self) -> None:
        super().on_exit()
        self._background = None
        self._animals = []

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.handle_escape()

    def handle_escape(self) -> None:
        from pause_scene import PauseScene # Import here to avoid circular import when loading module
        self._manager.push(PauseScene(self._manager))

    def update(self, dt: float) -> None:
        screen_width = pygame.display.get_surface().get_width()
        for animal in self._animals:
            animal.update(screen_width, dt)

    def draw(self, screen: pygame.Surface) -> None:
        if self._background:
            screen.blit(pygame.transform.scale(self._background, screen.get_size()), (0, 0))
        else:
            screen.fill((180, 160, 120))

        for animal in sorted(self._animals, key=lambda a: a.y):
            animal.draw(screen)

        if self.cursor:
            screen.blit(self.cursor, pygame.mouse.get_pos())