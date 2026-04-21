import os
import pygame
import random
import math
from button import Button
from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal

_SUBFOLDER = os.path.join("assets", "animals", "zebra")
_LAYER_FILES = [
    "zebra_hind_back_upper.png",
    "zebra_hind_back_lower.png",
    "zebra_hind_front_upper.png",
    "zebra_hind_front_lower.png",
    "zebra_tail.png",
    "zebra_body.png",
    "zebra_fore_back_upper.png",
    "zebra_fore_back_lower.png",
    "zebra_fore_front_upper.png",
    "zebra_fore_front_lower.png",
    "zebra_neck.png",
    "zebra_head.png",
]

import math
from animal_movement import AnimalMovement

movement = AnimalMovement()

def zebra_walk(animal, dt):
    """
    Animates zebra walking motion using sinusoidal leg rotation.

    Args:
        animal (Animal): The zebra instance containing animation state and layer angles.
    """
    t = animal.time
    swing = math.sin(t * 5) * 5

    HBU, HBL = 0, 1
    HFU, HFL = 2, 3
    TAIL = 4
    BODY = 5
    FBU, FBL = 6, 7
    FFU, FFL = 8, 9
    NECK = 10
    HEAD = 11

    animal.layer_angles[HBU] = swing
    animal.layer_angles[HBL] = swing * 0.8

    animal.layer_angles[HFU] = -swing
    animal.layer_angles[HFL] = -swing * 0.8

    animal.layer_angles[FBU] = -swing
    animal.layer_angles[FBL] = -swing * 0.8

    animal.layer_angles[FFU] = swing
    animal.layer_angles[FFL] = swing * 0.8


def zebra_draw(animal, screen):
    """
    Renders a zebra using layered sprite animation with pivot-based rotation.

    Args:
        animal (Animal): The zebra instance containing sprite layers and animation state.
        screen (pygame.Surface): The surface to render the zebra onto.
    """
    should_flip = animal.facing_left != animal.default_facing_left
    body_width = animal.layers[5].get_width() if animal.layers else 0
    body_pos = pygame.Vector2(animal.x + body_width / 2, animal.y)

    for i, (layer, angle) in enumerate(zip(animal.layers, animal.layer_angles)):

        rotated_img, rotated_rect = pygame.transform.rotozoom(
            layer,
            angle,
            1.0
        ), layer.get_rect()

        pivot = pygame.Vector2(
            layer.get_width() // 2,
            layer.get_height() // 2
        )

        rotated_img, rotated_rect = movement.rotate_image(
            layer,
            angle,
            pivot
        )

        rotated_rect.center = body_pos

        if should_flip:
            rotated_img = pygame.transform.flip(rotated_img, True, False)

        screen.blit(rotated_img, rotated_rect)

