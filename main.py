"""
Entry point for the game
Handles menu -> game transitions
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

from menu import Menu
from game import Game

def main():
    while True:
        # Show menu
        menu = Menu()
        action = menu.run()
        
        if action == 'start':
            # Start the game
            game = Game()
            game.run()
            # When game ends, loop back to menu
            
        elif action == 'settings':
            pass
            
        elif action == 'quit':
            break
            
    pygame.quit()

if __name__ == "__main__":
    main()