"""
Various global settings and hard coded values across the game
"""

class Settings:
  def __init__(self)-> None:
    
    self.window: dict = {
      "title": "Zoo Game",
      "size": (1280, 720),
      "width": 1280,
      "height": 720,
    }

    self.time: dict = {
      "FPS": 120
    }