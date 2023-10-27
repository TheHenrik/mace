import logging

from mace.domain.parser import TOMLParser
from mace.domain.plane import Plane
from mace.setup.airfoils import populate_airfoils
from mace.test import getsize, performance_report, performance_time


class Project:
    planes: list[Plane] = None
    eval: dict = None

    def __init__(self, eval: str = None, planes_location: list[str] = None) -> None:
        populate_airfoils()
        self.planes = []
        for plane_location in planes_location:
            self.planes.append(TOMLParser(plane_location).get("Plane"))

    def calculate(self, verbose=False):
        pass

    def evaluate(self):
        pass

    def optimize(self):
        pass

    def benchmark(self):
        logging.debug(f"Size on Disk of Plane: {getsize(self)}")
        performance_time(10_000, print, self.planes[0])
        performance_report(performance_time, 1_000, print, self.planes[0], output=None)
