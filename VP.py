from __future__ import division
import os, sys
from OpenGL.GL import *
import pygame
from pygame.locals import *

# ship class

class Vec(object):
    def __init__(self, *value):
        if len(value) > 1:
            self.value = value
        else:
            self.value = value[0]

    def __add__(self, other):
        return Vec(*tuple(i + j for i, j in zip(self.value, other.value)))

    def __sub__(self, other):
        return Vec(*tuple(i - j for i, j in zip(self.value, other.value)))

    def __mul__(self, other):
        return Vec(*tuple(i * other for i in self.value))

    def __rmul__(self, other):
        return Vec(*tuple(other * i for i in self.value))

    def __div__(self, other):
        return Vec(*tuple(i / other for i in self.value))

    def __getitem__(self, index):
        return value[index]

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "Vec(%s)" % repr(self.value)

    def __str__(self):
        return str(self.value)

class HexField(object):
    def __init__(self, width, height, scale = 2):
        self.width = width
        self.height = height
        self.scale = scale
        self.hex_image = None

    def setup_window(self):
        pygame.display.set_mode(((self.width * 21 + 7) * self.scale,
                                 (self.height * 12 + 12) * self.scale))
                                

    def draw_hex(self, x, y):
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

    def draw_field(self):
        if self.hex_image is None:
            print self.width, self.height
            self.hex_image = pygame.Surface(((self.width * 21 + 7) * self.scale,
                                             (self.height * 12 + 12) * self.scale))
            for i in range(0, self.width + 2, 2):
                for j in range(0, self.height + 2, 2):
                    self.draw_hex(i, j)
        screen = pygame.display.get_surface()
        screen.blit(self.hex_image, (0, 0))
                
    def to_display_coords(vec):
        assert (vec[0] + vec[1]) % 2 == 0
        return Vec(vec[0] * 42 + 28, vec[1] * 24 + 24)

class Direction(object):
    _instances = [None] * 6
    
    def __new__(cls, val):
        assert 0 <= val < 6
        if cls._instances[val] is None:
            cls._instances[val] = object.__new__(cls)
            cls._instances[val].val = val
        return cls._instances[val]
        
    def inc(self):
        if self.val == 5:
            return Direction(0)
        else:
            return Direction(self.val + 1)

    def dec(self):
        if self.val == 0:
            return Direction(5)
        else:
            return Direction(self.val - 1)

    def __sub__(self, other):
        dif = self.val - other.val
        if dif > 3:
            dif -= 6
        elif dif <= -3:
            dif += 6
        return dif

    _unit_vectors = [Vec(0, -2),
                     Vec(1, -1),
                     Vec(1, 1),
                     Vec(0, 2),
                     Vec(-1, 1),
                     Vec(-1, -1)]
    def vector(self):
        return self._unit_vectors[self.val]

    def __repr__(self):
        return "Direction(%d)" % self.val

    def __str__(self):
        return str(self.val)

class Entity(object):
    def __init__(self, id, pos, vel, orientation):
        self.id = id
        self.pos = pos
        self.vel = vel
        self.orientation = orientation

    def thrust(self, direction):
        vector = direction.vector()
        self.pos += vector
        self.vel += vector*2

    def boost(self, direction):
        vector = direction.vector
        self.vel += vector

    def rotate(self, sign):
        assert sign <> 0
        if sign > 0:
            self.orientation = self.orientation.inc()
        else:
            self.orientation = self.orientation.dec()

    def update(self):
        self.pos += self.vel

    def __repr__(self):
        return "Entity(%s, %s, %s, %s)" % (str(self.id),
                                           str(self.pos),
                                           str(self.vel),
                                           str(self.orientation))

class ThrustSpec(object):
    def __init__(self, max_thrust, max_g, thrusters, spin_cost):
        self.max_thrust = max_thrust
        self.max_g = max_g
        self.thrusters = thrusters
        self.spin_cost = spin_cost

    def __repr__(self):
        return "ThrustSpec(%d, %d, %d, %d)" % (self.max_thrust, self.max_g,
                                               self.thrusters, self.spin_cost)

class Ship(Entity):
    def __init__(self, id, pos, vel, orientation,
                 thrust_spec, used_thrust = 0, used_g = 0):
        Entity.__init__(self, id, pos, vel, orientation)
        self.thrust_spec = thrust_spec
        self.used_thrust = used_thrust
        self.used_g = used_g
        
    def thrust(self, direction):
        assert self.used_thrust + 1 <= self.thrust_spec.max_thrust
        assert self.used_g + 1 <= self.thrustspec.max_g
        super(Ship, self).thrust(direction)
        self.used_thrust += 1
        self.used_g += 1

    def boost(self, direction):
        assert self.used_thrust + 1 <= self.thrust_spec.max_thrust
        assert self.used_g + 1 <= self.thrustspec.max_g
        super(Ship, self).boost(direction)
        self.used_thrust += 1
        self.used_g += 1
        
    def rotate(self, direction):
        assert self.used_thrust + self.thrust_spec.spin_cost <= \
               self.thrust_spec.max_thrust
        super(Ship, self).rotate(direction)
        self.used_thrust += self.thrust_spec.spin_cost        

    def command(self, c):
        assert 4 <= c <= 9
        if c == 8:
            assert self.thrust_spec.thrusters == 1
            self.thrust(self.orientation)
        elif c == 5:
            assert self.thrust_spec.thrusters == 1
            self.boost(self.orientation)
        elif c == 7:
            assert self.thrust_spec.thrusters == 2
            self.thrust(self.orientation.dec())
        elif c == 9:
            assert self.thrust_spec.thrusters == 2
            self.thrust(self.orientation.inc())
        elif c == 4:
            self.rotate(-1)
        elif c == 6:
            self.rotate(1)
        else:
            raise ValueError()

    def __repr__(self):
        return "Ship(%s, %s, %s, %s, %s, %d)" % (repr(self.id), repr(self.pos),
                                                 repr(self.vel),
                                                 repr(self.orientation),
                                                 repr(self.thrust_spec),
                                                 self.used_thrust)
