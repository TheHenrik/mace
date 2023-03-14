from mace.algo.calculate_plane import calculate_plane
from mace.domain.parser import PlaneParser
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
            self.planes.append(PlaneParser(plane_location).get())

    def calculate(self, verbose=False):
        planes = []
        for plane in self.planes:
            planes.append(calculate_plane(plane))
            if verbose:
                print(f"The weight of the plane is approx. {plane.mass} kg!")
        self.planes = planes

    def evaluate(self):
        pass

    def optimize(self):
        pass

    def benchmark(self):
        print(f"Size on Disk of Plane: {getsize(self)}")
        performance_time(10_000, calculate_plane, self.planes[0])
        performance_report(
            performance_time, 1_000, calculate_plane, self.planes[0], output=None
        )
