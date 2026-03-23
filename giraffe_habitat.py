import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal

_SUBFOLDER = os.path.join("assets", "animals", "giraffe")
_LAYER_FILES = [
    "giraffe_neck.png",
    "giraffe_hind_back_upper.png",
    "giraffe_hind_back_lower.png",
    "giraffe_hind_front_upper.png",
    "giraffe_hind_front_lower.png",
    "giraffe_tail.png",
    "giraffe_body.png",
    "giraffe_fore_back_upper.png",
    "giraffe_fore_back_lower.png",
    "giraffe_fore_front_upper.png",
    "giraffe_fore_front_lower.png",
    "giraffe_head.png",
]


class GiraffeHabitat(HabitatScene):
    BACKGROUND_FILE = "savanna_background.png"

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        return [
            Animal(x=200, y=300, layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                   scale=0.5, default_facing_left=True, direction=1,  speed=0.8),
            Animal(x=600, y=0,   layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                   scale=0.5, default_facing_left=True, direction=-1, speed=1.4),
        ]