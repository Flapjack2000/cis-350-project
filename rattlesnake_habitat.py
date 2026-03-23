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
    t = animal.time
    cycle = t % (_STILL_TIME + _RATTLE_TIME)
    is_rattling = cycle >= _STILL_TIME

    animal.layer_angles[_HEAD] = math.sin(t * _HEAD_BOB_SPEED) * _HEAD_BOB_AMOUNT
    animal.layer_angles[_TONGUE] = animal.layer_angles[_HEAD]
    animal.layer_angles[_TAIL] = math.sin(t * _RATTLE_SPEED) * _TAIL_RATTLE_AMOUNT if is_rattling else 0.0


class RattlesnakeHabitat(HabitatScene):
    BACKGROUND_FILE = "grassland_background.png"

    def __init__(self, manager: SceneManager) -> None:
        super().__init__(manager)

    def create_animals(self) -> list[Animal]:
        return [
            Animal(x=300, y=300, layer_files=_LAYER_FILES, subfolder=_SUBFOLDER,
                   scale=1.0, default_facing_left=False, speed=0,
                   animate_fn=_rattlesnake_animate),
        ]