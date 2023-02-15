from mace.domain.plane import Plane
from mace.mass.mass import get_mass_plane


def calculate_plane(plane: Plane):
    plane = get_mass_plane(plane)
    # plane = get_aero(plane)
    return plane
