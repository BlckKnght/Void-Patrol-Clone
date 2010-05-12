# hexfield.py

from __future__ import division

import pygame
import pygame.display
import pygame.draw
import pygame.font

from .vpmath import Vec, HexVec, Direction

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

    def center(self, focuses):
        weighted_position = HexVec()
        total_weight = 0
        for (position, weight) in focuses:
            weighted_position += position * weight
            total_weight += weight

        weight_center = Vec(weighted_position // total_weight)
        screen_center = Vec(self.width // 2, self.height // 2)

        center = screen_center - weight_center
        if (center.x + center.y) % 2 == 1:
            center += Vec(0,1)

        self.origin = center

    _hex_vertecies = [Vec(-1/3, 1), Vec(-2/3, 0),
                      Vec(-1/3, -1), Vec(1/3, -1),
                      Vec(2/3, 0), Vec(1/3, 1)]

    def draw_single_hex(self, position, color):
        offset = self.display_coords(position)
        pygame.draw.aalines(self.hex_image, color, True,
                            [self.display_coords(v) + offset
                             for v in self._hex_vertecies])

    _hex_tiling_lines = [Vec(-1, 0), Vec(-2/3, 0),
                         Vec(2/3, 0), Vec(1, 0)]

    def draw_hex_tile(self, position):
        offset = self.display_coords(position + Vec(1, 1))
        pygame.draw.aalines(self.hex_image, (255, 255, 255), False,
                            [self.display_coords(v) + offset
                             for v in self._hex_vertecies])
        pygame.draw.aaline(self.hex_image, (255, 255, 255),
                           *(self.display_coords(v) + offset
                            for v in self._hex_tiling_lines[0:2]))
        pygame.draw.aaline(self.hex_image, (255, 255, 255),
                           *(self.display_coords(v) + offset
                            for v in self._hex_tiling_lines[2:4]))

    def draw_field(self):
        if self.hex_image is None:
            self.hex_image = pygame.Surface(((self.width * 21) * self.scale,
                                             (self.height * 12) * self.scale))
            for i in range(0, self.height + 2, 2):
                for j in range(0, self.width + 2, 2):
                    self.draw_hex_tile(Vec(j, i))
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
        return self.display_coords(self.origin)

    def display_coords(self, vecs):
        if isinstance(vecs, Vec):
            return Vec(vecs.x * 21, vecs.y * 12) * self.scale
        elif isinstance(vecs, HexVec):
            return self.display_coords(Vec(vecs))
        elif isinstance(vecs, Direction):
            return self.display_coords(Vec(vecs))
        else:
            return [self.display_coords(v) for v in vecs]

    def set_top_text_fields(self, fields):
        self.top_text_fields = fields

    def set_top_text(self, field, new_text):
        if field not in self.top_text_fields:
            self.top_text_fields.append(field)

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
        if field not in self.bottom_text_fields:
            self.bottom_text_fields.append(field)

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
