# vpmath.py

from __future__ import division

# arbitrary dimensional vector
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

    def __setitem__(self, index, value):
        self.value[index] = value

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "Vec(%s)" % repr(self.value)

    def __str__(self):
        return str(self.value)

    def __itr__(self):
        return itr(self.value)

    def magnitude(self):
        return math.sqrt(sum(x*x for x in self.value))

    def __hash__(self):
        return hash(self.value)
    
# 6-way direction, has exactly six instances.
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
        return Direction(self.val - 1) # small negative values are ok

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

    _direction_names = ["North", "Northeast", "Southeast",
                        "South", "Southwest", "Northwest"]
    def __str__(self):
        return self._direction_names[self.val]

    def __hash__(self):
        return hash(self.val)

class HexVec(object):
    def __init__(self, lst = None, **kwargs):
        if lst is None:
            self.components = [0] * 6
        else:
            self.components = lst[:]
            
        for dir, magnitude in kwargs.iteritems():
            self.components[dir.value] += magnitude

    def simplify(self):
        loop = True
        while loop:
            loop = False
            for d in range(3):
                m = min(self.components[d], self.components[d-3])
                if m > 0:
                    self.components[d] -= m
                    self.components[d-3] -= m

            for d in range(6):
                m = min(self.components[d], self.components[d-2])
                if m > 0:
                    self.components[d-1] += m
                    self.components[d] -= m
                    self.components[d-2] -= m
                    loop = True
                    break
            
    def vector(self):
        if self.direction is None:
            return Vec(0, 0)
        else:
            return self.direction.vector() * self.distance
        
    def __add__(self, other):
        if self.direction == other.direction:
            return 1, HexVec(self.direction, self.distance + other.distance)
        elif abs(self.direction - other.direction) == 1:
            if self.distance >= other.distance:
                return 2, (self, other)
            else:
                return 2, (other, self)
        elif self.direction - other.direction == 3:
            d = self.distance - other.distance
            if d == 0:
                return 0, None
            elif d > 0:
                return 1, HexVec(self.direction, d)
            else:
                return 1, HexVec(other.direction, -d)
        elif self.direction - other.direction == 2:
            dir = self.direction.dec()
            d = self.distance - other.distance
            if d > self.distance / 2:
                return 2, (HexVec(self.direction, d),
                           HexVec(dir, other.distance))
            elif d > 0:
                return 2, (HexVec(dir, other.distance),
                           HexVec(self.direction, d))
            elif d == 0:
                return 1, HexVec(dir, self.distance)
            elif d > -other.distance / 2:
                return 2, s

    def __init__(self, dir1, dist1, dir2 = None, dist2 = 0):
        self.dir1 = dir1
        self.dist1 = dist1
        self.dir2 = dir2
        self.dist2 = dist2

    def vector(self):
        if dir2 is not None:
            return self.dir1.vector() * dist1 + self.dir2.vector() * dist2
        else:
            return self.dir1.vector() * dist1

    def __add__(self, other):
        components = {self.dir1 : self.dist1}
        if self.dir2 is not None:
            components[self.dir2] = self.dist2
        
        if components.has_key(other.dir1):
            components[other.dir1] += other.dist1
        else:
            components[other.dir1] = other.dist1

        if other.dir2 is not None:
            if components.has_key(other.dir1):
                components[other.dir2] += other.dist2
            else:
                components[other.dir2] = other.dist2

        keys = components.keys()
        while len(keys) >= 2:
            d1 = keys.pop()
            for d2 in keys:
                if d1 - d2 == 3:
                    if components[d1] >= components[d2]:
                        components[d1] -= components[d2]
                        components[d2] = 0
                    else:
                        components[d2] -= components[d1]
                        components[d1] = 0
                    break

        
