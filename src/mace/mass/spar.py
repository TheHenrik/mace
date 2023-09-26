import numpy as np

from mace.domain.plane import Plane, Wing, WingSegment


def max_weight(plane: Plane, load_case = 0):
    # Case with cargo == 0.7kg: 
    if load_case == 0:
        weight = (plane.mass + 0.7) * 9.81
    return weight


def calc_load(plane: Plane) -> Plane:
    main_wing = plane.wings["main_wing"]
    mass = 0
    for segment in main_wing.segments:
        mass += segment.span * 6 * 0.097
        a =0
    
    
    plane.mass += mass
    return plane
