from __future__ import division

import pygame
import pygame.display
import pygame.event
from pygame.locals import *

from .vpmath import Vec, Direction, HexVec
from .hexfield import HexField
from .entity import Entity
from .ship import ThrustSpec, Ship
from .shiperror import *
from .missile import Missile

class App(object):

    badger_spec = ThrustSpec(4, 3, 1, 1)
    javelin_spec = ThrustSpec(6, 4, 1, 2)
    sparrowhawk_spec = ThrustSpec(4, 3, 2, 1)
    lone_wolf_spec = ThrustSpec(5, 4, 2, 2)

    def __init__(self):
        pygame.init()

    def quit(self):
        pygame.quit()

    def setup_window(self, width = 20, height = 30, scale = 2):
        cX = width // 2
        cY = height // 2
        if (cX + cY) % 2 != 0:
            cY += 1
        self.h = HexField(width, height, Vec(cX, cY), scale)
        self.h.setup_window()
        self.h.set_top_text_fields(["Ship Name", "Ship Maneuverability", "Energy", "Gs",
                                    "Velocity", "Position"])
        self.h.set_bottom_text_fields(["Notice"])
        self.h.draw_field()

    def setup_ship(self, name = "Badger", thrust_spec = badger_spec):
        self.s = Ship(name, HexVec(Vec(0,0)), HexVec(Vec(0, 0)),
                      Direction(0), thrust_spec)

        self.h.set_top_text("Ship Name", str(self.s.id))
        self.h.set_top_text("Ship Maneuverability", str(self.s.thrust_spec))

    def setup_missiles(self):
        self.missiles = []
        self.missile_number = 0

    def recenter(self):
        focuses = [(self.s.pos, 2),
                   (self.sprime.pos, 4),
                   (self.sprimeprime.pos, 2)]
        focuses.extend((m.pos, 1) for m in self.missiles)
        focuses.extend((mp.pos, 2) for mp in self.mprime)
        self.h.center(focuses)

    def add_missile(self, thrust, seek_algorithm):
        m = Missile("Missile {0}".format(self.missile_number),
                    HexVec(Vec(0, 0)), HexVec(Vec(0, 0)),
                    Direction(0), thrust, seek_algorithm)
        self.missile_number += 1
        self.missiles.append(m)

    def draw(self):
        self.h.draw_field()
        self.h.draw_text()
        #self.h.draw_single_hex(0, 0, (128, 0, 0))

        self.sprimeprime.draw_all_moves(self.h, (128, 128, 128))
        self.sprime.draw_all_moves(self.h, (255, 255, 255))
        self.sprime.draw_connection(self.h, (128, 128, 128), self.sprimeprime)
        self.s.draw_connection(self.h, (255, 255, 255), self.sprime)
        self.sprime.draw_ship(self.h, (128, 128, 128))
        self.s.draw_ship(self.h, (255, 255, 255))

        for i in range(len(self.missiles)):
            self.missiles[i].draw_vel(self.h, (128, 128, 0))
            self.mprime[i].draw_vel(self.h, (128, 128, 0))
            self.missiles[i].draw_connection(self.h, (255, 255, 0), self.mprime[i])
            self.mprime[i].draw_missile(self.h, (128, 128, 0))
            self.missiles[i].draw_missile(self.h, (255, 255, 0))

        pygame.display.flip()

    def calculate_future_states(self):
        self.sprimeprime = self.sprime.update()
        self.mprime = [m.update() for m in self.missiles]
        for mp in self.mprime:
            v = mp.seek(self.sprime)
            self.h.set_bottom_text(mp.id, mp.display_text(v))

        self.h.set_top_text("Energy",
                            "Energy: {0}".format(
                                self.sprime.thrust_spec.max_thrust -
                                self.sprime.used_thrust))
        self.h.set_top_text("Gs", "G load: {0}".format(self.sprime.used_g))
        self.h.set_top_text("Position",
                               "Position: {0}".format(self.sprime.pos))
        self.h.set_top_text("Velocity", "Speed: {0} ({1})".format(
                                abs(self.sprime.vel),
                                " + ".join("{0[1]}x{0[0]}".format(c)
                                           for c in self.sprime.vel.components())))
        self.h.set_bottom_text("Notice", None)

    def setup_current_turn(self):
        self.sprime = self.s.update()
        self.calculate_future_states()
        #self.recenter()

    def next_turn(self):
        self.s = self.sprime
        self.missiles = []
        for mp in self.mprime:
            if mp.pos == self.s.pos:
                self.h.set_bottom_text(mp.id, None)
            else:
                self.missiles.append(mp)
        self.setup_current_turn()

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
                        self.calculate_future_states()
                    elif e.key == K_i or e.key == K_KP5:
                        self.sprime.command(5)
                        self.calculate_future_states()
                    elif e.key == K_u or e.key == K_KP7:
                        self.sprime.command(7)
                        self.calculate_future_states()
                    elif e.key == K_o or e.key == K_KP9:
                        self.sprime.command(9)
                        self.calculate_future_states()
                    elif e.key == K_j or e.key == K_KP4:
                        self.sprime.command(4)
                        self.calculate_future_states()
                    elif e.key == K_l or e.key == K_KP6:
                        self.sprime.command(6)
                        self.calculate_future_states()
                    elif e.key == K_RETURN or e.key == K_KP_ENTER:
                        self.next_turn()
                    elif e.key == K_x or e.key == K_KP0:
                        self.setup_current_turn()
                    elif e.key == K_F1:
                        self.setup_ship("Badger", self.badger_spec)
                        self.setup_current_turn()
                    elif e.key == K_F2:
                        self.setup_ship("Javelin", self.javelin_spec)
                        self.setup_current_turn()
                    elif e.key == K_F3:
                        self.setup_ship("Sparrowhawk", self.sparrowhawk_spec)
                        self.setup_current_turn()
                    elif e.key == K_F4:
                        self.setup_ship("Lone Wolf", self.lone_wolf_spec)
                        self.setup_current_turn()
                    elif e.key == K_F5:
                        self.add_missile(5, 1)
                        self.calculate_future_states()
                    elif e.key == K_F6:
                        self.add_missile(6, 1)
                        self.calculate_future_states()
                    elif e.key == K_F7:
                        self.add_missile(7, 1)
                        self.calculate_future_states()
                    elif e.key == K_F8:
                        self.add_missile(8, 1)
                        self.calculate_future_states()
                    elif e.key == K_F9:
                        self.add_missile(7, 0)
                        self.calculate_future_states()
                    elif e.key == K_F10:
                        self.add_missile(9, 0)
                        self.calculate_future_states()
                    elif e.key == K_F12:
                        self.recenter()
                    elif e.key == K_q or e.key == K_ESCAPE:
                        loop = False
                    else:
                        print("I don't recognize key: {0}".format(str(e.key)))

                except ThrustLimit:
                    self.h.set_bottom_text("Notice", "Thrust limit exceeded!")
                except GLimit:
                    self.h.set_bottom_text("Notice", "G limit exceeded!")
                except IllegalCommand:
                    self.h.set_bottom_text("Notice", "Illegal command for this fighter!")

            elif e.type == pygame.QUIT:
                loop = False
