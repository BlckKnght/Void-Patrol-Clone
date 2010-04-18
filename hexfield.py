# hexfield.py

from __future__ import division

import pygame
import pygame.display
import pygame.draw
import pygame.font

from vpmath import Vec

class HexField(object):
    def __init__(self, width, height, origin = None, scale = 2):
        self.width = width
        self.height = height
        self.origin = origin
        if self.origin is None:
            self.origin = Vec(0, 0)
        self.scale = scale

        self.hex_image = None

        self.font = pygame.font.SysFont("Arial", 12 * self.scale)
        
        self.top_text_fields = []
        self.top_text = {}
        self.top_images = {}

        self.bottom_text_fields = []
        self.bottom_text = {}
        self.bottom_images = {}

    def setup_window(self):
        pygame.display.set_mode(((self.width * 21 + 7) * self.scale,
                                 (self.height * 12 + 12) * self.scale))
        
    def draw_hex_tile(self, x, y):
        xunit = 21 * self.scale
        yunit = 12 * self.scale
        pygame.draw.aalines(self.hex_image, (255, 255, 255), False,
                            [((1/3 + x) * xunit, (2 + y) * yunit),
                             ((      x) * xunit, (1 + y) * yunit),
                             ((1/3 + x) * xunit, (    y) * yunit),
                             ((1   + x) * xunit, (    y) * yunit),
                             ((4/3 + x) * xunit, (1 + y) * yunit),
                             ((1   + x) * xunit, (2 + y) * yunit)])
        pygame.draw.aaline(self.hex_image, (255, 255, 255),
                           ((4/3 + x) * xunit, (1 + y) * yunit),
                           ((2   + x) * xunit, (1 + y) * yunit))

    def draw_single_hex(self, x, y, color):
        xunit = 21 * self.scale
        yunit = 12 * self.scale
        pygame.draw.aalines(self.hex_image, color, True,
                            [((1/3 + x) * xunit, (2 + y) * yunit),
                             ((      x) * xunit, (1 + y) * yunit),
                             ((1/3 + x) * xunit, (    y) * yunit),
                             ((1   + x) * xunit, (    y) * yunit),
                             ((4/3 + x) * xunit, (1 + y) * yunit),
                             ((1   + x) * xunit, (2 + y) * yunit)], False)

    def draw_field(self):
        if self.hex_image is None:
            self.hex_image = pygame.Surface(((self.width * 21 + 7) * self.scale,
                                             (self.height * 12 + 12) * self.scale))
            for i in range(0, self.width + 2, 2):
                for j in range(0, self.height + 2, 2):
                    self.draw_hex_tile(i, j)
        screen = pygame.display.get_surface()
        screen.blit(self.hex_image, (0, 0))

    def draw_text(self):
        screen = pygame.display.get_surface()
        offset = 0
        for field in self.top_text_fields:
            try:
                image = self.top_images[field]
                screen.blit(image, (0, offset))
                offset += image.get_height()
            except KeyError:
                pass

        offset = self.hex_image.get_height()
        for field in self.bottom_text_fields:
            try:
                image = self.bottom_images[field]
                offset -= image.get_height()
                screen.blit(image, (0, offset))
            except KeyError:
                pass
            
    def origin_coords(self):
        return Vec(self.origin[0] * 21 + 14,
                   self.origin[1] * 12 + 12) * self.scale
    
    def display_coords(self, vecs):
        if isinstance(vecs, Vec):
            return Vec(vecs[0] * 21, vecs[1] * 12) * self.scale
        else:
            return [Vec(v[0] * 21, v[1] * 12) * self.scale
                    for v in vecs]

    def set_top_text_fields(self, fields):
        self.top_text_fields = fields

    def set_top_text(self, field, new_text):
        if new_text is None:
            try:
                del self.top_text[field]
                del self.top_images[field]
            except KeyError:
                pass
            return
        
        try:
            if self.top_text[field] == new_text:
                return
        except KeyError:
            pass

        self.top_text[field] = new_text
        self.top_images[field] = self.font.render(new_text, True,
                                                  (255, 255, 255),
                                                  (0, 0, 0))


    def set_bottom_text_fields(self, fields):
        self.bottom_text_fields = fields

    def set_bottom_text(self, field, new_text):
        if new_text is None:
            try:
                del self.bottom_text[field]
                del self.bottom_images[field]
            except KeyError:
                pass
            return
            
            
        try:    
            if self.bottom_text[field] == new_text:
                return
        except KeyError:
            pass

        self.bottom_text[field] = new_text
        self.bottom_images[field] = self.font.render(new_text, True,
                                                     (255, 255, 255),
                                                     (0, 0, 0))
