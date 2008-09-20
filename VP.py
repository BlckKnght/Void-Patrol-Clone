from __future__ import division
import os, sys, copy
import pygame
import pygame.display
import pygame.draw
import pygame.event
import pygame.font
import pygame.time
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

    def __truediv__(self, other):
        return Vec(*tuple(i / other for i in self.value))

    __div__ = __truediv__

    def __getitem__(self, index):
        return self.value[index]

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "Vec(%s)" % repr(self.value)

    def __str__(self):
        return str(self.value)

    def __itr__(self):
        return itr(self.value)

class BaseHexVec(object):
    def __init__(self, direction, distance):
        self.direction = direction
        self.distance = distance

    def vector(self):
        return self.direction.vector() * distance

    
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
            self.hex_image = pygame.Surface(((self.width * 21 + 7) * self.scale,
                                             (self.height * 12 + 12) * self.scale))
            for i in range(0, self.width + 2, 2):
                for j in range(0, self.height + 2, 2):
                    self.draw_hex(i, j)
        screen = pygame.display.get_surface()
        screen.blit(self.hex_image, (0, 0))
                
    def display_coords(self, vecs):
        if isinstance(vecs, Vec):
            return Vec(vecs[0] * 21 + 14, vecs[1] * 12 + 12) * self.scale
        else:
            return [Vec(v[0] * 21 + 14, v[1] * 12 + 12) * self.scale
                    for v in vecs]
        
    def relative_display_coords(self, vecs):
        if isinstance(vecs, Vec):
            return Vec(vecs[0] * 21, vecs[1] * 12) * self.scale
        else:
            return [Vec(v[0] * 21, v[1] * 12) * self.scale
                    for v in vecs]
    
class Direction(object):
    _instances = [None] * 6
    
    def __new__(cls, val):
        if cls._instances[val] is None:
            cls._instances[val] = object.__new__(cls)
            cls._instances[val].val = val
        return cls._instances[val]

    def __getnewargs__(self):
        return (self.val,)
    
    def inc(self):
        if self.val == 5:
            return Direction(0)
        else:
            return Direction(self.val + 1)

    def dec(self):
        return Direction(self.val - 1) # negative values are ok

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
        vector = direction.vector()
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

class ShipError(ValueError):
    pass

class GLimit(ShipError):
    pass

class ThrustLimit(ShipError):
    pass

class IllegalCommand(ShipError):
    pass

class Ship(Entity):
    def __init__(self, id, pos, vel, orientation,
                 thrust_spec, used_thrust = 0, used_g = 0):
        Entity.__init__(self, id, pos, vel, orientation)
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
        
    def rotate(self, direction):
        if self.used_thrust + self.thrust_spec.spin_cost > \
           self.thrust_spec.max_thrust:
            raise ThrustLimit()
        super(Ship, self).rotate(direction)
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
        return "Ship(%s, %s, %s, %s, %s, %d)" % (repr(self.id), repr(self.pos),
                                                 repr(self.vel),
                                                 repr(self.orientation),
                                                 repr(self.thrust_spec),
                                                 self.used_thrust)
    
    def display_vecs(self, hexfield):
        center = hexfield.display_coords(self.pos)
        front = hexfield.relative_display_coords(self.orientation.vector())
        left = hexfield.relative_display_coords(self.orientation.dec().vector())
        right = hexfield.relative_display_coords(self.orientation.inc().vector())
        return center, front, left, right

    def draw_ship(self, hexfield, color):
        center, front, left, right = self.display_vecs(hexfield)
        l = [center + front * 1/3,
             center + (front + right) * (-1/6),
             center + (front + left) * (-1/6)]
        pygame.draw.aalines(pygame.display.get_surface(), color, True, l)

    def draw_front_arc(self, hexfield, color):
        center, front, left, right = self.display_vecs(hexfield)
        l = [center + (front * 3 + right * 2) * (3/40),
             center + front * 3/8,
             center + (front * 3 + left * 2) * (3/40)]
        pygame.draw.aalines(pygame.display.get_surface(), color, False, l)
        
    def draw_all_moves(self, hexfield, color):
        self.draw_front_arc(hexfield)
        s = None
        for c in [8, 7, 9, 4, 6]:
            if s is None:
                s = copy.deepcopy(self)
            try:
                s.command(c)
                s.draw_all_moves(hexfield, color)
                s = None
            except ShipError:
                pass

if __name__ == "__main__":
    pygame.init()
    h = HexField(30,30)
    h.setup_window()
    h.draw_field()
    
    s = Ship(1, Vec(15,15), Vec(0, 0), Direction(0),
             ThrustSpec(5, 4, 2, 2))
    sprime = copy.deepcopy(s)
    sprime.update()
    sprimeprime = copy.deepcopy(sprime)
    sprimeprime.update()
    
    sprimeprime.draw_ship(h, (128, 128, 128))
    sprime.draw_ship(h, (192, 192, 192))
    s.draw_ship(h, (255, 255, 255))
    pygame.display.flip()
    
    pygame.event.set_allowed(None)
    pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
    
    loop = True
    while loop:
        e = pygame.event.wait()
        if e.type == pygame.QUIT:
            loop = False
        elif e.type == pygame.KEYDOWN:
            try:
                if e.key == K_k or e.key == K_KP8:
                    sprime.command(8)
                    sprimeprime = copy.deepcopy(sprime)
                    sprimeprime.update()
                elif e.key == K_i or e.key == K_KP5:
                    sprime.command(5)
                    sprimeprime = copy.deepcopy(sprime)
                    sprimeprime.update()
                elif e.key == K_u or e.key == K_KP7:
                    sprime.command(7)
                    sprimeprime = copy.deepcopy(sprime)
                    sprimeprime.update()
                elif e.key == K_o or e.key == K_KP9:
                    sprime.command(9)
                    sprimeprime = copy.deepcopy(sprime)
                    sprimeprime.update()
                elif e.key == K_j or e.key == K_KP4:
                    sprime.command(4)
                    sprimeprime = copy.deepcopy(sprime)
                    sprimeprime.update()
                elif e.key == K_l or e.key == K_KP6:
                    sprime.command(6)
                    sprimeprime = copy.deepcopy(sprime)
                    sprimeprime.update()
                elif e.key == K_RETURN or e.key == K_KP_ENTER:
                    s = sprime
                    sprime = copy.deepcopy(s)
                    sprime.update()
                    sprimeprime = copy.deepcopy(sprime)
                    sprimeprime.update()
                elif e.key == K_x or e.key == K_KP0:
                    sprime = copy.deepcopy(s)
                    sprime.update()
                    sprimeprime = copy.deepcopy(sprime)
                    sprimeprime.update()
                elif e.key == K_q or e.key == K_ESCAPE:
                    loop = False
                else:
                    print "I don't recognize key: %s" % str(e.key)

            except ShipError:
                surface = pygame.display.get_surface()
                surface.fill((255, 255, 255))
                pygame.display.flip()
                pygame.time.wait(40)

        h.draw_field()
        sprimeprime.draw_ship(h, (128, 128, 128))
        sprime.draw_ship(h, (192, 192, 192))
        s.draw_ship(h, (255, 255, 255))

        pygame.display.flip()
        
    pygame.quit()
