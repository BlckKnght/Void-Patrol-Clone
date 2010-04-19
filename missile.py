# missile.py

from __future__ import division

import copy

import pygame
import pygame.display
import pygame.draw

from entity import Entity
from vpmath import HexVec

class Missile(Entity):
    def __init__(self, id, pos, vel, orientation, max_thrust):
        super(Missile, self).__init__(id, pos, vel, orientation)

        self.max_thrust = max_thrust

    def berserk_seek(self, target):
        target_vector = target.pos - self.pos
        target_hexvec = HexVec.from_vector(target_vector)

        components = target_hexvec.components()

##        print target_vector
##        print target_hexvec
##        print components

        if len(components) == 0:
##            print "0 comps"
            pass
        elif len(components) == 1:
##            print "1 comps"
            direction, distance = components[0]
            
            used_thrust = abs(direction - self.orientation)
            self.orientation = direction
            
            while used_thrust < self.max_thrust and distance > 0:
                self.thrust(self.orientation)
                used_thrust += 1
                distance -= 1
        else: # len(components) == 2
##            print "2 comps"
            # Swap the component order if the distances are equal 
            # but second component requires less turning.
            if components[0][1] == components[1][1]:
                turns0 = components[0][0] - self.orientation
                turns1 = components[1][0] - self.orientation
                if turns0 > turns1:
                    components.reverse()

            used_thrust = abs(components[0][0] - self.orientation)
##            if components[0][0] - self.orientation >= 0:
##                s = "R"*used_thrust
##            else:
##                s = "L"*used_thrust
            self.orientation = components[0][0]
            
            while used_thrust < self.max_thrust and (components[0][1] or
                                                     components[1][1]):
                if components[0][1] < components[1][1]:
##                    s += str(components[0][0] - components[1][0])
##                    if components[0][0] - components[1][0] < 0:
##                        s += "R"
##                    else:
##                        s += "L"
                    self.orientation = components[1][0]
                    used_thrust += 1
                    components.reverse()
                else:
##                    s += "S"
                    self.thrust(self.orientation)
                    used_thrust += 1
                    components[0][1] -= 1

##            if used_thrust < self.max_thrust:
##                s += "X"
##
##            print s

    def draw_missile(self, hexfield, color):
        center, front, left, right = self.display_vecs(hexfield)
        l = [center + front * 1/3,
             center + (front + right/2) * (-1/6),
             center + (front + left/2) * (-1/6)]
        pygame.draw.aalines(pygame.display.get_surface(), color, True, l)
