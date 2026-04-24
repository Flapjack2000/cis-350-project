import pygame
from abc import ABC, abstractmethod
from checklist import Checklist


class GameContext:
    """Exposes things that need to be modifiable everywhere."""

    def __init__(
            self,
            checklist: Checklist,
            cursor: pygame.Surface,
            music_player=None,
    ) -> None:
        self.checklist = checklist
        self.music_player = music_player
        self.cursor = cursor

    @property
    def is_day(self):
        """Return whether it's currently daytime."""
        return self.checklist.is_day


class Scene(ABC):
    """
    Abstract base class for all game scenes.

    Subclasses must implement handle_events, update, and draw.
    Lifecycle hooks on_enter / on_exit are optional.

    The scene receives a reference to the SceneManager so it can
    trigger transitions itself.
    """

    def __init__(self, manager: "SceneManager") -> None:
        """Store a reference to the scene manager for use in transitions.

        Args:
            manager (SceneManager):
                The scene manager controlling scene transitions.
        """
        self._manager = manager

    def on_enter(self) -> None:
        """Called once when this scene becomes the active scene."""
        pass

    def on_exit(self) -> None:
        """Called once just before this scene is removed / replaced."""
        pass

    @abstractmethod
    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Process input events for this frame.

        Args:
            events (list[pygame.event.Event]): The events for this frame.
        """

    @abstractmethod
    def update(self, dt: float) -> None:
        """Advance game logic.

        Args:
            dt (float): Delta time, the time since the last frame.
        """

    @abstractmethod
    def draw(self, screen: pygame.Surface) -> None:
        """Render everything to screen.

        Args:
            screen (pygame.Surface): The main screen to draw on.
        """


class SceneManager:
    """Manage a stack of Scene objects."""

    def __init__(self, context: GameContext) -> None:
        """Initialize the scene stack."""
        self.__stack: list[Scene] = []
        self.context = context

    @property
    def current(self) -> Scene | None:
        """Return the top scene in the stack."""
        return self.__stack[-1] if self.__stack else None

    @property
    def is_empty(self) -> bool:
        """Check if stack is empty.

        Returns:
            bool: True if there are no scenes on the stack, False otherwise.
        """
        return not self.__stack

    def push(self, scene: Scene) -> None:
        """Overlay scene on top of the current scene.

        Args:
            scene (Scene): the scene to run next
        """
        scene.on_enter()
        self.__stack.append(scene)
        self.context.music_player.update_scene(scene)

    def pop(self) -> None:
        """Remove the top scene and return to the one below."""
        if self.__stack:
            self.__stack.pop().on_exit()

        if self.__stack:
            self.context.music_player.update_scene(self.__stack[-1])

    def exit_all(self) -> None:
        """Clear the entire stack, causing the game loop to exit cleanly."""
        while self.__stack:
            self.__stack.pop().on_exit()

    def __len__(self) -> int:
        """Return the number of scenes in the stack."""
        return len(self.__stack)
