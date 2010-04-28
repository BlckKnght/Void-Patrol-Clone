# vpmath.py

from __future__ import division

# 6-way direction, has exactly six instances.
class Direction(object):
    _instances = [None] * 6

    def __new__(cls, value):
        value %= 6
        if cls._instances[value] is None:
            cls._instances[value] = object.__new__(cls)
            cls._instances[value].value = value

        return cls._instances[value]

    def __getnewargs__(self):
        return (self.value,)

    def __add__(self, amount):
        """Return the direction rotated clockwise by amount."""
        return Direction(self.value + amount)

    def __sub__(self, rhs):
        """Do subtraction. This can have two different meanings.

        If 'rhs' is another direction, return the turns needed to go from
        'self' to 'rhs'.

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
        return "Direction(%d)" % self.value

    _direction_names = ["North", "Northeast", "Southeast",
                        "South", "Southwest", "Northwest"]
    def __str__(self):
        return self._direction_names[self.value]

    def __hash__(self):
        return hash(self.value)


# arbitrary dimensional vector
class Vec(object):
    _unit_vectors = [(0, -2),
                     (1, -1),
                     (1, 1),
                     (0, 2),
                     (-1, 1),
                     (-1, -1)]

    def __init__(self, x=0, y=0):
        if isinstance(x, (int, float)):
            self.x = x
            self.y = y
        elif isinstance(x, Vec):
            self.x = x.x
            self.y = x.y
        elif isinstance(x, (tuple, list)):
            self.x, self.y = x
        elif isinstance(x, HexVec):
            self.x = x.a
            self.y = x.b - x.c
        elif isinstance(x, Direction):
            self.x, self.y = self._unit_vectors[x.value]
        else:
            raise TypeError("Can't build a Vec from arguments: %s" %
                            repr((x, y)))

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
        return Vec(self.x + scalar, self.y + scalar)

    __rmul__ = __mul__

    def __truediv__(self, scalar):
        return Vec(self.x / scalar, self.y / scalar)

    __div__ = __truediv__

    def __getitem__(self, index):
        return [self.x, self.y][index]

    def __len__(self):
        return 2

    def __repr__(self):
        return "Vec(%s, %s)" % (self.x, self.y)

    def __str__(self):
        return str((self.x, self.y))

    def __itr__(self):
        yield x
        yield y

    def __abs__(self):
        return math.sqrt(x*x + y*y)

    def __hash__(self):
        return hash((self.x, self.y))

class HexVec(object):
    _unit_hexvecs = [(0, -1),
                     (1, -1),
                     (1, 0),
                     (0, 1),
                     (-1, 1),
                     (-1, 0)]

    def __init__(self, a=None, b=None, c=None):
        if a is None and b is None and c is None:
            self.a = 0
            self.b = 0
        elif a is None:
            self.a = -(b+c)
            self.b = b
        elif isinstance(a, (int, float)):
            if b is None:
                b = -(a+c)
            self.a = a
            self.b = b
        elif isinstance(a, Vec):
            self.a = a.x
            self.b = type(a.x)((a.y - a.x) / 2)
        elif isinstance(a, Direction):
            self.a, self.b = self._unit_hexvecs[a.value]
        else:
            raise TypeError("Can't build a HexVec from arguments: %s" %
                            (repr((a, b, c))))

    @property
    def c(self):
        return -(self.a + self.b)

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
            components = [[Direction(1), -self.b],
                          [Direction(2), -self.c]]
        elif ab >= aa and ab >= ac:
            components = [[Direction(3), -self.c],
                          [Direction(4), -self.a]]
        else: # ac is largest
            components = [[Direction(5), -self.a],
                          [Direction(0), -self.b]]

        if components[0][1] < 0:
            components[0] = [v for v in components[0]]

        if components[1][1] < 0:
            components[1] = [v for v in components[1]]

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
