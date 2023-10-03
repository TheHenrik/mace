import numpy as np

from mace.domain.plane import Plane, Wing, WingSegment

def max_weight(plane: Plane, load_case = 0):
    # Case with cargo == 0.7kg: 
    if load_case == 0:
        weight = (plane.mass + 0.7) * 9.81
    return weight


def moment_at_position(mass: float, position: float, half_wing_span: float):
    moment = (half_wing_span - position) * mass * 10
    if position < 0.1 * half_wing_span:
        moment *= 1.2
    return moment
    

def get_rovings(segment: WingSegment, total_mass: float, plane_half_wing_span):
    max_height = segment.inner_chord * 0.05
    D100 =  moment_at_position(total_mass, segment.nose_inner[1], plane_half_wing_span)
    sigma = 700/(1_000**2)
    H100 = D100/sigma
    C100 = 10/1_000
    G100 = max_height-0.4/1_000
    J100 = np.cbrt(((C100*(G100**3))-(6*G100*H100))/C100)
    K100 = (G100-J100)/2
    m = K100 * C100 * 10
    n = np.ceil(m)
    return n


def calc_load(plane: Plane) -> Plane:
    main_wing: Wing = plane.wings["main_wing"]
    half_wing_span = main_wing.segments[-1].nose_outer[1]
    mass = 0
    for segment in main_wing.segments:
        rovings_count = get_rovings(segment, plane.mass, half_wing_span)
        mass += segment.span * rovings_count * 0.01
    
    plane.mass += 2 * mass
    return plane
