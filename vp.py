from __future__ import division

import copy
import math
import os
import sys

import pygame
import pygame.display
import pygame.draw
import pygame.event
import pygame.font
import pygame.time
from pygame.locals import *

from vpmath import Vec, Direction, HexVec
from hexfield import HexField
from entity import Entity
from ship import ThrustSpec, Ship, ShipError, \
                 GLimit, ThrustLimit, IllegalCommand

class App(object):

    badger_spec = ThrustSpec(4, 3, 1, 1)
    javelin_spec = ThrustSpec(6, 4, 1, 2)
    sparrowhawk_spec = ThrustSpec(4, 3, 2, 1)
    lone_wolf_spec = ThrustSpec(5, 4, 2, 2)
    
    def __init__(self):
        pygame.init()
    
    def setup_window(self, width = 20, height = 30, scale = 2):
        cX = width // 2
        cY = height // 2
        if (cX + cY) % 2 != 0:
            cY += 1
        self.h = HexField(width, height, Vec(cX, cY), scale)
        self.h.setup_window()
        self.h.set_top_text_fields(["Ship Name", "Ship Maneuverability", "Energy", "Gs"])
        self.h.set_bottom_text_fields(["Velocity", "Position", "Notice"])
        self.h.draw_field()

    def setup_ship(self, name = "Badger", thrust_spec = badger_spec):
        self.s = Ship(name, Vec(0,0), Vec(0, 0), Direction(0), thrust_spec)
        self.h.set_top_text("Ship Name", str(self.s.id))
        self.h.set_top_text("Ship Maneuverability", str(self.s.thrust_spec))
        self.update()

    def draw(self):
        self.h.draw_field()
        self.h.draw_text()
        self.h.draw_single_hex(0, 0, (128, 0, 0))
        self.sprimeprime.draw_all_moves(self.h, (128, 128, 128))
        self.sprime.draw_all_moves(self.h, (255, 255, 255))
        self.sprime.draw_connection(self.h, (128, 128, 128), self.sprimeprime)
        self.s.draw_connection(self.h, (255, 255, 255), self.sprime)
        self.sprime.draw_ship(self.h, (128, 128, 128))
        self.s.draw_ship(self.h, (255, 255, 255))
        
        pygame.display.flip()

    def update_step(self):
        self.sprimeprime = copy.deepcopy(self.sprime)
        self.sprimeprime.update()
        self.h.set_top_text("Energy", "Energy: %d" %
                                (self.sprime.thrust_spec.max_thrust - self.sprime.used_thrust))
        self.h.set_top_text("Gs", "G load: %d" % self.sprime.used_g)
        self.h.set_bottom_text("Position", "Position: %s" % HexVec.from_vector(self.sprime.pos))
        hv = HexVec.from_vector(self.sprime.vel)
        self.h.set_bottom_text("Velocity", "Speed: %d (%s)" % (abs(hv),
                                                               " + ".join("%dx%s" % tuple(reversed(c))
                                                                          for c in hv.components())))
        self.h.set_bottom_text("Notice", None)

    def update(self):
        self.sprime = copy.deepcopy(self.s)
        self.sprime.update()
        self.update_step()

    def loop(self):
        pygame.event.set_allowed(None)
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN])
    
        loop = True
        while loop:
            self.draw()
            
            e = pygame.event.wait()

            if e.type == pygame.KEYDOWN:
                try:
                    if e.key == K_k or e.key == K_KP8:
                        self.sprime.command(8)
                        self.update_step()
                    elif e.key == K_i or e.key == K_KP5:
                        self.sprime.command(5)
                        self.update_step()
                    elif e.key == K_u or e.key == K_KP7:
                        self.sprime.command(7)
                        self.update_step()
                    elif e.key == K_o or e.key == K_KP9:
                        self.sprime.command(9)
                        self.update_step()
                    elif e.key == K_j or e.key == K_KP4:
                        self.sprime.command(4)
                        self.update_step()
                    elif e.key == K_l or e.key == K_KP6:
                        self.sprime.command(6)
                        self.update_step()
                    elif e.key == K_RETURN or e.key == K_KP_ENTER:
                        self.s = self.sprime
                        self.update()
                    elif e.key == K_x or e.key == K_KP0:
                        self.update()
                    elif e.key == K_F1:
                        self.setup_ship("Badger", self.badger_spec)
                    elif e.key == K_F2:
                        self.setup_ship("Javelin", self.javelin_spec)
                    elif e.key == K_F3:
                        self.setup_ship("Sparrowhawk", self.sparrowhawk_spec)
                    elif e.key == K_F4:
                        self.setup_ship("Lone Wolf", self.lone_wolf_spec)
                    elif e.key == K_q or e.key == K_ESCAPE:
                        loop = False
                    else:
                        print "I don't recognize key: %s" % str(e.key)

                except ThrustLimit:
                    self.h.set_bottom_text("Notice", "Thrust limit exceeded!")
                except GLimit:
                    self.h.set_bottom_text("Notice", "G limit exceeded!")
                except IllegalCommand:
                    self.h.set_bottom_text("Notice", "Illegal command for this fighter!")
                    
            elif e.type == pygame.QUIT:
                loop = False
            
if __name__ == "__main__":
    try:
        a = App()
        a.setup_window(50, 50, 1)
        a.setup_ship()
        a.loop()
    finally:
        pygame.quit()
