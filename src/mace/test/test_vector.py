import unittest
#import pytest
from mace.domain.vector import Vector

class TestVector(unittest.TestCase):
    def setUp(self) -> None:
        self.a = Vector(0,1,3)
        self.b = Vector(2,4,7)

    def test_add(self):
        sum = self.a + self.b
        self.assertEqual(sum, Vector(2,5,10))

    def test_true(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()