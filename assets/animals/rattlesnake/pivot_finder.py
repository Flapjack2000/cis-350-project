import pygame

# Initialize Pygame
pygame.init()

# Screen setup
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Simple Pivot Finder - Stacked")
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Load all 4 images
body = pygame.image.load("rattlesnake_body.png").convert_alpha()
head = pygame.image.load("rattlesnake_head.png").convert_alpha()
tail = pygame.image.load("rattlesnake_tail.png").convert_alpha()
tongue = pygame.image.load("rattlesnake_tongue.png").convert_alpha()

# Image position (center of screen)
image_x = SCREEN_WIDTH // 2
image_y = SCREEN_HEIGHT // 2

# Point position (start at center of the 1024x1024 image)
point_x = 512
point_y = 512


def main():
    global point_x, point_y

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Arrow keys move the point
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            point_x -= 1
        if keys[pygame.K_RIGHT]:
            point_x += 1
        if keys[pygame.K_UP]:
            point_y -= 1
        if keys[pygame.K_DOWN]:
            point_y += 1

        # Draw
        screen.fill(WHITE)

        # Draw all 4 images stacked (in drawing order)
        for img in [body, head, tongue, tail]:
            rect = img.get_rect()
            rect.center = (image_x, image_y)
            screen.blit(img, rect)

        # Calculate where the point is on screen
        # (point_x, point_y) are coordinates on the 1024x1024 image
        screen_point_x = image_x + (point_x - 512)
        screen_point_y = image_y + (point_y - 512)

        # Draw the point (big and visible)
        pygame.draw.circle(screen, RED, (screen_point_x, screen_point_y), 10)

        # Draw coordinates
        font = pygame.font.Font(None, 56)
        text = font.render(f"Point X: {point_x}  Y: {point_y}", True, RED)
        screen.blit(text, (10, 10))

        # Draw offset from center (this is what you'll use for rotation pivot)
        offset_x = point_x - 512
        offset_y = point_y - 512
        font2 = pygame.font.Font(None, 48)
        text2 = font2.render(f"Offset from center: ({offset_x:+d}, {offset_y:+d})", True, BLACK)
        screen.blit(text2, (10, 70))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()