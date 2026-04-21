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
            color: tuple[int, int, int] = DEFAULT_COLOR,
            hover_color: tuple[int, int, int] = DEFAULT_HOVER_COLOR,
            border_color: tuple[int, int, int] = DEFAULT_BORDER_COLOR,
            text_color: tuple[int, int, int] = DEFAULT_TEXT_COLOR,
            border_width: int = DEFAULT_BORDER_WIDTH,
            border_radius: int = DEFAULT_BORDER_RADIUS,
            disabled_color: tuple[int, int, int] = DEFAULT_DISABLED_COLOR,
            disabled_text_color: tuple[int, int, int] = DEFAULT_DISABLED_TEXT_COLOR,
            hover_border_color: tuple[int, int, int] = DEFAULT_HOVER_BORDER_COLOR,
            disabled_border_color: tuple[int, int, int] = DEFAULT_DISABLED_BORDER_COLOR,
            enabled: bool = True,
    ) -> None:
        """Create a button using default and custom values.

        Args:
            x (int): The x-coordinate of the button's position.
            y (int): The y-coordinate of the button's position.
            text (string): The label displayed on the button.
            width (int): The width of the button in pixels.
            height (int): The height of the button in pixels.
            font_size (int): The font size of the button label.
            font (pygame.font.Font | None): A custom pygame Font object. If None, the default font is used.
            color (tuple[int, int, int]): The background color of the button.
            hover_color (tuple[int, int, int]): The background color when the button is hovered.
            border_color (tuple[int, int, int]): The border color of the button.
            text_color (tuple[int, int, int]): The color of the button label text.
            border_width (int): The thickness of the button border in pixels.
            border_radius (int): The radius of the button's rounded corners.
            disabled_color (tuple[int, int, int]): The background color when the button is disabled.
            disabled_text_color (tuple[int, int, int]): The text color when the button is disabled.
            hover_border_color (tuple[int, int, int]): The border color when the button is hovered.
            disabled_border_color (tuple[int, int, int]): The border color when the button is disabled.
            enabled (bool): Whether the button is interactive. Defaults to True.
        """

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
        """Track hover state. Call once per frame before draw().

        Args:
            mouse_pos (tuple[int, int]): the current mouse position
        """
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
        """Return True when the specified mouse button is pressed over this button.

        Args:
            mouse_pos: The current (x, y) position of the mouse cursor.
            mouse_pressed: A tuple of booleans representing the pressed state
                of each mouse button, as returned by pygame.mouse.get_pressed().
            button: The index of the mouse button to check. Defaults to 0 (left click).

        Returns:
            True if the button is enabled, the mouse is over it, and the
            specified mouse button is pressed. False otherwise.
        """
        return (
                self.enabled
                and self.rect.collidepoint(mouse_pos)
                and mouse_pressed[button]
        )

    def move_to(self, x: int, y: int):
        """Reposition the button.

        Args:
            x (int): the new x position of the button's top left corner
            y (int): the new y position of the button's top left corner

        """
        self.rect.topleft = (x, y)

    def resize(self, width: int, height: int):
        """Resize the button, keeping its top-left position.

        Args:
            width (int): the new width of the button
            height (int): the new height of the button
        """
        self.rect.size = (width, height)
