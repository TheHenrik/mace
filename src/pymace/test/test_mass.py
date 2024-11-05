import unittest

import pytest

from pymace.domain.parser import PlaneParser


class TestMassCalc(unittest.TestCase):
    def setUp(self) -> None:
        self.plane = PlaneParser("flugzeug.xml").build_plane()

    def test_parser(self):
        assert self.plane is not None

    def test_zero_division(self):
        with pytest.raises(ZeroDivisionError):
            1 / 0


if __name__ == "__main__":
    unittest.main()
