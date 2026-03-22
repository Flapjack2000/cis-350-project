import pygame
import os

from root.assets.animals.tiger.tiger import Tiger
from root.assets.animals.giraffe.giraffe import Giraffe
from root.assets.animals.zebra.zebra import Zebra
from root.assets.animals.lion.lion import Lion
from root.assets.animals.meerkat.meerkat import Meerkat
from root.assets.animals.rattlesnake.rattlesnake import Rattlesnake


class Enclosure:
    def __init__(self, animal_type):
        self.animal_type = animal_type
        self.habitat_name = animal_type.HABITAT_NAME

        self.animals = animal_type.create_default_group()

        self.background_image = self.load_background_image()

    def load_background_image(self):
        path = self.animal_type.get_background_path()

        if path and os.path.exists(path):
            return pygame.image.load(path).convert()

        return None

    def update(self, screen_width):
        for animal in self.animals:
            animal.update(screen_width)

    def draw(self, screen):
        if self.background_image:
            bg = pygame.transform.scale(self.background_image, screen.get_size())
            screen.blit(bg, (0, 0))

        for animal in sorted(self.animals, key=lambda a: a.y):
            animal.draw(screen)


#THIS IS REALLY BAD PRACTICE, BUT FOR TESTING PURPOSES I MADE A NEW MAIN TO SEE THE ENCLOSURES
#FEEL FREE TO ADD WHATEVER TO THE OFFICIAL SCENE SWITCH
def main():
    pygame.init()

    WIDTH, HEIGHT = 1200, 800
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Enclosure Test")

    clock = pygame.time.Clock()

    #THIS IS THE LINE THAT SELECTS WHICH ENCLOSURE YOU ARE ON
    #FOR TESTING I SWAP IT OUT BETWEEN ANIMALS
    #ON THE MAP, WE WILL NEED TO CALL THE ANIMAL BASED ON PLAYER CLICK
    enclosure = Enclosure(Tiger)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        enclosure.update(WIDTH)
        enclosure.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()