import pygame
from global_settings import Settings
from checklist import Checklist
from scene import Scene, SceneManager
from button import Button


class ChecklistScene(Scene):
    """Displays the list of tasks on the checklist
    and whether they've been completed.
    """

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

    @staticmethod
    def _format_task_text(internal_name: str) -> str:
        """Parse task names into text for the checklist.

        Args:
            internal_name (str): Task name

        Returns:
            str: Task name
        """
        task_map = {
            "zebra_pet": "Pet the Zebras",
            "zebra_poop": "Clean Up the Zebra Habitat",
            "zebra_feed": "Feed the Zebras",
            "zebra_water": "Refill the Water in the Zebra Habitat",

            "giraffe_pet": "Pet the Giraffes",
            "giraffe_poop": "Clean Up the Giraffe Habitat",
            "giraffe_feed": "Feed the Giraffes",
            "giraffe_water": "Refill the Water in the Giraffe Habitat",

            "tiger_pet": "Pet the Tigers",
            "tiger_poop": "Clean Up the Tiger Habitat",
            "tiger_feed": "Feed the Tigers",
            "tiger_water": "Refill the Water in the Tiger Habitat",

            "lion_pet": "Pet the Lions",
            "lion_poop": "Clean Up the Lion Habitat",
            "lion_feed": "Feed the Lions",
            "lion_water": "Refill the Water in the Lion Habitat",

            "meerkat_pet": "Pet the Meerkats",
            "meerkat_poop": "Clean Up the Meerkat Habitat",
            "meerkat_feed": "Feed the Meerkats",
            "meerkat_water": "Refill the Water in the Meerkat Habitat",

            "red_panda_pet": "Pet the Red Panda",
            "red_panda_poop": "Clean Up the Red Panda Habitat",

            "penguin_pet": "Pet the Penguins",
            "penguin_feed": "Feed the Penguins",
            "penguin_water": "Refill the Water in the Penguin Habitat",

            "rattlesnake_pet": "Pet the Rattlesnake",

            "octopus_pet": "Pet the Octopus",

            "fish_feed": "Feed the Fish",
        }

        return task_map.get(internal_name,
                            internal_name.replace("_", " ").title())

    def update(self, dt: float) -> None:
        """Do nothing. This scene doesn't change after initialization.

        Args:
            dt (float): the time since the last frame
        """
        pass

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle mouse events and pausing.

        Args:
            events (list[pygame.event.Event]): the events to handle
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
        """Handle return button click.

        Args:
            action (str): the action to take
        """
        if action == "return":
            self._manager.pop()

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the scene.

        Args:
            screen (pygame.Surface): the screen to draw on
        """
        screen.fill(
            (242, 153, 115)
            if self.__checklist.is_day
            else (37, 46, 90)
        )

        screen_w = self.__settings.window["size"][0]
        pad = self.PADDING
        cb = self.CHECKBOX_SIZE

        font_header = (
            pygame.font.SysFont("Times New Roman", self.HEADER_FONT_SIZE)
        )
        font_task = (
            pygame.font.SysFont("Times New Roman", self.TASK_FONT_SIZE)
        )

        panel_x = (screen_w - self.TASK_WIDTH) // 2

        phase = "Daytime" if self.__checklist.is_day else "Nighttime"
        header_surf = font_header.render(
            f"Day {self.__checklist.day_count} : {phase} Tasks",
            True,
            (80, 40, 20)
        )

        header_padding = 10
        header_rect = pygame.Rect(
            panel_x,
            pad,
            self.TASK_WIDTH,
            header_surf.get_height() + header_padding * 2
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

        uline_y = header_rect.bottom - 8
        uline_margin = 120
        pygame.draw.line(
            screen, (80, 40, 20),
            (panel_x + uline_margin, uline_y),
            (panel_x + self.TASK_WIDTH - uline_margin, uline_y),
            3
        )
        header_x = panel_x + (self.TASK_WIDTH - header_surf.get_width()) // 2
        screen.blit(header_surf, (header_x, pad + header_padding))

        completed = self.__checklist.get_completed_tasks()
        incomplete = self.__checklist.get_incomplete_tasks()
        ordered_tasks = ([(t, True) for t in completed] +
                         [(t, False) for t in incomplete])

        y = header_rect.bottom + 12

        for task_name, done in ordered_tasks:
            task_rect = pygame.Rect(
                panel_x,
                y,
                self.TASK_WIDTH,
                self.TASK_HEIGHT
            )

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

            cb_x = panel_x + 10
            cb_rect = pygame.Rect(
                cb_x,
                y + (self.TASK_HEIGHT - cb) // 2,
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

            # Use the new formatter here
            display_text = self._format_task_text(task_name)
            color = (110, 70, 40) if done else (60, 25, 10)
            label_surf = font_task.render(display_text, True, color)

            lx = cb_x + cb + 10
            ly = y + (self.TASK_HEIGHT - label_surf.get_height()) // 2
            screen.blit(label_surf, (lx, ly))

            if done:
                strike_y = ly + label_surf.get_height() // 2
                pygame.draw.line(
                    screen, (110, 70, 40),
                    (lx, strike_y), (lx + label_surf.get_width(), strike_y), 2
                )

            y += self.TASK_HEIGHT + 6

        for button in self.buttons.values():
            button.draw(screen)
