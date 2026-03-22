from root.assets.animals.animal import Animal

class Lion(Animal):
    HABITAT_NAME = "Savanna"

    def __init__(self, x, y, has_mane=True):
        layer_files = [
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

        if has_mane:
            layer_files.append("lion_mane.png")

        layer_files.append("lion_head.png")

        super().__init__(x, y, scale=0.45, layer_files=layer_files, subfolder = "lion")
        self.default_facing_left = True

    @staticmethod
    def create_default_group():
        g1 = Lion(200, 300, has_mane = True)
        g2 = Lion(600, 0, has_mane = False)
        g2.direction = -1
        g2.speed = 1.4

        return [g1, g2]