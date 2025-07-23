import pygame
from spritesheet import SpriteSheet

class SpriteAnimation:

    def __init__(self, sheet, frames,frame_index=0):
        
        self.spritesheet = sheet
        self.spriteframes = frames
        self.frame_index = frame_index

    def get_current_frame(self):
        try: 
            return self.spriteframes[self.frame_index]
        except:
            return self.spriteframes[0]
    def get_next_frame(self):
        self.frame_index += 1 
        if len(self.spriteframes)<=self.frame_index:
            self.frame_index=0
        return self.get_current_frame()
    
    def get_specific_frame(self,index):
        try: 
            return self.spriteframes[self.frame_index]
        except:
            return self.spriteframes[0]
    def get_animation_frames(self, start_x, start_y, frame_width, frame_height, num_frames, orientation='horizontal', padding=0):
        """
        Extracts a sequence of animation frames from the spritesheet.

        Args:
            start_x (int): The x-coordinate of the first frame.
            start_y (int): The y-coordinate of the first frame.
            frame_width (int): The width of each animation frame.
            frame_height (int): The height of each animation frame.
            num_frames (int): The number of frames in the animation sequence.
            orientation (str): 'horizontal' or 'vertical' indicating how frames are laid out.
                               Defaults to 'horizontal'.
            padding (int): Optional padding (space) between frames. Defaults to 0.

        Returns:
            list: A list of pygame.Surface objects, each representing an animation frame.
        """
        frames = []
        for i in range(num_frames):
            if orientation == 'horizontal':
                x = start_x + (i * (frame_width + padding))
                y = start_y
            elif orientation == 'vertical':
                x = start_x
                y = start_y + (i * (frame_height + padding))
            else:
                raise ValueError("Orientation must be 'horizontal' or 'vertical'")

            frames.append(self.get_sprite(x, y, frame_width, frame_height))
        return frames