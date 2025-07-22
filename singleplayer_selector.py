
import pygame
import random
import os
from spritesheet import SpriteSheet
from game_config import *
from sprite_animation import SpriteAnimation

class SinglePlayerSelector:
    def __init__(self, asset_manager, center):
        self.asset_manager = asset_manager
        self.center = center
        self.options = SINGLEPLAYER_OPTIONS
        self.selecting = False
        self.selected_option = None
        self.current_highlighted = 0
        self.start_time = 0
        self.last_highlight_change = 0
        self.selection_complete = False
        
        # Load background spritesheet
        self.load_background_spritesheet()
        
        # Position for each option on the spritesheet (6 positions)
        self.option_positions = [
            (0, 0),      # Adventure Mode
            (360, 0),    # Time Attack  
            (720, 0),    # Survival Mode
            (0, 360),    # Puzzle Challenge
            (360, 360),  # Boss Rush
            (720, 360)   # Training Mode
        ]
        
        # Size of each selection area
        self.selection_size = (1280, 720)
        
    def load_background_spritesheet(self):
        """Load the stage selection background spritesheet"""
        try:
            sprite_path = os.path.join(
                self.asset_manager.script_dir, 
                'imagenes', 
                'singleplayer', 
                'singleplayer-bg-720p.png'
            )
            #self.background_spritesheet = pygame.image.load(sprite_path)
            self.spritesheet = SpriteSheet(sprite_path)
            self.bg_animation = SpriteAnimation ( self.spritesheet, self.spritesheet.get_animation_frames(1280, 0, 1280, 720, 6))
            self.background_spritesheet = self.spritesheet.get_sprite(0,0,1280,720)
            self.background_spritesheet = pygame.transform.scale(
                self.background_spritesheet, (1280, 720)
            )
        except pygame.error:
            # Create a placeholder background if spritesheet doesn't exist
            self.background_spritesheet = pygame.Surface((1280, 720))
            # self.background_spritesheet.fill((50, 50, 100))  # Dark blue background
    def update_background(self,screen,index):

        #self.background_spritesheet = pygame.image.load(sprite_path)
        
        self.background_spritesheet = self.bg_animation.get_specific_frame(index)

    def start_selection(self):
        """Start the single player option selection process"""
        if not self.selecting and not self.selection_complete:
            self.selecting = True
            self.current_highlighted = 0
            self.start_time = pygame.time.get_ticks()
            self.last_highlight_change = self.start_time
            self.selected_option = None
            print("Single player selection started!")
            
    def update(self):
        """Update the selection process"""
        if not self.selecting:
            return None
            
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.start_time
        
        # Check if selection time is complete
        if elapsed_time >= TIEMPO_SELECCION_SINGLEPLAYER:
            # Randomly select an option
            self.selected_option = random.choice(self.options)
            self.selecting = False
            self.selection_complete = True
            print(f"Selected: {self.selected_option}")
            return self.selected_option
            
        # Cycle through options during selection
        if current_time - self.last_highlight_change >= TIEMPO_MOSTRAR_OPCION:
            self.current_highlighted = (self.current_highlighted + 1) % len(self.options)
            self.last_highlight_change = current_time
            

            
        return None
        
    def draw(self, screen):
        """Draw the single player selection interface"""
        # Draw background
        screen.blit(self.background_spritesheet, (0, 0))
        
        # Draw title
        font_large = pygame.font.Font(None, 96)
        title_text = font_large.render("SELECT GAME MODE", True, BLANCO)
        title_rect = title_text.get_rect(center=(ANCHO // 2, 100))
        screen.blit(title_text, title_rect)
        
        # Draw options in a 3x2 grid
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        grid_start_x = ANCHO // 6
        grid_start_y = 200
        grid_width = (ANCHO - 2 * grid_start_x) // 3
        grid_height = (ALTO - grid_start_y - 100) // 2
        
        for i, option in enumerate(self.options):
            row = i // 3
            col = i % 3
            
            x = grid_start_x + col * grid_width
            y = grid_start_y + row * grid_height
            
            # Create option rectangle
            option_rect = pygame.Rect(x, y, grid_width - 20, grid_height - 20)
            
            # Highlight current option during selection
            if self.selecting and i == self.current_highlighted:
                pygame.draw.rect(screen, (255, 255, 0), option_rect, 5)  # Yellow highlight
                pygame.draw.rect(screen, (255, 255, 100, 100), option_rect)  # Semi-transparent yellow fill
            elif self.selection_complete and option == self.selected_option:
                pygame.draw.rect(screen, (0, 255, 0), option_rect, 8)  # Green highlight for selected
                pygame.draw.rect(screen, (0, 255, 0, 100), option_rect)  # Semi-transparent green fill
            else:
                pygame.draw.rect(screen, BLANCO, option_rect, 2)  # White border
                
            # Draw option text
            self.bg_animation.get_next_frame()
            text_surface = font_medium.render(option, True, BLANCO)
            text_rect = text_surface.get_rect(center=option_rect.center)
            screen.blit(text_surface, text_rect)
            
        # Draw instructions
        if not self.selecting and not self.selection_complete:
            instruction_text = font_small.render("Press SPACE to start selection", True, BLANCO)
            instruction_rect = instruction_text.get_rect(center=(ANCHO // 2, ALTO - 50))
            screen.blit(instruction_text, instruction_rect)
        elif self.selecting:
            remaining_time = (TIEMPO_SELECCION_SINGLEPLAYER - (pygame.time.get_ticks() - self.start_time)) // 1000 + 1
            time_text = font_small.render(f"Selecting... {remaining_time}s", True, BLANCO)
            time_rect = time_text.get_rect(center=(ANCHO // 2, ALTO - 50))
            screen.blit(time_text, time_rect)
        elif self.selection_complete:
            result_text = font_medium.render(f"Selected: {self.selected_option}", True, (0, 255, 0))
            result_rect = result_text.get_rect(center=(ANCHO // 2, ALTO - 80))
            screen.blit(result_text, result_rect)
            
            continue_text = font_small.render("Press SPACE to continue or R to restart", True, BLANCO)
            continue_rect = continue_text.get_rect(center=(ANCHO // 2, ALTO - 30))
            screen.blit(continue_text, continue_rect)
            
    def reset(self):
        """Reset the selector for a new selection"""
        self.selecting = False
        self.selected_option = None
        self.current_highlighted = 0
        self.selection_complete = False
        print("Single player selector reset")
        
    def is_selection_complete(self):
        """Check if selection process is complete"""
        return self.selection_complete
        
    def get_selected_option(self):
        """Get the currently selected option"""
        return self.selected_option
