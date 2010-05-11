# vpmath.py

from __future__ import division

# 6-way direction, has exactly six instances.
class Direction(object):
    __slots__ = "_value"

    _instances = [None] * 6

    def __new__(cls, value):
        assert isinstance(value, int)
        value = (value + 2) % 6 - 2
        if cls._instances[value] is None:
            cls._instances[value] = object.__new__(cls)
            cls._instances[value]._value = value

        return cls._instances[value]

    @property
    def value(self):
        return self._value

    def __getnewargs__(self):
        return (self.value,)

    def __add__(self, amount):
        """Return the direction rotated clockwise by amount."""
        return Direction(self.value + amount)

    def __sub__(self, rhs):
        """Do subtraction. This can have two different meanings.

        If 'rhs' is another direction, return the turns needed to go from
        'self' to 'rhs', in the range of -2 to 3.

        If 'rhs' is an integer, return this direction rotated counter-
        clockwise by that amount."""
        if isinstance(rhs, Direction):
            return (self.value - rhs.value + 2) % 6 - 2
        else:
            return Direction(self.value - rhs)

    def __neg__(self):
        """Return the opposite direction."""
        return Direction(self.value + 3)

    def __repr__(self):
        return "Direction({0})".format(self.value)

    _direction_names = ["North", "Northeast", "Southeast",
                        "South", "Southwest", "Northwest"]
    def __str__(self):
        return self._direction_names[self.value]

    def __hash__(self):
        return hash(self.value)


# two dimensional vector
class Vec(object):
    __slots__ = ["_x", "_y"]

    _unit_vectors = [(0, -2),
                     (1, -1),
                     (1, 1),
                     (0, 2),
                     (-1, 1),
                     (-1, -1)]

    def __new__(cls, *values):
        vec = object.__new__(cls)
        if len(values) == 2:
            vec._x, vec._y = values
        elif len(values) == 0:
            vec._x = 0
            vec._y = 0
        elif isinstance(values[0], (Vec, tuple, list)):
            vec._x, vec._y = values[0]
        elif isinstance(values[0], HexVec):
            vec._x = values[0].a
            vec._y = values[0].b - values[0].c
        elif isinstance(values[0], Direction):
            vec._x, vec._y = cls._unit_vectors[values[0].value]
        else:
            raise TypeError("Can't build a Vec from arguments: {0}".format(
                            repr(values)))

        return vec

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __eq__(self, other):
        if not isinstance(other, Vec):
            other = Vec(other)

        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        if not isinstance(other, Vec):
            other = Vec(other)

        return self.x != other.x or self.y != other.y

    def __add__(self, other):
        if not isinstance(other, Vec):
            other = Vec(other)

        return Vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Vec):
            other = Vec(other)

        return Vec(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vec(self.x * scalar, self.y * scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        return Vec(self.x / scalar, self.y / scalar)

    __div__ = __truediv__

    def __getitem__(self, index):
        return [self.x, self.y][index]

    def __len__(self):
        return 2

    def __repr__(self):
        return "Vec({0}, {1})".format(self.x, self.y)

    def __str__(self):
        return str((self.x, self.y))

    def __itr__(self):
        yield self.x
        yield self.y

    def __abs__(self):
        return math.sqrt(x*x + y*y)

    def __hash__(self):
        return hash((self.x, self.y))

class HexVec(object):
    __slots__ = "_a", "_b"
    _unit_hexvecs = [(0, -1),
                     (1, -1),
                     (1, 0),
                     (0, 1),
                     (-1, 1),
                     (-1, 0)]

    def __new__(cls, *values):
        hv = object.__new__(cls)
        if len(values) == 2:
            hv._a, hv._b = values
        elif len(values) == 0:
            hv._a = 0
            hv._b = 0
        elif isinstance(values[0], (list, tuple)):
            hv._a, hv._b = values[0]
        elif isinstance(values[0], Vec):
            hv._a = values[0].x
            hv._b = type(hv._a)((values[0].y - values[0].x) / 2)
        elif isinstance(values[0], Direction):
            hv._a, hv._b = cls._unit_hexvecs[values[0].value]
        else:
            raise TypeError("Can't build a HexVec from arguments: {0}".format(
                            repr(values)))

        return hv

    @property
    def a(self):
        return self._a

    @property
    def b(self):
        return self._b

    @property
    def c(self):
        return -(self._a + self._b)

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

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def __ne__(self, other):
        return self.a != other.a or self.b != other.b

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
            components = [[Direction(1), -self.b],
                          [Direction(2), -self.c]]
        elif ab >= aa and ab >= ac:
            components = [[Direction(3), -self.c],
                          [Direction(4), -self.a]]
        else: # ac is largest
            components = [[Direction(5), -self.a],
                          [Direction(0), -self.b]]

        if components[0][1] < 0:
            components[0] = [-v for v in components[0]]

        if components[1][1] < 0:
            components[1] = [-v for v in components[1]]

        if components[0][1] < components[1][1]:
            components.reverse()

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
