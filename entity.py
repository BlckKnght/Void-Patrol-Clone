# entity.py

from __future__ import division

import pygame
import pygame.display
import pygame.draw

from vpmath import HexVec

class Entity(object):
    def __init__(self, id, pos, vel, orientation):
        self.id = id
        self.pos = pos
        self.vel = vel
        self.orientation = orientation

    def thrust(self, direction):
        hv = HexVec(direction)
        self.pos += hv
        self.vel += hv*2

    def boost(self, direction):
        hv = HexVec(direction)
        self.vel += hv

    def rotate(self, sign):
        assert sign != 0
        if sign > 0:
            self.orientation += 1
        else:
            self.orientation -= 1

    def update(self):
        self.pos += self.vel

    def __repr__(self):
        return "Entity({0}, {1}, {2}, {3})".format(repr(self.id),
                                                   repr(self.pos),
                                                   repr(self.vel),
                                                   repr(self.orientation))

    def display_vecs(self, hexfield):
        center, front, left, right = \
                hexfield.display_coords((self.pos,
                                         self.orientation,
                                         self.orientation - 1,
                                         self.orientation + 1))
        center += hexfield.origin_coords()

        return center, front, left, right

    def draw_front_arc(self, hexfield, color):
        center, front, left, right = self.display_vecs(hexfield)
        l = [center + (front * 3 + right * 2) * (3/40),
             center + front * 3/8,
             center + (front * 3 + left * 2) * (3/40)]
        pygame.draw.aalines(pygame.display.get_surface(), color, False, l)

    def draw_vel(self, hexfield, color):
        start = hexfield.display_coords(self.pos) + hexfield.origin_coords()
        end = start + hexfield.display_coords(self.vel)
        pygame.draw.aaline(pygame.display.get_surface(), color, start, end)

    def draw_connection(self, hexfield, color, other):
        start = hexfield.display_coords(self.pos) + hexfield.origin_coords()
        end = hexfield.display_coords(other.pos) + hexfield.origin_coords()
        pygame.draw.aaline(pygame.display.get_surface(), color, start, end)
