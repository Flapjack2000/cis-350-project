from root.assets.animals.animal import Animal

class Rattlesnake(Animal):
    HABITAT_NAME = "Grassland"

    def __init__(self, x, y):
        layer_files = [
            "rattlesnake_body.png",
            "rattlesnake_head.png",
            "rattlesnake_tongue.png",
            "rattlesnake_tail.png",
        ]

        super().__init__(
            x,
            y,
            scale=1,
            layer_files=layer_files,
            subfolder="rattlesnake"
        )

        self.default_facing_left = False
        self.speed = 0

    @staticmethod
    def create_default_group():
        s1 = Rattlesnake(300, 300)

        return [s1]