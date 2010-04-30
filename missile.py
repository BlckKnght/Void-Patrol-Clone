# missile.py

from __future__ import division

import copy
import itertools

import pygame
import pygame.display
import pygame.draw

from entity import Entity
from vpmath import HexVec

class Missile(Entity):
    def __init__(self, id, pos, vel, orientation, max_thrust,
                 seek_algorithm=0):
        super(Missile, self).__init__(id, pos, vel, orientation)

        self.max_thrust = max_thrust
        self.seek_algorithm = seek_algorithm

    def berserk_seek(self, target):
        target_hexvec = target.pos - self.pos

        components = target_hexvec.components()

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
                turns0 = abs(components[0][0] - self.orientation)
                turns1 = abs(components[1][0] - self.orientation)
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

    def smart_seek(self, target):
        if self.pos == target.pos:
            return

        pos_hv = target.pos - self.pos
        vel_hv = target.vel - self.vel

        for lookahead in itertools.count(): # will increase forever!
            seek_hv = pos_hv + vel_hv * lookahead
            scaled_hv = seek_hv // (lookahead+1)**2

            if abs(scaled_hv) > self.max_thrust:
               continue

            components = scaled_hv.components()

            #print lookahead, seek_hv.components(), components

            if len(components) == 0:
                return
            elif len(components) == 1:
                turns = abs(components[0][0] - self.orientation)
                if turns + components[0][1] > self.max_thrust:
                    continue

                self.orientation = components[0][0]
                for i in range(components[0][1]):
                    self.thrust(self.orientation)

                return

            else: #len(components) == 2
                turns0 = abs(components[0][0] - self.orientation)
                turns1 = abs(components[1][0] - self.orientation)

                if max(turns0, turns1)+(components[0][1] +
                                        components[1][1]) > self.max_thrust:
                    continue

                for i in range(components[0][1]):
                    self.thrust(components[0][0])
                for i in range(components[1][1]):
                    self.thrust(components[1][0])

                if turns0 > turns1:
                    self.orientation = components[0][0]
                else:
                    self.orientation = components[1][0]

                return
    _algorithms = [berserk_seek,
                   smart_seek]
    def seek(self, target):
        return self._algorithms[self.seek_algorithm](self, target)


    def draw_missile(self, hexfield, color):
        center, front, left, right = self.display_vecs(hexfield)
        l = [center + front * 1/3,
             center + (front + right/2) * (-1/6),
             center + (front + left/2) * (-1/6)]
        pygame.draw.aalines(pygame.display.get_surface(), color, True, l)

