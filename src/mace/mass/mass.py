# Absolete


from mace.domain.plane import Plane
from mace.mass.mass_estimation import estimate_mass_plane
from mace.mass.spar import calc_load


def get_mass_plane(plane: Plane):
    plane = estimate_mass_plane(plane)
    plane = calc_load(plane)
    plane = calc_load(plane)
    # plane = estimate_mass_plane(plane)
    return plane
