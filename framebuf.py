import pygame

MONO_VLSB = 0
MONO_HLSB = 1
MONO_HMSB = 2

class FrameBuffer:
    def __init__(self, buffer, width, height, format_type):
        self.width = width
        self.height = height
        self.format = format_type
        self.buffer = buffer 
        self.surface = pygame.Surface((width, height))
        self.surface.fill((0, 0, 0)) 
        pygame.font.init()
        self.mono_font = pygame.font.Font("lib/PixelOperator8.ttf", 8)
        
        if buffer and len(buffer) > 0:
            if format_type == MONO_HMSB:
                self._parse_mono_hmsb(buffer)
            elif format_type == MONO_VLSB:
                self._parse_mono_vlsb(buffer)

    def _get_color(self, color_bit):
        return (255, 255, 255) if color_bit else (0, 0, 0)

    def _sync_buffer_pixel(self, x, y, color):
        if self.buffer is None or len(self.buffer) == 0:
            return
            
        if self.format == MONO_VLSB:
            page = y // 8
            byte_idx = (page * self.width) + x
            bit_idx = y % 8
            if byte_idx < len(self.buffer):
                if color:
                    self.buffer[byte_idx] |= (1 << bit_idx)
                else:
                    self.buffer[byte_idx] &= ~(1 << bit_idx)
                    
        elif self.format == MONO_HMSB:
            stride = (self.width + 7) // 8
            byte_idx = y * stride + (x // 8)
            bit_idx = 7 - (x % 8)
            if byte_idx < len(self.buffer):
                if color:
                    self.buffer[byte_idx] |= (1 << bit_idx)
                else:
                    self.buffer[byte_idx] &= ~(1 << bit_idx)

    def fill(self, color):
        self.surface.fill(self._get_color(color))
        if self.buffer is not None and len(self.buffer) > 0:
            fill_val = 0xFF if color else 0x00
            for i in range(len(self.buffer)):
                self.buffer[i] = fill_val

    def pixel(self, x, y, color=None):
        if color is None:
            if 0 <= x < self.width and 0 <= y < self.height:
                rgb = self.surface.get_at((x, y))
                return 1 if (rgb[0] > 0 or rgb[1] > 0 or rgb[2] > 0) else 0
            return 0
        else:
            if 0 <= x < self.width and 0 <= y < self.height:
                self.surface.set_at((x, y), self._get_color(color))
                self._sync_buffer_pixel(x, y, color)

    def line(self, x1, y1, x2, y2, color):
        pygame.draw.line(self.surface, self._get_color(color), (x1, y1), (x2, y2))
        min_x, max_x = max(0, min(x1, x2)), min(self.width, max(x1, x2) + 1)
        min_y, max_y = max(0, min(y1, y2)), min(self.height, max(y1, y2) + 1)
        for ry in range(min_y, max_y):
            for rx in range(min_x, max_x):
                rgb = self.surface.get_at((rx, ry))
                p_color = 1 if (rgb[0] > 0 or rgb[1] > 0 or rgb[2] > 0) else 0
                self._sync_buffer_pixel(rx, ry, p_color)

    def rect(self, x, y, w, h, color):
        pygame.draw.rect(self.surface, self._get_color(color), pygame.Rect(x, y, w, h), 1)
        for ry in range(max(0, y), min(self.height, y + h)):
            for rx in range(max(0, x), min(self.width, x + w)):
                rgb = self.surface.get_at((rx, ry))
                p_color = 1 if (rgb[0] > 0 or rgb[1] > 0 or rgb[2] > 0) else 0
                self._sync_buffer_pixel(rx, ry, p_color)

    def fill_rect(self, x, y, w, h, color):
        pygame.draw.rect(self.surface, self._get_color(color), pygame.Rect(x, y, w, h), 0)
        for ry in range(max(0, y), min(self.height, y + h)):
            for rx in range(max(0, x), min(self.width, x + w)):
                self._sync_buffer_pixel(rx, ry, color)

    def text(self, string, x, y, color=1):
        # Render using the pre-loaded 8x8 pixel font
        text_surf = self.mono_font.render(string, False, self._get_color(color))
        self.surface.blit(text_surf, (x, y))
        
        # Sync loop remains exactly the same...
        for ry in range(max(0, y), min(self.height, y + text_surf.get_height())):
            for rx in range(max(0, x), min(self.width, x + text_surf.get_width())):
                rgb = self.surface.get_at((rx, ry))
                p_color = 1 if (rgb[0] > 0 or rgb[1] > 0 or rgb[2] > 0) else 0
                self._sync_buffer_pixel(rx, ry, p_color)

    def blit(self, source, x, y, key=-1):
        if key == 0:
            temp_surf = source.surface.copy()
            temp_surf.set_colorkey((0, 0, 0))
            self.surface.blit(temp_surf, (x, y))
        else:
            self.surface.blit(source.surface, (x, y))
            
        if self.buffer is not None and len(self.buffer) > 0:
            for ry in range(max(0, y), min(self.height, y + source.height)):
                for rx in range(max(0, x), min(self.width, x + source.width)):
                    rgb = self.surface.get_at((rx, ry))
                    p_color = 1 if (rgb[0] > 0 or rgb[1] > 0 or rgb[2] > 0) else 0
                    self._sync_buffer_pixel(rx, ry, p_color)

    def _parse_mono_hmsb(self, buffer):
        stride = (self.width + 7) // 8
        for y in range(self.height):
            for x in range(self.width):
                byte_idx = y * stride + (x // 8)
                bit_idx = 7 - (x % 8)
                if byte_idx < len(buffer):
                    if (buffer[byte_idx] >> bit_idx) & 1:
                        self.surface.set_at((x, y), (255, 255, 255))

    def _parse_mono_vlsb(self, buffer):
        for y in range(self.height):
            for x in range(self.width):
                page = y // 8
                byte_idx = (page * self.width) + x
                bit_idx = y % 8
                if byte_idx < len(buffer):
                    if (buffer[byte_idx] >> bit_idx) & 1:
                        self.surface.set_at((x, y), (255, 255, 255))