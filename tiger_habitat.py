import os
from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal

_SUBFOLDER = os.path.join("assets", "animals", "tiger")
_LAYER_FILES = [
    "tiger_hind_back_lower.png",
    "tiger_hind_back_upper.png",
    "tiger_hind_back_paw.png",
    "tiger_hind_front_lower.png",
    "tiger_hind_front_upper.png",
    "tiger_hind_front_paw.png",
    "tiger_tail.png",
    "tiger_body.png",
    "tiger_fore_back_lower.png",
    "tiger_fore_back_upper.png",
    "tiger_fore_back_paw.png",
    "tiger_fore_front_lower.png",
    "tiger_fore_front_upper.png",
    "tiger_fore_front_paw.png",
    "tiger_neck.png",
    "tiger_head.png",
]


class TigerHabitat(HabitatScene):
    """Habitat scene representing tigers in a jungle environment.

    Handles creating tiger animals with layered sprites,
    movement, and rendering within the scene.
    """
    BACKGROUND_FILE = "jungle_background.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize the TigerHabitat scene.

        Args:
            manager (SceneManager): The object controlling scene transitions.
        """
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        """Return a list of tiger Animal instances for this habitat.

       Returns:
           list[Animal]: The tiger animals in the scene,
           each with its sprite layers, position, and movement settings.
       """
        return [
            Animal(x=200, y=300,
                   layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                   scale=0.4, default_facing_left=False,
                   direction=1, speed=1.0),
            Animal(x=600, y=0,
                   layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                   scale=0.4, default_facing_left=False,
                   direction=-1, speed=1.4),
        ]
