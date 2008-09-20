
# ship class

class Vec(object):
    def __init__(self, *value):
        if len(value) > 1:
            self.value = value
        else:
            self.value = value[0]

    def __add__(self, other):
        return Vec([i + j for i, j in zip(self.value, other.value)])

    def __sub__(self, other):
        return Vec([i - j for i, j in zip(self.value, other.value)])

    def __mul__(self, other):
        return Vec([i * other for i in self.value])

    def __rmul__(self, other):
        return Vec([other * i for i in self.value])

    def __div__(self, other):
        return Vec([i / other for i in self.value])

    def __len__(self):
        return len(self.value)

    def __str__(self):
        return str(self.value)
        

class Entity(object):
    def __init__(self, id, pos, vel, orientation):
        self.id = id
        self.pos = pos
        self.vel = vel
        self.orientation = orientation

    def update(self, thrust, rotation):
        self.pos += self.vel + thrust
        self.vel += thrust * 2
        self.orientation += rotation
        while self.orientation < 0:
            self.orientation += 6
        while self.orientation >= 6:
            self.orientation -= 6

    def __str__(self):
        return "(%d, %s, %s, %d)" % (self.id, str(self.pos), str(self.vel),
                                     self.orientation)

class Ship(Entity):
    def __init__(self, id, pos, vel, orientation,
                 thrust, thrusters, spinners):
        super(self, id, pos, vel, orientation)
        self.thrust = thrust
        self.thrusters = thrusters
        self.spinners = spinners
