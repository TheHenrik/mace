import numpy as np

from mace.domain.plane import Plane, Wing, WingSegment


def calc_load(plane: Plane) -> Plane:
    wing = plane.wing
    return plane
