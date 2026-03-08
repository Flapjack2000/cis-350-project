"""
Entry point for the game.
"""
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

from game import Game

if __name__ == "__main__":
    game = Game()
    game.run()