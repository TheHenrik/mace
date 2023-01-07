import unittest

# import pytest
from mace.domain.vector import Vector, Vectorcalc


class TestVector(unittest.TestCase):
    def setUp(self) -> None:
        self.a = Vector(0, 1, 3)
        self.b = Vector(2, 4, 7)

    def test_add(self):
        sum = self.a + self.b
        self.assertEqual(sum, Vector(2, 5, 10))

    def test_true(self):
        self.assertTrue(True)


class TestVectorcalc(unittest.TestCase):
    def setUp(self) -> None:
        self.a = Vector(3, 4, 7)
        self.b = Vector(4, 25, 7)
        self.c = Vector(2, 6, 8)

    def test_dot(self):
        dot = Vectorcalc.dot(self.a, self.b)
        self.assertEqual(dot, 161.0)

    def test_cross(self):
        cross = Vectorcalc.cross(self.a, self.b)
        self.assertEqual(cross, Vector(-147, 7, 59))


if __name__ == "__main__":
    unittest.main()
