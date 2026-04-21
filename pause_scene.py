"""
Pause scene to be overlaid on other scenes via SceneManager.push().
Press Escape or click Resume to return to the game.
"""
import os

os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame
from scene import Scene, SceneManager
from global_settings import Settings
from button import Button
from menu_scene import MenuScene


class PauseScene(Scene):
    """The pause menu.

    Extends Scene for scene switching logic.
    Actions for resuming and returning to the main menu.
    """

    def __init__(self, manager: SceneManager) -> None:
        """Create the screen and buttons of the pause menu.

        Args:
            manager (SceneManager): The scene manager controlling scene transitions.
        """

        super().__init__(manager)

        screen_width, screen_height = Settings().window["size"]
        bw, bh = 200, 60
        bx = (screen_width - bw) // 2
        start_y = screen_height // 2 - 60

        self.buttons = {
            "resume": Button(bx, start_y, "Resume", width=bw, height=bh),
            "quit": Button(bx, start_y + 80, "Quit to Menu", width=bw, height=bh),
        }
        self.title_font = pygame.font.Font(None, 72)
        self.overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self.overlay.fill((10, 0, 0, 120))

    def on_enter(self) -> None:
        """Set hovered state of buttons to false."""
        for button in self.buttons.values():
            button.hovered = False

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle button presses and keyboard shortcuts in the pause menu.

        Args:
            events (list[pygame.event.Event]): A list of pygame events to process.
        """
        mouse_pos = pygame.mouse.get_pos()

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._manager.pop()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, button in self.buttons.items():
                    if button.is_clicked(mouse_pos, (True,)):
                        self._handle_action(name)

    def update(self, dt: float) -> None:
        """Update button hover states based on the current mouse position.

        Args:
            dt (float): Time delta since the last frame (unused but required by Scene interface).
        """
        for button in self.buttons.values():
            button.update(pygame.mouse.get_pos())

    def draw(self, screen: pygame.Surface) -> None:
        """Render the pause overlay, title, and buttons onto the screen.

        Args:
            screen (pygame.Surface): The surface to draw the pause menu on.
        """
        screen.blit(self.overlay, (0, 0))

        title = self.title_font.render("Paused", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 140)))

        for button in self.buttons.values():
            button.draw(screen)

    def _handle_action(self, action: str) -> None:
        """Handle button press actions.

        Args:
            action (str): The name of the action to enact.
        """
        if action == "resume":
            self._manager.pop()
        elif action == "quit":
            self._manager.exit_all()
            self._manager.push(MenuScene(self._manager))
