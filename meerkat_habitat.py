import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal

_SUBFOLDER = os.path.join("assets", "animals", "meerkat")

_LAYERS_V1 = ["1_meerkat_body.png", "1_meerkat_head.png"]
_LAYERS_V2 = ["2_meerkat_body.png", "2_meerkat_head.png"]
_LAYERS_V3 = [
    "3_meerkat_hind_back.png",
    "3_meerkat_hind_front.png",
    "3_meerkat_tail.png",
    "3_meerkat_body.png",
    "3_meerkat_fore_hind.png",
    "3_meerkat_fore_front.png",
    "3_meerkat_head.png",
]


class MeerkatHabitat(HabitatScene):
    BACKGROUND_FILE = "savanna_background.png"

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        return [
            Animal(x=200, y=300, layer_files=_LAYERS_V1, subfolder=_SUBFOLDER, scale=0.65, speed=0),
            Animal(x=500, y=200, layer_files=_LAYERS_V2, subfolder=_SUBFOLDER, scale=0.65, speed=0),
            Animal(x=700, y=100, layer_files=_LAYERS_V3, subfolder=_SUBFOLDER, scale=0.75, direction=1,  speed=2),
            Animal(x=850, y=400, layer_files=_LAYERS_V3, subfolder=_SUBFOLDER, scale=0.75, direction=-1, speed=2),
        ]