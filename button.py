"""
Reusable Button widget for pygame scenes.

Typical usage
-------------
    btn = Button(x, y, "Click me")

    # in update:
    btn.update(pygame.mouse.get_pos())

    # in draw:
    btn.draw(screen)

    # in handle_events:
    if btn.is_clicked(mouse_pos, pygame.mouse.get_pressed()):
        ...

Customisation
-------------
Pass keyword arguments to the constructor to override any visual property:

    Button(x, y, "Start",
        width=240, height=70,
        font_size=42,
        color=(200, 230, 255),
        hover_color=(160, 200, 255),
        border_color=(100, 150, 200),
        text_color=(20, 40, 80),
        border_width=3,
        border_radius=16,
        disabled_color=(180, 180, 180),
        disabled_text_color=(120, 120, 120),
    )

You can also mutate any attribute after construction:
    btn.text = "Resume"
    btn.color = (255, 200, 200)
"""
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame


class Button:
    """Button for use across the game"""
    DEFAULT_WIDTH = 200
    DEFAULT_HEIGHT = 60
    DEFAULT_FONT_SIZE = 36
    DEFAULT_COLOR = (255, 192, 203)  # idle background
    DEFAULT_HOVER_COLOR = (255, 160, 180)  # background while hovered
    DEFAULT_BORDER_COLOR = (200, 150, 150)  # outline
    DEFAULT_TEXT_COLOR = (80, 60, 60)  # label text
    DEFAULT_BORDER_WIDTH = 3
    DEFAULT_BORDER_RADIUS = 10
    DEFAULT_DISABLED_COLOR = (200, 200, 200)
    DEFAULT_DISABLED_TEXT_COLOR = (140, 140, 140)
    DEFAULT_DISABLED_BORDER_COLOR = (173, 173, 173)
    DEFAULT_HOVER_BORDER_COLOR = (180, 120, 140)

    def __init__(
            self,
            x: int,
            y: int,
            text: str,
            *,
            width: int = DEFAULT_WIDTH,
            height: int = DEFAULT_HEIGHT,
            font_size: int = DEFAULT_FONT_SIZE,
            font: pygame.font.Font | None = None,
            color: tuple = DEFAULT_COLOR,
            hover_color: tuple = DEFAULT_HOVER_COLOR,
            border_color: tuple = DEFAULT_BORDER_COLOR,
            text_color: tuple = DEFAULT_TEXT_COLOR,
            border_width: int = DEFAULT_BORDER_WIDTH,
            border_radius: int = DEFAULT_BORDER_RADIUS,
            disabled_color: tuple = DEFAULT_DISABLED_COLOR,
            disabled_text_color: tuple = DEFAULT_DISABLED_TEXT_COLOR,
            hover_border_color: tuple = DEFAULT_HOVER_BORDER_COLOR,
            disabled_border_color: tuple = DEFAULT_DISABLED_BORDER_COLOR,
            enabled: bool = True,
    ) -> None:
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font or pygame.font.Font(None, font_size)

        # visual properties
        self.color = color
        self.hover_color = hover_color
        self.border_color = border_color
        self.text_color = text_color
        self.border_width = border_width
        self.border_radius = border_radius
        self.disabled_color = disabled_color
        self.disabled_text_color = disabled_text_color
        self.hover_border_color = hover_border_color
        self.disabled_border_color = disabled_border_color

        # state
        self.enabled = enabled
        self.hovered = False

    def update(self, mouse_pos: tuple[int, int]) -> None:
        """Track hover state. Call once per frame before draw()."""
        self.hovered = self.enabled and self.rect.collidepoint(mouse_pos)

    def draw(self, screen: pygame.Surface) -> None:
        """Render the button to *screen*."""
        if not self.enabled:
            bg = self.disabled_color
            fg = self.disabled_text_color
            bd = self.disabled_border_color
        elif self.hovered:
            bg = self.hover_color
            fg = self.text_color
            bd = self.hover_border_color
        else:
            bg = self.color
            fg = self.text_color
            bd = self.border_color

        pygame.draw.rect(screen, bg, self.rect, border_radius=self.border_radius)
        if self.border_width > 0:
            pygame.draw.rect(
                screen, bd, self.rect,
                self.border_width, border_radius=self.border_radius,
            )

        label = self.font.render(self.text, True, fg)
        screen.blit(label, label.get_rect(center=self.rect.center))

    def is_clicked(
            self,
            mouse_pos: tuple[int, int],
            mouse_pressed: tuple[bool, ...],
            button: int = 0,
    ) -> bool:
        """Return True when the left mouse button (or *button* index) is pressed over this button."""
        return (
                self.enabled
                and self.rect.collidepoint(mouse_pos)
                and mouse_pressed[button]
        )

    def move_to(self, x: int, y: int) -> "Button":
        """Reposition the button and return self for chaining."""
        self.rect.topleft = (x, y)
        return self

    def resize(self, width: int, height: int) -> "Button":
        """Resize the button, keeping its top-left position."""
        self.rect.size = (width, height)
        return self