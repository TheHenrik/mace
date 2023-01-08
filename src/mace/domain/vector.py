import numpy as np


class Vector:
    def __init__(self, x, y, z) -> None:
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)

    def __repr__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"

    def __eq__(self, next: "Vector|int") -> bool:
        if self.x == next.x and self.y == next.y and self.z == next.z:
            return True
        return False

    def __hash__(self) -> int:
        return hash((self.x, self.y, self.z))

    def __add__(self, next: "Vector|float") -> "Vector":
        if type(next) is type(self):
            x = self.x + next.x
            y = self.y + next.y
            z = self.z + next.z
        else:
            x = self.x + next
            y = self.y + next
            z = self.z + next
        return Vector(x, y, z)

    def __sub__(self, next: "Vector|float") -> "Vector":
        if type(next) is type(self):
            x = self.x - next.x
            y = self.y - next.y
            z = self.z - next.z
        else:
            x = self.x - next
            y = self.y - next
            z = self.z - next
        return Vector(x, y, z)

    def __mul__(self, next: "Vector|float") -> "Vector":
        if type(next) is type(self):
            x = self.x * next.x
            y = self.y * next.y
            z = self.z * next.z
        else:
            x = self.x * next
            y = self.y * next
            z = self.z * next
        return Vector(x, y, z)

    def __truediv__(self, next: "Vector|float") -> "Vector":
        if type(next) is type(self):
            x = self.x / next.x
            y = self.y / next.y
            z = self.z / next.z
        else:
            x = self.x / next
            y = self.y / next
            z = self.z / next
        return Vector(x, y, z)

    def __floordiv__(self, next: "Vector|float") -> "Vector":
        if type(next) is type(self):
            x = self.x // next.x
            y = self.y // next.y
            z = self.z // next.z
        else:
            x = self.x // next
            y = self.y // next
            z = self.z // next
        return Vector(x, y, z)

    def __iadd__(self, next: "Vector|float") -> None:
        if type(next) is type(self):
            self.x += next.x
            self.y += next.y
            self.z += next.z
        else:
            self.x += next
            self.y += next
            self.z += next
        return self

    def __isub__(self, next: "Vector|float") -> None:
        if type(next) is type(self):
            self.x -= next.x
            self.y -= next.y
            self.z -= next.z
        else:
            self.x -= next
            self.y -= next
            self.z -= next
        return self

    def __imul__(self, next: "Vector|float") -> None:
        if type(next) is type(self):
            self.x *= next.x
            self.y *= next.y
            self.z *= next.z
        else:
            self.x *= next
            self.y *= next
            self.z *= next
        return self

    def __itruediv__(self, next: "Vector|float") -> None:
        if type(next) is type(self):
            self.x /= next.x
            self.y /= next.y
            self.z /= next.z
        else:
            self.x /= next
            self.y /= next
            self.z /= next
        return self

    def __ifloordiv__(self, next: "Vector|float") -> None:
        if type(next) is type(self):
            self.x //= next.x
            self.y //= next.y
            self.z //= next.z
        else:
            self.x //= next
            self.y //= next
            self.z //= next
        return self

    def __abs__(self) -> float:
        return np.sqrt(self.x**2 + self.y**2 + self.z**2)

    __radd__ = __add__
    __rmul__ = __mul__


class Vectorcalc:
    def cross(first: Vector, second: Vector) -> Vector:
        x = first.y * second.z - first.z * second.y
        y = first.z * second.x - first.x * second.z
        z = first.x * second.y - first.y * second.x
        return Vector(x, y, z)

    def dot(first: Vector, second: Vector) -> float:
        x = first.x * second.x
        y = first.y * second.y
        z = first.z * second.z
        return x + y + z

    def tri_volume(first: Vector, second: Vector, third: Vector) -> float:
        """V = <a⨯b, c>*1/6"""
        return Vectorcalc.dot(Vectorcalc.cross(first, second), third) / 6

    def tri_area(first: Vector, second: Vector, third: Vector) -> float:
        return abs(Vectorcalc.cross(second - first, third - first)) / 2
