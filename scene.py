import pygame
from abc import ABC, abstractmethod


class Scene(ABC):
    """
    Abstract base class for all game scenes.

    Subclasses must implement handle_events, update, and draw.
    Lifecycle hooks on_enter / on_exit are optional.

    The scene receives a reference to the SceneManager so it can
    trigger transitions itself.
    """

    def __init__(self, manager: "SceneManager") -> None:
        self._manager = manager

    def on_enter(self) -> None:
        """Called once when this scene becomes the active scene."""
        pass

    def on_exit(self) -> None:
        """Called once just before this scene is removed / replaced."""
        pass

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Process input events for this frame."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Advance game logic. dt is elapsed seconds since the last frame."""

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Render everything to screen."""


class SceneManager:
    """
    Manages a stack of Scene objects.

    push(scene)    - overlay a scene on top (pause menus, etc.).
    pop()          - remove the top scene and resume the one below.
    exit_all()     - empty the stack, allowing the game to end on the next loop
    """

    def __init__(self) -> None:
        """Initialize the scene stack."""
        self.__stack: list[Scene] = []

    @property
    def current(self) -> Scene | None:
        """Return the top scene in the stack."""
        return self.__stack[-1] if self.__stack else None

    @property
    def is_empty(self) -> bool:
        """Check if stack is empty."""
        return not self.__stack

    def push(self, scene: Scene) -> None:
        """Overlay scene on top of the current scene."""
        scene.on_enter()
        self.__stack.append(scene)

    def pop(self) -> None:
        """Remove the top scene and return to the one below."""
        if self.__stack:
            self.__stack.pop().on_exit()

    def exit_all(self) -> None:
        """Clear the entire stack, causing the game loop to exit cleanly."""
        while self.__stack:
            self.__stack.pop().on_exit()
