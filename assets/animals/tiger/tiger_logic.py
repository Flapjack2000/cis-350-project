import pygame
import math

# Initialize Pygame
pygame.init()

# Screen setup
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Tiger Rig Test")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)


class BodyPart:
    """Represents a single body part (image) that can rotate"""

    def __init__(self, image_path, pivot_x, pivot_y):
        """
        Args:
            image_path: Path to the PNG file
            pivot_x: X position of the pivot point (where this part rotates from)
            pivot_y: Y position of the pivot point
        """
        self.original_image = pygame.image.load(image_path).convert_alpha()
        self.image = self.original_image
        self.pivot_x = pivot_x  # Pivot point relative to the part's position
        self.pivot_y = pivot_y
        self.angle = 0  # Current rotation angle in degrees
        self.position = [0, 0]  # World position [x, y]

    def rotate(self, angle):
        """Rotate the part by the given angle"""
        self.angle = angle
        self.image = pygame.transform.rotate(self.original_image, angle)

    def draw(self, surface):
        """Draw the part on the screen"""
        # Get the rect of the rotated image
        rect = self.image.get_rect()
        # Position it so the pivot point is at self.position
        rect.center = (self.position[0], self.position[1])
        surface.blit(self.image, rect)

        # Draw a red dot at the pivot point for debugging
        pygame.draw.circle(surface, RED, (int(self.position[0]), int(self.position[1])), 5)


class TigerRig:
    """The complete tiger character rig"""

    def __init__(self):
        # TODO: Update these paths to match your actual file structure
        base_path = "./"

        # Load all body parts
        # TODO: Adjust pivot points - these are just placeholders!
        # The pivot point should be where the part connects to its parent

        self.body = BodyPart(base_path + "tiger_body.png", 512, 512)
        self.head = BodyPart(base_path + "tiger_head.png", 512, 512)
        self.neck = BodyPart(base_path + "tiger_neck.png", 512, 512)
        self.tail = BodyPart(base_path + "tiger_tail.png", 512, 512)

        # Back legs (hind)
        self.hind_back_upper = BodyPart(base_path + "tiger_hind_back_thigh.png", 512, 512)
        self.hind_back_lower = BodyPart(base_path + "tiger_hind_back_lower.png", 512, 512)
        self.hind_back_paw = BodyPart(base_path + "tiger_hind_back_paw.png", 512, 512)

        # Front legs (hind front)
        self.hind_front_upper = BodyPart(base_path + "tiger_hind_front_upper.png", 512, 512)
        self.hind_front_lower = BodyPart(base_path + "tiger_hind_front_lower.png", 512, 512)
        self.hind_front_paw = BodyPart(base_path + "tiger_hind_front_paw.png", 512, 512)

        # Front legs (fore back)
        self.fore_back_upper = BodyPart(base_path + "tiger_fore_back_upper.png", 512, 512)
        self.fore_back_lower = BodyPart(base_path + "tiger_fore_back_lower.png", 512, 512)
        self.fore_back_paw = BodyPart(base_path + "tiger_fore_back_paw.png", 512, 512)

        # Front legs (fore front)
        self.fore_front_upper = BodyPart(base_path + "tiger_fore_front_upper.png", 512, 512)
        self.fore_front_lower = BodyPart(base_path + "tiger_fore_front_lower.png", 512, 512)
        self.fore_front_paw = BodyPart(base_path + "tiger_fore_front_paw.png", 512, 512)

        # Set the body as the root position (center of screen)
        self.root_x = SCREEN_WIDTH // 2
        self.root_y = SCREEN_HEIGHT // 2

    def update_positions(self):
        """
        Update all body part positions based on the hierarchy.
        This is where the magic happens - child parts follow parent parts!
        """
        # Body is the root
        self.body.position = [self.root_x, self.root_y]

        # TEMPORARY FIX: Put all parts at the same position as body
        # This will stack them all together so you can see the full tiger
        # Later, you'll calculate proper offsets for each part

        self.head.position = [self.root_x, self.root_y]
        self.neck.position = [self.root_x, self.root_y]
        self.tail.position = [self.root_x, self.root_y]

        # Back legs
        self.hind_back_upper.position = [self.root_x, self.root_y]
        self.hind_back_lower.position = [self.root_x, self.root_y]
        self.hind_back_paw.position = [self.root_x, self.root_y]

        self.hind_front_upper.position = [self.root_x, self.root_y]
        self.hind_front_lower.position = [self.root_x, self.root_y]
        self.hind_front_paw.position = [self.root_x, self.root_y]

        # Front legs
        self.fore_back_upper.position = [self.root_x, self.root_y]
        self.fore_back_lower.position = [self.root_x, self.root_y]
        self.fore_back_paw.position = [self.root_x, self.root_y]

        self.fore_front_upper.position = [self.root_x, self.root_y]
        self.fore_front_lower.position = [self.root_x, self.root_y]
        self.fore_front_paw.position = [self.root_x, self.root_y]

    def calculate_child_position(self, parent, offset_x, offset_y):
        """
        Calculate where a child part should be positioned based on its parent.

        Args:
            parent: The parent BodyPart
            offset_x: X offset from parent's pivot to child's pivot (before rotation)
            offset_y: Y offset from parent's pivot to child's pivot (before rotation)

        Returns:
            [x, y] position for the child
        """
        # Convert parent's angle to radians
        angle_rad = math.radians(parent.angle)

        # Rotate the offset by the parent's angle
        rotated_x = offset_x * math.cos(angle_rad) - offset_y * math.sin(angle_rad)
        rotated_y = offset_x * math.sin(angle_rad) + offset_y * math.cos(angle_rad)

        # Add to parent's position
        child_x = parent.position[0] + rotated_x
        child_y = parent.position[1] + rotated_y

        return [child_x, child_y]

    def draw(self, surface):
        """Draw all parts in the correct order (back to front)"""

        # Back layer (behind body)
        self.hind_back_upper.draw(surface)
        self.hind_back_lower.draw(surface)
        self.hind_back_paw.draw(surface)

        self.hind_front_upper.draw(surface)
        self.hind_front_lower.draw(surface)
        self.hind_front_paw.draw(surface)

        self.tail.draw(surface)

        # Middle layer
        self.body.draw(surface)

        # Front layer (in front of body)
        self.fore_back_upper.draw(surface)
        self.fore_back_lower.draw(surface)
        self.fore_back_paw.draw(surface)

        self.fore_front_upper.draw(surface)
        self.fore_front_lower.draw(surface)
        self.fore_front_paw.draw(surface)

        self.neck.draw(surface)
        self.head.draw(surface)


# Main game loop
def main():
    running = True
    tiger = TigerRig()

    # Test variables - you can adjust these with keyboard later
    test_angle = 0

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle keyboard input for testing rotations
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            test_angle += 1
        if keys[pygame.K_RIGHT]:
            test_angle -= 1

        # TODO: Apply test_angle to a specific body part for testing
        # Example: tiger.hind_back_upper.rotate(test_angle)
        tiger.head.rotate(test_angle)

        # Update positions based on current rotations
        tiger.update_positions()

        # Draw everything
        screen.fill(WHITE)
        tiger.draw(screen)

        # Draw instructions
        font = pygame.font.Font(None, 36)
        text = font.render(f"Test Angle: {test_angle}", True, BLACK)
        screen.blit(text, (10, 10))

        pygame.display.flip()
        clock.tick(60)  # 60 FPS

    pygame.quit()


if __name__ == "__main__":
    main()