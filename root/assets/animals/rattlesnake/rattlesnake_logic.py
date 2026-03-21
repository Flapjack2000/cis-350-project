import pygame
import math
import time

pygame.init()
screen = pygame.display.set_mode((1200, 800))
clock = pygame.time.Clock()


# ============ SIMPLE BODY PART CLASS ============
class BodyPart:
    def __init__(self, image_path):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.angle = 0
        self.position = [0, 0]

    def draw(self, surface):
        # Rotate the image
        rotated = pygame.transform.rotate(self.image, self.angle)
        rect = rotated.get_rect(center=self.position)
        surface.blit(rotated, rect)


# ============ LOAD IMAGES ============
body = BodyPart("./rattlesnake_body.png")
head = BodyPart("./rattlesnake_head.png")
tail = BodyPart("./rattlesnake_tail.png")
tongue = BodyPart("./rattlesnake_tongue.png")

# ============ ANIMATION SETTINGS ============
# ** TWEAK THESE VALUES **
HEAD_BOB_SPEED = 2  # How fast the head bobs
HEAD_BOB_AMOUNT = 3  # How many degrees the head rotates

RATTLE_SPEED = 30  # How fast the rattle oscillates
TAIL_RATTLE_AMOUNT = 15  # How many degrees the tail shakes
TONGUE_RATTLE_AMOUNT = 15  # How many degrees the tongue shakes

STILL_TIME = 2.0  # Seconds of stillness before rattle
RATTLE_TIME = 1.0  # Seconds of rattling

# ============ MAIN LOOP ============
start_time = time.time()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # -------- TIMING --------
    t = time.time() - start_time
    cycle_time = t % (STILL_TIME + RATTLE_TIME)  # Repeat every 3 seconds
    is_rattling = cycle_time >= STILL_TIME

    # -------- HEAD ANIMATION (always bobbing) --------
    head_angle = math.sin(t * HEAD_BOB_SPEED) * HEAD_BOB_AMOUNT

    # -------- TAIL ANIMATION --------
    if is_rattling:
        tail_angle = math.sin(t * RATTLE_SPEED) * TAIL_RATTLE_AMOUNT
    else:
        tail_angle = 0

    # -------- TONGUE ANIMATION --------
    '''if is_rattling:
        # Tongue = head rotation + its own rattle
        tongue_angle = head_angle + math.sin(t * RATTLE_SPEED) * TONGUE_RATTLE_AMOUNT
    else:
        # Tongue follows head exactly
        tongue_angle = head_angle'''

    # -------- SET ANGLES --------
    body.angle = 0
    head.angle = head_angle
    tail.angle = tail_angle
    #tongue.angle = tongue_angle

    # -------- SET POSITIONS (all stacked at center for now) --------
    center_x = 600
    center_y = 400

    body.position = [center_x, center_y]
    head.position = [center_x, center_y]
    tail.position = [center_x, center_y]
    tongue.position = [center_x, center_y]

    # ** TO FIX PIVOT POINTS: You'll need to adjust these positions **
    # ** based on where each part should rotate from **

    # -------- DRAW --------
    screen.fill((255, 255, 255))
    body.draw(screen)
    head.draw(screen)
    tongue.draw(screen)
    tail.draw(screen)

    # -------- DEBUG INFO --------
    font = pygame.font.Font(None, 36)
    text = font.render(f"Rattling: {is_rattling}  Head: {head_angle:.1f}  Tail: {tail_angle:.1f}", True, (0, 0, 0))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
