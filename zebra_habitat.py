import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

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


class ZebraHabitat(HabitatScene):
    BACKGROUND_FILE = "savanna_background.png"

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        return [
            Animal(x=200, y=300, layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                   scale=0.45, default_facing_left=True, direction=1,  speed=1.0),
            Animal(x=600, y=0,   layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                   scale=0.45, default_facing_left=True, direction=-1, speed=1.4),
        ]