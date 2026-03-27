class Settings:
    """Various global settings and hard coded values across the game."""

    def __init__(self) -> None:
        """Initialize settings values."""

        self.window: dict = {
            "title": "Zoo Game",
            "size": (1280, 720)
        }

        self.time: dict = {
            "fps": 120
        }

        self.cursor: dict = {
            "image_path": "assets/images/cat_cursor.png",
            "size": (64, 64),
        }

        self.backgrounds = {
        "Jungle": "jungle_background.png",
        "Savanna": "savanna_background.png",
        "Grassland": "grassland_background.png",
        "Aquarium": "aquarium_background.png",
    }