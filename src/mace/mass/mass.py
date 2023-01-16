from mace.domain.plane import Plane
from mace.mass.mass_estimation import estimate_mass_plane


def get_mass_plane(plane: Plane):
    plane = estimate_mass_plane(plane)
    return plane
