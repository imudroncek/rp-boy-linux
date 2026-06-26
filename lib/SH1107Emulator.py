import pygame

class SH1107:
    """Handles the physical hardware emulation, centering, scaling, and pixel-grid mask."""
    def __init__(self, options, width=640, height=480, scale=3):
        self.options = options
        self.screen_w = width
        self.screen_h = height
        self.scale = scale
        
        # Fixed hardware dimensions of the SH1107
        self.canvas_size = 128
        self.scaled_w = self.canvas_size * self.scale
        self.scaled_h = self.canvas_size * self.scale
        
        # Centering Math (Letterboxing/Pillarboxing)
        self.offset_x = (self.screen_w - self.scaled_w) // 2
        self.offset_y = (self.screen_h - self.scaled_h) // 2
        
        # Surfaces
        self.screen = pygame.display.set_mode((self.screen_w, self.screen_h))
        pygame.display.set_caption("SH1107 OLED Emulator - Local Dev Mode")
        self.canvas = pygame.Surface((self.canvas_size, self.canvas_size))

        # Pre-load a standard crisp monospace font to replicate the 8x8 bitmap look
        # Antialiasing is turned off later to keep it pixelated
        pygame.font.init()
        self.font = pygame.font.SysFont("Courier", 7, bold=True)
        
        # Color Palette
        self.COLOR_WHITE = (255, 255, 255)
        self.COLOR_BLACK = (0, 0, 0)
        
        self._pre_render_grid()

    def _get_color_black(self):
        if (self.options.green_background):
            return (0, 128, 0)
        else:
            return self.COLOR_BLACK

    def _pre_render_grid(self):
        """Creates the physical OLED pixel-gap mask overlay once to maximize PC performance."""
        self.grid_mask = pygame.Surface((self.scaled_w, self.scaled_h), pygame.SRCALPHA)
        for i in range(0, self.scaled_w, self.scale):
            pygame.draw.line(self.grid_mask, (0, 0, 0, 255), (i + self.scale - 1, 0), (i + self.scale - 1, self.scaled_h))
            pygame.draw.line(self.grid_mask, (0, 0, 0, 255), (0, i + self.scale - 1), (self.scaled_w, i + self.scale - 1))

    def get_canvas(self):
        """Returns the 128x128 surface for the app to draw on."""
        self.canvas.fill(self._get_color_black())
        return self.canvas

    def draw_pixel(self, x, y, active=True):
        """Helper to draw individual raw hardware pixels with proper panel coloring."""
        if not (0 <= x < 128 and 0 <= y < 128):
            return
        if not active:
            self.canvas.set_at((x, y), self._get_color_black())
            return
            
        self.canvas.set_at((x, y), self.COLOR_WHITE)

    def refresh(self):
        """Processes the scaling, applies the grid overlay, and updates the display window."""
        self.screen.fill((15, 15, 18)) # Simulated dark plastic bezel border
        
        # Nearest-neighbor upscale to keep pixels crisp
        scaled_oled = pygame.transform.scale(self.canvas, (self.scaled_w, self.scaled_h))
        if (self.options.enable_mask):
            scaled_oled.blit(self.grid_mask, (0, 0)) # Drop the OLED gap mask on top
        
        self.screen.blit(scaled_oled, (self.offset_x, self.offset_y))
        pygame.display.flip()

# -------------------------------------------------------------
    # 🛠️ MICROPYTHON COMPATIBILITY LAYER (SHIMS)
    # -------------------------------------------------------------

    def fill(self, color_bit):
        """Maps MicroPython self.display.fill(0) to Pygame."""
        # 0 is Black, 1 is White (or active panel color)
        color = self._get_color_black() if color_bit == 0 else self.COLOR_WHITE
        self.canvas.fill(color)

    def show(self):
        """Maps MicroPython self.display.show() to Pygame refresh routines."""
        self.refresh()

    def text(self, string, x, y, color_bit=1):
        """
        Maps MicroPython self.display.text("Hello", x, y, 1) directly to Pygame.
        Automatically honors the split-color physical screen zones!
        """
        color = self._resolve_color(color_bit)

        # Render the text (False sets anti-aliasing off for sharp retro pixels)
        text_surface = self.font.render(string, False, color)
        self.canvas.blit(text_surface, (x, y))

    def _resolve_color(self, color_bit):
        if color_bit == 0:
            return self._get_color_black()
        else:
            return self.COLOR_WHITE

    def pixel(self, x, y, color_bit=1):
        """Maps MicroPython self.display.pixel(x, y, 1)"""
        color = self._resolve_color(color_bit)
        # Protect against drawing out-of-bounds crashes
        if 0 <= x < self.canvas_size and 0 <= y < self.canvas_size:
            self.canvas.set_at((x, y), color)

    def line(self, x1, y1, x2, y2, color_bit=1):
        """Maps MicroPython self.display.line(x1, y1, x2, y2, 1)"""
        color = self._resolve_color(color_bit)
        pygame.draw.line(self.canvas, color, (x1, y1), (x2, y2), 1)

    def rect(self, x, y, w, h, color_bit=1):
        """Maps MicroPython self.display.rect(x, y, w, h, 1) - Outline box"""
        color = self._resolve_color(color_bit)
        pygame.draw.rect(self.canvas, color, (x, y, w, h), 1)

    def fill_rect(self, x, y, w, h, color_bit=1):
        """Maps MicroPython self.display.fill_rect(x, y, w, h, 1) - Solid box"""
        color = self._resolve_color(color_bit)
        pygame.draw.rect(self.canvas, color, (x, y, w, h), 0)
        
    def blit(self, fbuf, x, y):
        """
        Maps MicroPython self.display.blit(fbuf, x, y) to Pygame.
        Optimized opaque blit running entirely in native C-code.
        """
        if hasattr(fbuf, 'surface'):
            # Define the exact bounding box footprint of the incoming framebuffer
            rect = pygame.Rect(int(x), int(y), fbuf.width, fbuf.height)
            
            # 1. Instantly clear ONLY this footprint area back to your green COLOR_BLACK.
            # For a full-screen 128x128 canvas update, this acts as an instant frame clear.
            self.canvas.fill(self._get_color_black(), rect)
            
            # 2. Treat source pure black (0, 0, 0) as transparent so it doesn't 
            # overwrite your custom green background color with hardware black.
            fbuf.surface.set_colorkey((0, 0, 0))
            
            # 3. Blit the active white pixels natively at C-speed
            self.canvas.blit(fbuf.surface, (int(x), int(y)))