class ZebraHabitat(HabitatScene):
    """Habitat scene representing a zebra interacting with a water trough.

    Extends HabitatScene to include a water-trough mini-game where the zebra
    walks back and forth, drinks water when the trough is filled,
    and the player can increment the water level by clicking on the trough.
    """
    BACKGROUND_FILE_DAY = "savanna_background_day.png"
    BACKGROUND_FILE_NIGHT = "savanna_background_night.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize the ZebraHabitat scene and its gameplay elements.

        Args:
            manager (SceneManager): The object controlling scene transitions.
        """
        self.BACKGROUND_FILE = self.BACKGROUND_FILE_DAY if manager.context.is_day else self.BACKGROUND_FILE_NIGHT
        super().__init__(manager)

        self.__zebra_speed: float = 2.5

        # Check if playing minigame or just visiting
        self.is_game_active = "zebra" in self._manager.context.checklist.get_incomplete_tasks()
        if self.is_game_active:
            self.game_init()

    def game_init(self):
        # Habitat-specific gameplay setup variables
        self.__s1: int = 250  # wall height & base width
        self.__s2: int = 20  # wall thickness & base thickness

        self.__trough_color: tuple[int, int, int] = (123, 63, 0)
        self.__water_color: tuple[int, int, int] = (0, 94, 209)

        self.__water_level: int = 25
        self.__max_water_level: int = 100
        self.__increment_amount: int = 2
        self.__decrement_amount: int = 55

        self.__passes_until_drink: int = 1  # how many trough passes before drinking (zebra drinks on first pass, random later)
        self.__pass_counted: bool = False  # prevents counting the same pass twice
        self.__drink_duration: float = 1.5  # seconds to pause at trough
        self.__drink_timer: float = 0.0  # counts down while zebra is drinking

        bx, by, bw, bh = 800, 30, 400, 60
        self.buttons = {
            "finish": Button(
                bx, by, text="Finish & Return to Map", width=bw, height=bh, enabled=False,
                color=(147, 235, 147), border_color=(87, 196, 87)
            )
        }

        # Instruction text
        self._font = pygame.font.SysFont(None, 32)
        self._instruction_text = self._font.render(
            "Click the trough to fill it with water!", True, (0, 0, 0)
        )

        # Sanity check the water level
        if self.__water_level > self.__max_water_level or self.__water_level < 0:
            raise ValueError("Water level cannot exceed maximum and cannot be less than zero.")

    def create_animals(self) -> list[Animal]:
        """Create and return the zebra Animal instance for this habitat.

        Returns:
            list[Animal]: A single zebra configured with sprite layers, starting position, and speed.
        """
        if self.is_game_active:
            return [
                Animal(x=120, y=300, layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                       scale=0.45, default_facing_left=True, direction=1, speed=self.__zebra_speed,
                       animate_fn=zebra_walk, draw_fn=zebra_draw, has_droppings=True,)
            ]
        else:
            return [
                Animal(x=120, y=300, layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                       scale=0.45, default_facing_left=True, direction=1, speed=self.__zebra_speed,
                       animate_fn=zebra_walk, draw_fn=zebra_draw),
                Animal(x=520, y=500, layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                       scale=0.40, default_facing_left=True, direction=-1, speed=self.__zebra_speed * 1.1,
                       animate_fn=zebra_walk, draw_fn=zebra_draw)
            ]

    def draw_instruction(self, screen: pygame.Surface) -> None:
        """Render instruction text next to the water trough.

        Args:
            screen (pygame.Surface): The surface to draw the instruction text on.
        """
        trough_rect = self.get_trough_rect(screen)

        text_x = trough_rect.right + 20  # 20px padding to the right
        text_y = trough_rect.top + 20  # slight vertical offset

        screen.blit(self._instruction_text, (text_x, text_y))

    def draw_water_trough(self, screen: pygame.Surface):
        """Render the water trough, including walls, base, and current water level.

        Args:
            screen (pygame.Surface): The surface to draw the trough on.
        """
        # Create trough & water surfaces
        water_height = int(
            (self.__s1 - self.__s2) *
            (self.__water_level / self.__max_water_level)
        )
        trough_parts = [
            pygame.Surface((self.__s1 - self.__s2 * 2, water_height)),  # water
            pygame.Surface((self.__s1, self.__s2)),  # base
            pygame.Surface((self.__s2, self.__s1)),  # left wall
            pygame.Surface((self.__s2, self.__s1)),  # right wall
        ]

        # Apply colors
        for part in trough_parts:
            part.fill(self.__trough_color)
        trough_parts[0].fill(self.__water_color)

        # Calculate positions
        cx = (screen.get_width() // 2) - (self.__s1 // 2)  # horizontal center of trough
        cy = (screen.get_height() // 2) - (self.__s1 // 2) + 220  # vertical center of trough
        part_positions = [
            (cx + self.__s2, cy + self.__s1 - self.__s2 - water_height),  # water
            (cx, cy + self.__s1 - self.__s2),  # base
            (cx, cy),  # left wall
            (cx + self.__s1 - self.__s2, cy),  # right wall
        ]

        # Render to screen
        for i in range(len(trough_parts)):
            screen.blit(trough_parts[i], part_positions[i])

    def draw(self, screen: pygame.Surface) -> None:
        """Render the entire habitat, including background,
        zebra, trough, instructions, and buttons.

        Args:
            screen (pygame.Surface): The surface to render the scene on.
        """
        # Parent handles zebra and background automatically
        super().draw(screen)

        if self.is_game_active:
            # Render the trough
            self.draw_water_trough(screen)

            # Draw instruction text
            self.draw_instruction(screen)

            # Render the button(s)
            for button in self.buttons.values():
                button.draw(screen)

    def decrement_water(self) -> None:
        """Lower the water level in the trough if appropriate"""

        # Check if already empty
        if self.__water_level <= 0:
            return

        # Check if lowering the water would go negative and stop at empty
        if self.__water_level - self.__decrement_amount <= 0:
            self.__water_level = 0
            return

        # Lower the water level
        self.__water_level -= self.__decrement_amount

    def increment_water(self) -> None:
        """Raise the water level in the trough if appropriate"""

        # Check if already at max
        if self.__water_level >= self.__max_water_level:
            return

        # Check if raising the water would overflow and stop at the max
        if self.__water_level + self.__increment_amount >= self.__max_water_level:
            self.__water_level = self.__max_water_level
            return

        # Raise the water level
        self.__water_level += self.__increment_amount

    def get_trough_rect(self, screen: pygame.Surface) -> pygame.Rect:
        """Return the bounding rectangle of the trough for mouse hit-testing.

        Args:
            screen (pygame.Surface): The current screen surface for positioning calculations.

        Returns:
            pygame.Rect: The rectangle representing the trough's position and size.
        """
        cx = (screen.get_width() // 2) - (self.__s1 // 2)
        cy = (screen.get_height() // 2) - (self.__s1 // 2) + 220
        return pygame.Rect(cx, cy, self.__s1, self.__s1)

    def handle_events(self, events: list[pygame.event.Event]) -> None:
        """Handle mouse and keyboard events, including clicks on the trough or finish button.

        Args:
            events (list[pygame.event.Event]): The list of pygame events to process.
        """
        super().handle_events(events)

        screen = pygame.display.get_surface()
        trough_rect = self.get_trough_rect(screen)

        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if trough_rect.collidepoint(event.pos):
                    self.increment_water()
                elif self.buttons["finish"].is_clicked(mouse_pos, (True,)):
                    self.handle_finish()

    def update(self, dt: float) -> None:
        """Update the habitat scene, including zebra movement, trough interaction, and win conditions.

        Args:
            dt (float): Delta time since the last frame, in seconds.
        """
        if not self.is_game_active:
            super().update(dt)
            return

        # Check win condition and allow the player to use the finish button if done
        if self.__water_level >= self.__max_water_level:
            self.buttons["finish"].enabled = True

        zebra = self._animals[0] if self._animals else None

        # While the zebra is drinking, keep him frozen and count down
        if self.__drink_timer > 0:
            self.__drink_timer -= dt
            if self.__drink_timer <= 0:
                self.__drink_timer = 0.0

                # Resume walking by restoring the speed he had before stopping
                if zebra:
                    zebra.speed = self.__zebra_speed

            # Skip super().update() so the zebra doesn't move
            return

        # Continue walking
        super().update(dt)

        if zebra is None:
            return

        # Check when zebra is standing over the trough
        screen = pygame.display.get_surface()
        trough_rect = self.get_trough_rect(screen)
        zebra_center = zebra.x + (zebra.layers[0].get_width() // 2 if zebra.layers else 0)
        over_trough = trough_rect.left <= zebra_center <= trough_rect.right

        if over_trough:
            if not self.__pass_counted:
                self.__pass_counted = True
                self.__passes_until_drink -= 1

                if self.__passes_until_drink <= 0:
                    if self.__water_level > 0:
                        zebra.speed = 0.0
                        self.decrement_water()
                        self.__drink_timer = self.__drink_duration
                        self.__passes_until_drink = random.randint(1, 3)
        else:
            # Reset so the next crossing counts as a new pass
            self.__pass_counted = False

    def handle_finish(self):
        """Handle returning to the map by popping this scene from the SceneManager."""
        self._manager.context.checklist.complete_task("zebra")
        self._manager.pop()
