# vpmath.py

from __future__ import division

# arbitrary dimensional vector
class Vec(object):
    def __init__(self, *value):
        if len(value) > 1:
            self.value = value
        else:
            self.value = value[0]

    def __eq__(self, other):
        return self.value == other.value

    def __ne__(self, other):
        return self.value != other.value

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

    def __abs__(self):
        return math.sqrt(sum(x*x for x in self.value))

    def __hash__(self):
        return hash(self.value)


class HexVec(object):
    def __init__(self, a=None, b=None, c=None):
        if a is None and b is None and c is None:
            a = 0
            b = 0
        elif a is None:
            a = -(b+c)
        elif b is None:
            b = -(a+c)

        self.a = a
        self.b = b

    @property
    def c(self):
        return -(self.a + self.b)

    def vector(self):
        #return Vec(self.a, self.b - self.c)
        return Vec(self.a, 2*self.b + self.a)

    @staticmethod
    def from_vector(vec):
        a = vec[0]
        #   y = b-c
        #   b = y+c
        #   b = y-(a+b)
        # 2*b = y-a
        #   b = (y-a)/2
        b = (vec[1]-a)/2

        ib = int(b)

        if b == ib:
            b = ib

        return HexVec(a, b)

    def __add__(self, other):
        return HexVec(self.a + other.a,
                      self.b + other.b)

    def __sub__(self, other):
        return HexVec(self.a - other.a,
                      self.b - other.b)

    def __mul__(self, scalar):
        return HexVec(self.a * scalar,
                      self.b * scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        return HexVec(self.a / scalar,
                      self.b / scalar)

    def __floordiv__(self, scalar):
        return (self / scalar).round()

    def __hash__(self):
        return hash((self.a, self.b))

    def __str__(self):
        return str((self.a, self.b, self.c))

    def __repr__(self):
        return "HexVec({0}, {1})".format(self.a, self.b)

    def __abs__(self):
        """Return the hex equivalent of the manhattan distance."""
        return max(abs(self.a), abs(self.b), abs(self.c))

    def components(self):
        """Return hex-aligned vectors which add up to this one.

        The return value value will be a list of [direction, distance] lists.
        There will be between zero and two elements in the list. If there are
        two, the directions will be adjacent to one another and the first
        distance will be greater than or equal to the second.
        """
        if self.a == 0 and self.b == 0:
            return []

        aa = abs(self.a)
        ab = abs(self.b)
        ac = abs(self.c)

        #print aa, ab, ac

        if aa >= ab and aa >= ac:
            if self.a > 0:
                #print "a+"
                components = [[Direction(1), ab],
                              [Direction(2), ac]]
            else:
                #print "a-"
                components = [[Direction(4), ab],
                              [Direction(5), ac]]
        elif ab >= aa and ab >= ac:
            if self.b > 0:
                #print "b+"
                components = [[Direction(3), ac],
                              [Direction(4), aa]]
            else:
                #print "b-"
                components = [[Direction(0), ac],
                              [Direction(1), aa]]
        else:
            if self.c > 0:
                #print "c+"
                components = [[Direction(5), aa],
                              [Direction(0), ab]]
            else:
                #print "c-"
                components = [[Direction(2), aa],
                              [Direction(3), ab]]

        #print components

        if components[0][1] < components[1][1]:
            components.reverse()

        #print components

        if components[1][1] == 0:
            del components[1]

        return components

    def round(self):
        if isinstance(self.a, int) and isinstance(self.b, int):
            return self

        ia = int(round(self.a))
        ib = int(round(self.b))
        ic = int(round(self.c))

        s = ia + ib + ic

        if s != 0:
            aa = abs(self.a-ia)
            ab = abs(self.b-ib)
            ac = abs(self.c-ic)

            if aa >= ab and aa >= ac:
                ia -= s
            elif ab >= aa and ab >= ac:
                ib -= s
            else: #ac > aa and ac > ab
                #ic -= s
                pass

        return HexVec(ia, ib)


# 6-way direction, has exactly six instances.
class Direction(object):
    _instances = [None] * 6
    
    def __new__(cls, val):
        val %= 6
        if cls._instances[val] is None:
            cls._instances[val] = object.__new__(cls)
            cls._instances[val].val = val

        return cls._instances[val]

    def __getnewargs__(self):
        return (self.val,)

    def inc(self):
        return Direction(self.val + 1)

    def dec(self):
        return Direction(self.val - 1)

    def __add__(self, amount):
        return Direction(self.val + amount)

    def __sub__(self, rhs):
        if isinstance(rhs, Direction):
            return (self.val - rhs.val + 2) % 6 - 2
        else:
            return Direction(self.val - amount)

    def __neg__(self):
        return Direction(self.val + 3)

    _unit_vectors = [Vec(0, -2),
                     Vec(1, -1),
                     Vec(1, 1),
                     Vec(0, 2),
                     Vec(-1, 1),
                     Vec(-1, -1)]
    def vector(self):
        return self._unit_vectors[self.val]

    _unit_hexvecs = [HexVec(0, -1),
                     HexVec(1, -1),
                     HexVec(1, 0),
                     HexVec(0, 1),
                     HexVec(-1, 1),
                     HexVec(-1, 0)]
    def hex_vector(self):
        return self._unit_hexvecs[self.val]

    def __repr__(self):
        return "Direction(%d)" % self.val

    _direction_names = ["North", "Northeast", "Southeast",
                        "South", "Southwest", "Northwest"]
    def __str__(self):
        return self._direction_names[self.val]

    def __hash__(self):
        return hash(self.val)
