from root.assets.animals.animal import Animal

class Giraffe(Animal):
    HABITAT_NAME = "Savanna"

    def __init__(self, x, y):
        layer_files = [
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

        super().__init__(x, y, scale=0.5, layer_files=layer_files, subfolder = "giraffe")
        self.default_facing_left = True
        self.speed = 0.8

    @staticmethod
    def create_default_group():
        g2 = Giraffe(600, 0)
        g1 = Giraffe(200, 300)
        g2.direction = -1
        g2.speed = 1.4
        return [g1, g2]