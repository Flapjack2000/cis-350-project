"""
Main menu system
* Start Game button
* Settings button
* Quit button
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame

from global_settings import Settings


class Button():
    def __init__(self, x, y, width, height, text, font_size=36):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = pygame.font.Font(None, font_size)
        self.color = (255, 192, 203)  # Pink
        self.hover_color = (255, 160, 180)  # Darker pink
        self.text_color = (80, 60, 60)  # Dark text
        self.hovered = False
        
    def draw(self, screen):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, (200, 150, 150), self.rect, 3, border_radius=10)  # Border
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
        
    def is_clicked(self, mouse_pos, mouse_pressed):
        return self.rect.collidepoint(mouse_pos) and mouse_pressed[0]


class Menu():
    def __init__(self):
        pygame.init()
        self.settings = Settings()

        size = self.settings.window["size"]
        self.screen = pygame.display.set_mode(size)

        title = self.settings.window["title"]
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        
        # Load custom cursor
        cursor_surface = pygame.image.load('root\\assets\\images\\cat_cursor.png').convert_alpha()
        scaled_cursor_surface = pygame.transform.scale(cursor_surface, (64, 64))
        pygame.mouse.set_visible(False)
        self.cursor = scaled_cursor_surface
        
        # Menu state
        self.running = True
        self.menu_action = None
        
        # Create buttons
        screen_width, screen_height = size
        button_width = 200
        button_height = 60
        button_x = (screen_width - button_width) // 2
        start_y = screen_height // 2 - 100
        
        self.buttons = {
            'start': Button(button_x, start_y, button_width, button_height, "Start Game"),
            'settings': Button(button_x, start_y + 80, button_width, button_height, "Settings"),
            'quit': Button(button_x, start_y + 160, button_width, button_height, "Quit")
        }
        
        # Title font
        self.title_font = pygame.font.Font(None, 72)
        
    def run(self):
        while self.running:
            FPS = self.settings.time["FPS"]
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
            
        return self.menu_action
        
    def handle_events(self):
        mouse_pressed = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                self.menu_action = 'quit'
                
        # Check button clicks
        for button_name, button in self.buttons.items():
            if button.is_clicked(mouse_pos, mouse_pressed):
                self.running = False
                self.menu_action = button_name
                
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        for button in self.buttons.values():
            button.update(mouse_pos)
            
    def draw(self):
        # Background
        self.screen.fill([255, 230, 230])
        
        # Title
        title_text = self.title_font.render("Zoo Game", True, (150, 100, 100))
        title_rect = title_text.get_rect(center=(self.screen.get_width() // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Buttons
        for button in self.buttons.values():
            button.draw(self.screen)
            
        # Custom cursor
        mouse_pos = pygame.mouse.get_pos()
        self.screen.blit(self.cursor, mouse_pos)
        
        pygame.display.flip()


if __name__ == "__main__":
    RED = '\033[91m'
    ENDC = '\033[0m'
    print(f"{RED}---------------------------{ENDC}")
    print(f"{RED}Run the main.py file, bozo!{ENDC}")  
    print(f"{RED}---------------------------{ENDC}")