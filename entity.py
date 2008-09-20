# entity.py

from __future__ import division

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
        return "Entity(%s, %s, %s, %s)" % (repr(self.id),
                                           repr(self.pos),
                                           repr(self.vel),
                                           repr(self.orientation))
