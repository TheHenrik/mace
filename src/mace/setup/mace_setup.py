from mace.domain.parser import PlaneParser
from mace.domain.plane import Plane
from mace.setup.airfoils import populate_airfoils


class Project:
    planes: list[Plane] = None
    eval: dict = None


class ProjectSetup(Project):
    def __init__(self, eval: str = None, planes_location: list[str] = None) -> None:
        populate_airfoils()
        self.planes = []
        for plane_location in planes_location:
            self.planes.append(PlaneParser(plane_location).build_plane())
