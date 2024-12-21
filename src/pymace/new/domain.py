from functools import partial
from pathlib import Path

from pymace.new.geometries import Geometrie
from pymace.new.properties import Properties
from pymace.new.analysis import Analysis
from pymace.new.aero import Aero




class Plane:
    analysis: list[Analysis]
    geometry: Geometrie
    properties: Properties

    def __new__(cls, pth: Path):
        if pth.suffix == ".xml":
            return Plane.import_(pth)
        elif pth.suffix == ".pkl":
            return Plane.load(pth)
        elif pth.suffix is None:
            return super(Plane, cls).__new__(cls)
        else:
            raise ValueError(f"Unsupported file extension: {pth.suffix}")
        
        
    def __init__(self, pth: Path, aero: Aero):
        self.aero = aero

    def aero(self, *args, methode="ml", **kwargs): 
        """
        Calculate aerodynamic properties.
        Possible methods: ML, AVLXFOIL (default: ML).
        Own additional methods can be added or existing ones can be overwritten.
        """

    def structure(self): ...
    def propeller(self): ...
    def export(self): ...
    def import_(cls, pth: Path):
        instance = super(Plane, cls).__new__(cls)
        instance.__init__(pth, Aero())
        return instance

    def evaluate(self): ...
    def mutate(self): ...
    def mission(self): ...
    def save(self): ...
    def load(cls, pth: Path):
        instance = super(Plane, cls).__new__(cls)
        instance.__init__(pth, Aero())
        return instance

    def par_mutate(self, *func: tuple[callable], core_count=1, iter=1_000): ...


def main():
    pth = Path("path/to/plane.xml")
    plane = Plane(pth)

    while plane.properties.mass < 1000:
        plane.aero(methode="ml")
        plane.structure()
        plane.mutate(key="mass")

    plane.par_mutate(
        partial(plane.aero, methode="avlxfoil"),
        plane.structure,
        plane.propeller,
        plane.mission,
        plane.evaluate,
        partial(plane.export, pth="path/to/output/folder/"),
        core_count=8,
        iter=10_000
    )
    plane.save()


if __name__ == "__main__":
    main()
