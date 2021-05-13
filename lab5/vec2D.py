import math

class Vec2D:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __sub__(self, other):
        return Vec2D(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Vec2D(self.x + other.x, self.y + other.y)

    def is_less_eq_than(self, other):
        return self.x <= other.x and self.y <= other.y

    def is_more_eq_than(self, other):
        return self.x >= other.x and self.y >= other.y

    def times_scalar(self, scalar):
        return Vec2D(self.x * scalar, self.y * scalar)

    def is_small(self):
        return abs(self.x) <= 2 and abs(self.y) <= 2

    def get_distance_to(self, other):
        return math.sqrt((self.x + other.x) ** 2 + (self.y + other.y) ** 2)

    def to_tuple(self):
        return self.x, self.y

    def __str__(self):
        return f'({self.x},{self.y})'

    def __eq__(self, other):
        if isinstance(other, Vec2D):
            return self.x == other.x and self.y == other.y
        return NotImplemented

    def __hash__(self):
        return self.x * 2137 + self.y

