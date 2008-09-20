
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

    def __len__(self):
        return len(self.value)

    def __str__(self):
        return str(self.value)

class Orientation(object):
    values = [None] * 6
    unit_vectors = [Vec(0, 2),
                    Vec(1, 1),
                    Vec(1, -1),
                    Vec(0, -2),
                    Vec(-1, -1),
                    Vec(-1, 1)]
 
    @classmethod
    def get(cls, val):
        assert 0 <= val < 6
        if cls.values[val] is not None:
            return cls.values[val]
        else:
            return Orientation(val)
    
    def __init__(self, val):
        self.val = val
        Orientation.values[val] = self

    def inc(self):
        if self.val == 5:
            return Orientation.get(0)
        else:
            return Orientation.get(self.val + 1)

    def dec(self):
        if self.val == 0:
            return Orientation.get(5)
        else:
            return Orientation.get(self.val - 1)

    def __sub__(self, other):
        dif = self.val - other.val
        if dif > 3:
            dif -= 6
        elif dif <= -3:
            dif += 6

        return dif

    def vector(self):
        return Orientation.unit_vectors[self.val]

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
        return Entity(self.pos + vector, self.vel + vector*2,
                      self.orientation)

    def rotate(self, sign):
        assert sign <> 0
        if sign > 0:
            return Entity(self.pos, self.vel, self.orientation.inc())
        else:
            return Entity(self.pos, self.vel, self.orientation.dec())

    def update(self):
        return Entity(self.pos + self.vel, self.vel, self.orientation)

    def __str__(self):
        return "(%d, %s, %s, %s)" % (self.id, str(self.pos), str(self.vel),
                                     str(self.orientation))



class Ship(Entity):
    def __init__(self, id, pos, vel, orientation,
                 max_thrust, thrusters, spin_cost):
        Entity.__init__(self, id, pos, vel, orientation, used_thrust = 0)
        self.max_thrust = max_thrust
        self.thrusters = thrusters
        self.spin_cost = spin_cost
        self.used_thrust = used_thrust

    def __init__(self, e, max_thrust, thusters, spin_cost, used_thrust = 0):
        __init__(self, e.id, e.pos, e.vel, e.orientation,
                 max_thrust, thrusters, spin_cost, used_thrust)

    def thrust(self, direction):
        assert self.used_thrust < self.max_thrust
        return Ship(
        

    def command(self, c):
        assert 4 <= c <= 9
        if c == 8:
            assert self.thrusters == 1
            return self.thrust(orientation.vector())
