import pygame
import os
import sys
import random

pygame.init()

WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fish Test")

BLUE = (30, 100, 180)
clock = pygame.time.Clock()

# Each entry: (filename, faces_right, size_px)
# size_px is proportional to each species' real-world max size.
# Reference: sailfin tang & yellow perch (~38 cm) = 240px, clownfish (~8 cm) = 50px
FISH_INFO = [
    ("moorishidol.png", False, 180),
    ("sailfintang.png", False, 240),
    ("clownfish.png", True, 100),
    ("discus.png", False, 125),
    ("yellowtang.png", True, 125),
    ("yellowperch.png", False, 180),
    ("africanjewelfish.png", False, 220),
]

class Fish:
    def __init__(self, img_path, faces_right, size_px, x, y, speed):
        raw = pygame.image.load(img_path).convert_alpha()
        w, h = raw.get_size()
        scale = size_px / h
        self.base_img = pygame.transform.smoothscale(raw, (int(w * scale), size_px))
        self.faces_right = faces_right

        self.x = float(x)
        self.y = float(y)
        self.home_y = float(y)
        self.speed = speed
        self.moving_right = random.choice([True, False])

    @property
    def width(self):
        return self.base_img.get_width()

    def _respawn(self):
        self.moving_right = random.choice([True, False])
        self.x = -self.width if self.moving_right else float(WIDTH)
        self.y = self.home_y

    def update(self):
        if self.moving_right:
            self.x += self.speed
            if self.x >= WIDTH:
                self._respawn()
        else:
            self.x -= self.speed
            if self.x + self.width <= 0:
                self._respawn()

    def draw(self, surface):
        should_flip = (self.moving_right != self.faces_right)
        img = pygame.transform.flip(self.base_img, should_flip, False)
        surface.blit(img, (int(self.x), int(self.y)))


def load_fish():
    fish_list = []
    script_dir = os.path.dirname(os.path.abspath(__file__))

    margin_x = 60
    x_gap = (WIDTH - margin_x * 2) // 4

    speeds =      [0.60, 0.80, 0.50, 0.70, 0.90, 0.65, 0.75]
    y_positions = [30,   310,  140,  400,  60,   250,  185]

    for i, (fname, faces_right, size_px) in enumerate(FISH_INFO):
        path = os.path.join(script_dir, fname)
        if not os.path.exists(path):
            print(f"WARNING: {path} not found, skipping.")
            continue
        x = margin_x + (i % 4) * x_gap
        y = y_positions[i]
        fish_list.append(Fish(path, faces_right, size_px, x, y, speeds[i]))

    return fish_list


def main():
    fish_list = load_fish()
    if not fish_list:
        print("No fish images found! Make sure the .png files are in the same folder as this script.")
        pygame.quit()
        sys.exit()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        screen.fill(BLUE)

        for fish in fish_list:
            fish.update()
            fish.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()