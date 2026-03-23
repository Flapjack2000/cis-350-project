import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal

_SUBFOLDER = os.path.join("assets", "animals", "lion")

_LAYERS_BASE = [
    "lion_hind_back_upper.png",
    "lion_hind_back_lower.png",
    "lion_hind_back_paw.png",
    "lion_hind_front_upper.png",
    "lion_hind_front_lower.png",
    "lion_hind_front_paw.png",
    "lion_tail.png",
    "lion_body.png",
    "lion_fore_back_upper.png",
    "lion_fore_back_lower.png",
    "lion_fore_back_paw.png",
    "lion_fore_front_upper.png",
    "lion_fore_front_lower.png",
    "lion_fore_front_paw.png",
    "lion_neck.png",
]
_LAYERS_MALE   = _LAYERS_BASE + ["lion_mane.png", "lion_head.png"]
_LAYERS_FEMALE = _LAYERS_BASE + ["lion_head.png"]


class LionHabitat(HabitatScene):
    BACKGROUND_FILE = "savanna_background.png"

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        return [
            Animal(x=200, y=300, layer_files=_LAYERS_MALE,   subfolder=_SUBFOLDER,
                   scale=0.45, default_facing_left=True, direction=1,  speed=1.0),
            Animal(x=600, y=0,   layer_files=_LAYERS_FEMALE, subfolder=_SUBFOLDER,
                   scale=0.45, default_facing_left=True, direction=-1, speed=1.4),
        ]