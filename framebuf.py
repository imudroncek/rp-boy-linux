import pygame

# Emulate the MicroPython framebuf format constants
MONO_VLSB = 0
MONO_HLSB = 1
MONO_HMSB = 2  # This is the one your Invader screen uses

class FrameBuffer:
    def __init__(self, buffer, width, height, format_type):
        self.width = width
        self.height = height
        self.format = format_type
        
        # Create a tiny transparent surface to hold our sprite pixels
        self.surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.surface.fill((0, 0, 0, 0)) # Clear to transparent
        
        if format_type == MONO_HMSB:
            self._parse_mono_hmsb(buffer)

    def _parse_mono_hmsb(self, buffer):
        """
        Unpacks MicroPython Horizontal Most-Significant-Bit byte streams.
        Each bit represents 1 pixel (1 = filled, 0 = empty).
        """
        stride = (self.width + 7) // 8
        for y in range(self.height):
            for x in range(self.width):
                byte_idx = y * stride + (x // 8)
                bit_idx = 7 - (x % 8)
                
                if byte_idx < len(buffer):
                    # Check if the specific bit is flipped 'On'
                    bit_active = (buffer[byte_idx] >> bit_idx) & 1
                    if bit_active:
                        # Draw a solid white pixel onto our sprite canvas
                        self.surface.set_at((x, y), (255, 255, 255, 255))