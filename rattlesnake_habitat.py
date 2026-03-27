import os
import math
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from scene import SceneManager
from habitat_scene import HabitatScene
from animal import Animal

_SUBFOLDER = os.path.join("assets", "animals", "rattlesnake")
_LAYER_FILES = [
    "rattlesnake_body.png",
    "rattlesnake_head.png",
    "rattlesnake_tongue.png",
    "rattlesnake_tail.png",
]

# Layer indices for readability
_BODY    = 0
_HEAD    = 1
_TONGUE  = 2
_TAIL    = 3

# Animation tuning
_HEAD_BOB_SPEED    = 2.0   # rad/s
_HEAD_BOB_AMOUNT   = 3.0   # degrees
_RATTLE_SPEED      = 30.0  # rad/s
_TAIL_RATTLE_AMOUNT = 15.0 # degrees
_STILL_TIME        = 2.0   # seconds still before rattling
_RATTLE_TIME       = 1.0   # seconds of rattling


def _rattlesnake_animate(animal: Animal, dt: float) -> None:
    """Manipulate the parts of the rattlesnake puppet to animate it.

    Applies a continuous head bob to the head and tongue layers, and a rapid
    tail rattle that activates periodically based on the animal's elapsed time.

    Args:
        animal (Animal): The rattlesnake Animal instance whose layer_angles are updated.
        dt (float): Time delta since the last frame in seconds (unused; animation uses animal.time).
    """
    t = animal.time
    cycle = t % (_STILL_TIME + _RATTLE_TIME)
    is_rattling = cycle >= _STILL_TIME

    animal.layer_angles[_HEAD] = math.sin(t * _HEAD_BOB_SPEED) * _HEAD_BOB_AMOUNT
    animal.layer_angles[_TONGUE] = animal.layer_angles[_HEAD]
    animal.layer_angles[_TAIL] = math.sin(t * _RATTLE_SPEED) * _TAIL_RATTLE_AMOUNT if is_rattling else 0.0


class RattlesnakeHabitat(HabitatScene):
    """Habitat scene representing rattlesnakes in a grassland environment.

    Handles creating rattlesnake animals with layered sprites and optional
    animation (head bobbing and tail rattling) within the scene.
    """
    BACKGROUND_FILE = "grassland_background.png"

    def __init__(self, manager: SceneManager) -> None:
        """Initialize the RattlesnakeHabitat scene.

        Args:
            manager (SceneManager): The scene manager controlling scene transitions.
        """
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        """Create and return a list of rattlesnake Animal instances for this habitat.

       Returns:
           list[Animal]: The rattlesnake animals in the scene, each with its sprite layers, position, and optional animation function.
       """
        return [
            Animal(x=300, y=300, layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                   scale=1.0, default_facing_left=False, speed=0,
                   # animate_fn=_rattlesnake_animate),
                   animate_fn=None),
        ]