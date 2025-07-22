import pygame

class SpriteSheet:
    """
    A utility class for managing spritesheets in Pygame.

    This class loads a spritesheet image and provides methods to
    extract individual sprites or sequences of sprites from it.
    """

    def __init__(self, filename):
        """
        Initializes the Spritesheet with the given filename.

        Args:
            filename (str): The path to the spritesheet image file.
        """
        try:
            self.sheet = pygame.image.load(filename).convert_alpha()
        except pygame.error as e:
            print(f"Unable to load spritesheet image: {filename}, {e}")
            raise SystemExit(e)
        self.filename = filename

    def get_sprite(self, x, y, width, height):
        """
        Extracts a single sprite from the spritesheet.

        Args:
            x (int): The x-coordinate (left edge) of the sprite on the spritesheet.
            y (int): The y-coordinate (top edge) of the sprite on the spritesheet.
            width (int): The width of the sprite.
            height (int): The height of the sprite.

        Returns:
            pygame.Surface: A new Surface containing the extracted sprite.
        """
        # Create a new blank surface for the sprite, with alpha channel for transparency
        sprite = pygame.Surface([width, height], pygame.SRCALPHA)
        # Blit the desired part of the spritesheet onto the new surface
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        return sprite

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