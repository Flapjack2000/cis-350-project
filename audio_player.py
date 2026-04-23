import pygame
import random

class AudioPlayer:
    def __init__(self):
        pygame.mixer.init()

        self.menu_music = "assets/music/MainMenu.ogg"
        self.game_music = "assets/music/Lofi.ogg"

        self.sounds = {
            "FishHabitat": ["Water1.ogg", "Water2.ogg", "Water3.ogg", "Water4.ogg"],
            "LionHabitat": ["LionRoar1.ogg", "LionRoar2.ogg", "LionRoar3.ogg"],
            "MeerkatHabitat": ["Meerkat1.ogg", "Meerkat2.ogg", "Meerkat3.ogg", "Meerkat4.ogg"],
            "RattlesnakeHabitat": ["SnakeHiss1.ogg", "SnakeHiss2.ogg", "SnakeRattle.ogg"],
            "TigerHabitat": ["TigerGrowl1.ogg", "TigerGrowl2.ogg"],
            "ZebraHabitat": ["ZebraAnnoyed.ogg", "ZebraAnxious.ogg", "ZebraCasual.ogg"],
            "RedPandaHabitat": ["Panda1.ogg", "Panda2.ogg"],
            "PenguinHabitat": ["Penguin1.ogg"]
        }

        self.current_music = None
        self.current_scene = None

        self.timer = 0
        self.delay = random.uniform(5, 10)


    def update_scene(self, scene) -> None:
        """Receive the name of a scene and determine if a sound should be played."""
        name = scene.__class__.__name__

        if name == self.current_scene:
            return

        self.current_scene = name

        if name == "MenuScene":
            self.check_music(self.menu_music)
        else:
            self.check_music(self.game_music)

    def check_music(self, path):
        """Check if the path music selected is already playing. Make it currently playing if not."""
        if self.current_music == path:
            return

        pygame.mixer.music.stop()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play(-1)

        self.current_music = path

    def update_sounds(self, ms):
        """Constantly updates each frame, until randomly generating a set sound for a given habitat."""
        sounds = self.sounds.get(self.current_scene)

        if sounds is None:
            return

        self.timer += ms

        if self.timer > self.delay:
            path = f"assets/sounds/{sounds[random.randint(0, len(sounds) - 1)]}"
            pygame.mixer.Sound(path).play()

            self.timer = 0
            self.delay = random.uniform(5, 10)