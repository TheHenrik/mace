import mace.aero.flightconditions.horizontalflight as horizontalflight
import numpy as np
from mace.domain.parser import PlaneParser
from mace.aero.implementations.avl.geometry_and_mass_files import GeometryFile, MassFile
from mace.aero.implementations.avl import athenavortexlattice
from mace.aero.implementations.viscousdrag import ViscousDrag
from mace.domain import params, Plane


class BuildMission:
    def __init__(self, plane: Plane):
        self.plane = plane

    def build_mission(self):
        # Horizontal Flight

        drag_over_v = horizontalflight.HorizontalFlight(self.plane).fv_diagramm(0.1, 1.1, step=0.1)





if __name__ == "__main__":
    testplane = PlaneParser("aachen.toml").get("Plane")
    cruise = BuildMission(testplane)
    cruise.build_mission()