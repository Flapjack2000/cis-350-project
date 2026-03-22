from root.assets.animals.animal import Animal

class Tiger(Animal):
    HABITAT_NAME = "Jungle"

    def __init__(self, x, y):
        layer_files = [
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

        super().__init__(x, y, scale=0.4, layer_files=layer_files, subfolder = "tiger")
        self.default_facing_left = False

        # Preserve original behavior tweaks
        self.speed = 1

    @staticmethod
    def create_default_group():
        tiger1 = Tiger(200, 300)
        tiger2 = Tiger(600, 0)
        tiger2.direction = -1
        tiger2.speed = 1.4
        return [tiger1, tiger2]