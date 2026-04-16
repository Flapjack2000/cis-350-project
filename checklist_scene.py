import pygame
from global_settings import Settings
from checklist import Checklist
from scene import Scene, SceneManager
from button import Button


class ChecklistScene(Scene):
    PADDING = 75
    HEADER_FONT_SIZE = 32
    TASK_FONT_SIZE = 28
    BTN_FONT_SIZE = 28
    TASK_HEIGHT = 64
    TASK_WIDTH = 550
    CHECKBOX_SIZE = 22

    def __init__(self, manager: SceneManager, checklist: Checklist) -> None:
        super().__init__(manager)

        self.__checklist = checklist
        self.__settings = Settings()

        bw, bh = 220, 64
        screen_w = self.__settings.window["size"][0]
        bx = screen_w - self.PADDING - bw
        by = self.PADDING
        self.buttons = {
            "return": Button(
                bx, by,
                text="Return to Game",
                width=bw,
                height=bh,
                font_size=self.BTN_FONT_SIZE,
                color=(255, 220, 190),
                hover_color=(255, 200, 165),
                border_color=(180, 100, 60),
                hover_border_color=(140, 70, 30),
                text_color=(80, 40, 20),
                enabled=True,
            )
        }

    def update(self, dt: float) -> None:
        """Does nothing because the checklist view doesn't need to update."""
        pass

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle keyboard and mouse input events.

        Args:
            events (list[pygame.event.Event]):
                A list of pygame events to process.
        """
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                from pause_scene import PauseScene
                self._manager.push(PauseScene(self._manager))

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for name, button in self.buttons.items():
                    if button.is_clicked(mouse_pos, (True,)):
                        self._handle_action(name)

    def _handle_action(self, action: str) -> None:
        """Handle button actions.

        Args:
            action (str): The button action identifier.
        """
        if action == "return":
            self._manager.pop()

    def draw(self, screen: pygame.Surface) -> None:
        """Render the checklist view scene.

        Args:
            screen (pygame.Surface): The surface to draw the scene on.
        """

        # Bg color
        screen.fill((242, 153, 115))

        screen_w = self.__settings.window["size"][0]
        pad = self.PADDING
        cb = self.CHECKBOX_SIZE

        # Create fonts
        font_header = pygame.font.SysFont(
            "Times New Roman",
            self.HEADER_FONT_SIZE
        )
        font_task = pygame.font.SysFont(
            "Times New Roman",
            self.TASK_FONT_SIZE
        )

        # Center the task panel horizontally
        panel_x = (screen_w - self.TASK_WIDTH) // 2

        # Header
        phase = "Daytime" if self.__checklist.is_day else "Nighttime"
        header_surf = font_header.render(
            f"Day {self.__checklist.day_count} : {phase} Tasks",
            True,
            (80, 40, 20)
        )
        header_padding = 10
        header_rect = (
            pygame.Rect(
                panel_x,
                pad,
                self.TASK_WIDTH,
                header_surf.get_height() +
                header_padding * 2
            )
        )
        pygame.draw.rect(
            screen,
            (255, 220, 185),
            header_rect,
            border_radius=6
        )
        pygame.draw.rect(
            screen,
            (180, 100, 60),
            header_rect,
            width=2,
            border_radius=6
        )

        # Underline header text
        uline_y = header_rect.bottom - 8
        uline_margin = 120
        pygame.draw.line(
            surface=screen,
            color=(80, 40, 20),
            start_pos=(panel_x + uline_margin, uline_y),
            end_pos=(panel_x + self.TASK_WIDTH - uline_margin, uline_y),
            width=3
        )
        header_x = panel_x + (self.TASK_WIDTH - header_surf.get_width()) // 2
        screen.blit(header_surf, (header_x, pad + header_padding))

        # Retrieve tasks from checklist
        completed = self.__checklist.get_completed_tasks()
        incomplete = self.__checklist.get_incomplete_tasks()
        ordered_tasks = (
                [(t, True) for t in completed] +
                [(t, False) for t in incomplete]
        )

        y = header_rect.bottom + 12

        for task_name, done in ordered_tasks:
            # Create rect for task display
            task_rect = pygame.Rect(
                panel_x,
                y,
                self.TASK_WIDTH,
                self.TASK_HEIGHT
            )

            # Task border and background
            pygame.draw.rect(
                screen,
                (255, 235, 210),
                task_rect,
                border_radius=6
            )
            pygame.draw.rect(
                screen,
                (180, 100, 60),
                task_rect,
                width=2,
                border_radius=6
            )

            # Checkbox
            cb_x = panel_x + 10
            cb_rect = pygame.Rect(
                cb_x,
                y +
                (self.TASK_HEIGHT - cb) // 2,
                cb,
                cb
            )
            pygame.draw.rect(
                screen,
                (242, 153, 115),
                cb_rect,
                border_radius=4
            )
            pygame.draw.rect(
                screen,
                (180, 100, 60),
                cb_rect,
                width=2,
                border_radius=4
            )

            # Checkmark (two lines forming a tick)
            if done:
                cx, cy = cb_rect.centerx, cb_rect.centery
                pygame.draw.line(
                    screen,
                    (80, 160, 80),
                    (cx - 6, cy),
                    (cx - 1, cy + 5),
                    3
                )
                pygame.draw.line(
                    screen,
                    (80, 160, 80),
                    (cx - 1, cy + 5),
                    (cx + 7, cy - 5),
                    3
                )

            # Task label
            color = (110, 70, 40) if done else (60, 25, 10)
            label_surf = font_task.render(task_name, True, color)
            lx = cb_x + cb + 10
            ly = y + (self.TASK_HEIGHT - label_surf.get_height()) // 2
            screen.blit(label_surf, (lx, ly))

            # Strikethrough label of completed tasks
            if done:
                strike_y = ly + label_surf.get_height() // 2
                pygame.draw.line(
                    screen,
                    (110, 70, 40),
                    (lx, strike_y),
                    (lx + label_surf.get_width(),
                     strike_y),
                    2
                )

            # Add gap between tasks
            y += self.TASK_HEIGHT + 6

        # Draw buttons
        for button in self.buttons.values():
            button.draw(screen)
