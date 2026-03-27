import os
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
    """Habitat scene representing giraffes in a savanna environment."""
    BACKGROUND_FILE = "savanna_background.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize the GiraffeHabitat scene.

        Args:
            manager (SceneManager): The scene manager controlling scene transitions.
        """
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        """Create and return a list of giraffe Animal instances for this habitat.

        Returns:
            list[Animal]: The giraffe animals in the scene, each with its sprite layers, position, and movement parameters.
        """
        return [
            Animal(x=200, y=300, layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                   scale=0.5, default_facing_left=True, direction=1,  speed=0.8),
            Animal(x=600, y=0,   layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                   scale=0.5, default_facing_left=True, direction=-1, speed=1.4),
        ]