from root.assets.animals.animal import Animal

class Zebra(Animal):
    HABITAT_NAME = "Savanna"

    def __init__(self, x, y):
        layer_files = [
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

        super().__init__(x, y, scale=0.45, layer_files=layer_files, subfolder = "zebra")
        self.default_facing_left = True

    @staticmethod
    def create_default_group():
        g1 = Zebra(200, 300)
        g2 = Zebra(600, 0)
        g2.direction = -1
        g2.speed = 1.4
        return [g1, g2]