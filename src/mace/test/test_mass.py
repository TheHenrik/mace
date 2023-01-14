import unittest

import pytest

from mace.domain.plane import FlugzeugParser


class TestVector(unittest.TestCase):
    def setUp(self) -> None:
        self.plane = FlugzeugParser("flugzeug.xml").build_plane()

    def test_parser(self):
        assert self.plane is not None

    def test_zero_division(self):
        with pytest.raises(ZeroDivisionError):
            1 / 0


if __name__ == "__main__":
    unittest.main()
