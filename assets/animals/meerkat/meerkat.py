from root.assets.animals.animal import Animal

class Meerkat(Animal):
    HABITAT_NAME = "Grassland"

    def __init__(self, x, y, variant=1):
        self.variant = variant

        if variant == 1:
            layer_files = [
                "1_meerkat_body.png",
                "1_meerkat_head.png",
            ]
            scale = .65

        elif variant == 2:
            layer_files = [
                "2_meerkat_body.png",
                "2_meerkat_head.png",
            ]
            scale = .65

        elif variant == 3:
            layer_files = [
                "3_meerkat_hind_back.png",
                "3_meerkat_hind_front.png",
                "3_meerkat_tail.png",
                "3_meerkat_body.png",
                "3_meerkat_fore_hind.png",
                "3_meerkat_fore_front.png",
                "3_meerkat_head.png",
            ]
            scale = .75

        else:
            raise ValueError("Invalid meerkat variant (must be 1, 2, or 3)")

        super().__init__(x, y, scale=scale, layer_files=layer_files, subfolder = "meerkat")
        self.default_facing_left = False
        self.speed = 0.6

    @staticmethod
    def create_default_group():

        m3a = Meerkat(700, 100, variant=3)
        m3a.direction = 1
        m3a.speed = 2

        m2 = Meerkat(500, 200, variant=2)
        m2.speed = 0

        m1 = Meerkat(200, 300, variant=1)
        m1.speed = 0

        m3b = Meerkat(850, 400, variant=3)
        m3b.direction = -1
        m3b.speed = 2

        return [m1, m2, m3a, m3b]