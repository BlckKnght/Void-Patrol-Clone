# ship.py

from __future__ import division

import copy

import pygame
import pygame.display
import pygame.draw

from entity import Entity
from shiperror import *

class ThrustSpec(object):
    def __init__(self, max_thrust, max_g, thrusters, spin_cost):
        self.max_thrust = max_thrust
        self.max_g = max_g
        self.thrusters = thrusters
        self.spin_cost = spin_cost

    def __repr__(self):
        return "ThrustSpec(%d, %d, %d, %d)" % (self.max_thrust, self.max_g,
                                               self.thrusters, self.spin_cost)

    def __str__(self):
        return "%d%s%d(%d)" % (self.max_thrust, [None, "S", "D"][self.thrusters],
                               self.spin_cost, self.max_g)

class Ship(Entity):
    def __init__(self, id, pos, vel, orientation,
                 thrust_spec, used_thrust = 0, used_g = 0):
        super(Ship, self).__init__(id, pos, vel, orientation)
        self.thrust_spec = thrust_spec
        self.used_thrust = used_thrust
        self.used_g = used_g
        
    def thrust(self, direction):
        if self.used_thrust + 1 > self.thrust_spec.max_thrust:
            raise ThrustLimit()
        if self.used_g + 1 > self.thrust_spec.max_g:
            raise GLimit()
        super(Ship, self).thrust(direction)
        self.used_thrust += 1
        self.used_g += 1

    def boost(self, direction):
        if self.used_thrust + 1 > self.thrust_spec.max_thrust:
            raise ThrustLimit()
        if self.used_g + 1 > self.thrust_spec.max_g:
            raise GLimit()
        super(Ship, self).boost(direction)
        self.used_thrust += 1
        self.used_g += 1
        
    def rotate(self, sign):
        if self.used_thrust + self.thrust_spec.spin_cost > \
           self.thrust_spec.max_thrust:
            raise ThrustLimit()
        super(Ship, self).rotate(sign)
        self.used_thrust += self.thrust_spec.spin_cost

    def update(self):
        self.used_thrust = 0
        self.used_g = 0
        super(Ship, self).update()
        
    def command(self, c):
        assert 4 <= c <= 9
        if c == 8:
            if self.thrust_spec.thrusters != 1:
                raise IllegalCommand()
            self.thrust(self.orientation)
        elif c == 5:
            if self.thrust_spec.thrusters != 1:
                raise IllegalCommand()
            self.boost(self.orientation)
        elif c == 7:
            if self.thrust_spec.thrusters != 2:
                raise IllegalCommand()
            self.thrust(self.orientation.dec())
        elif c == 9:
            if self.thrust_spec.thrusters != 2:
                raise IllegalCommand()
            self.thrust(self.orientation.inc())
        elif c == 4:
            self.rotate(-1)
        elif c == 6:
            self.rotate(1)
        else:
            raise ValueError()

    def __repr__(self):
        return "%s(%s, %s, %s, %s, %s, %d)" % (self.__class__.__name__,
                                               repr(self.id),
                                               repr(self.pos),
                                               repr(self.vel),
                                               repr(self.orientation),
                                               repr(self.thrust_spec),
                                               self.used_thrust)
    
    def draw_ship(self, hexfield, color):
        center, front, left, right = self.display_vecs(hexfield)
        l = [center + front * 1/3,
             center + (front + right) * (-1/6),
             center + (front + left) * (-1/6)]
        pygame.draw.aalines(pygame.display.get_surface(), color, True, l)

    def draw_all_moves(self, hexfield, color, visited = None):
        if visited == None:
            visited = {}
            
        state = (self.pos[0], self.pos[1], self.orientation)
        if visited.has_key(state):
            if visited[state] <= self.used_thrust:
                return
        else:
            self.draw_front_arc(hexfield, color)
                
        visited[state] = self.used_thrust

        s = None
        for c in [8, 7, 9, 4, 6]:
            if s is None:
                s = copy.deepcopy(self)
            try:
                s.command(c)
                s.draw_all_moves(hexfield, color, visited)
                s = None
            except ShipError:
                pass
