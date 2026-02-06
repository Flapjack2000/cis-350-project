"""
Manages the game loop and gameplay
* Clock
* Day/Night cycle
* Movement
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

from global_settings import Settings

class Game():
  def __init__(self) -> None:
    # Create window and apply settings
    self.running = True
    pygame.init()

    self.settings = Settings()
    size = self.settings.window["size"]
    self.screen = pygame.display.set_mode(size)

    title = self.settings.window["title"]
    pygame.display.set_caption(title)

    self.clock = pygame.time.Clock()
    
    cursor_surface = pygame.image.load('root\\assets\\images\\cat_cursor.png').convert_alpha()
    scaled_cursor_surface = pygame.transform.scale(cursor_surface, (64, 64))
    pygame.mouse.set_visible(False)
    self.cursor = scaled_cursor_surface
  
  def delta_time(self):
      """ Calculate time since last frame """
      return self.clock.tick(self.settings.time["FPS"]) / 1000
      
  def run(self):
        while self.running:
            FPS = self.settings.time["FPS"]
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            
  def handle_events(self):
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              self.running = False
              
  def update(self):
      pass
      
  def draw(self):
      self.screen.fill([255, 230, 230])
      # Draw the custom cursor
      mouse_pos = pygame.mouse.get_pos()
      self.screen.blit(self.cursor, mouse_pos)
      pygame.display.flip()
      
if __name__ == "__main__":
 
  RED = '\033[91m'
  ENDC = '\033[0m'
  print(f"{RED}---------------------------{ENDC}")
  print(f"{RED}Run the main.py file, bozo!{ENDC}")  
  print(f"{RED}---------------------------{ENDC}")
