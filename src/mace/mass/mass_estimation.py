from mace.mass.mesh import gen_profile, get_profil, mesh
from mace.domain.vehicle import Vehicle
from mace.domain.fuselage import Fuselage
from mace.domain.wing import Wing, WingSegment

from collections import defaultdict
import numpy as np


def estimate_mass_plane(plane: Vehicle):
    mass = defaultdict()
    weighted_cog = defaultdict()

    mass["main_wing"], weighted_cog["main_wing"] = \
        estimate_mass_wing(plane.wings["main_wing"])
    mass["h_stablizer"], weighted_cog["h_stabilizer"] = \
        estimate_mass_wing(plane.wings["horizontal_stabilizer"])
    mass["v_stabilizer"], weighted_cog["v_stabalizer"] = \
        estimate_mass_wing(plane.wings["vertical_stabilizer"])

    mass["fuselage"], weighted_cog["fuselage"] = \
        estimate_mass_fuselage(plane.fuselages["fuselage"])

    mass["landing_gear"], weighted_cog["landing_gear"] = \
        plane.landing_gear.mass, plane.landing_gear.center_of_gravity

    plane.mass = sum(mass.values())
    # TODO how does sum nparray work
    plane.center_of_gravity = sum(weighted_cog.values())/plane.mass
    return plane


def estimate_mass_wing(wing: Wing):
    masses = []
    cogs = []
    for segment in wing.segments:
        tmp_mass, tmp_cogs = estimate_mass_segment(segment)
        masses.append(tmp_mass)
        cogs.append(tmp_cogs)
    if not wing.spar is None:
        masses.append(wing.spar.mass) 
    mass = sum(masses)
    cog = sum(cogs)/mass
    return mass, cog


def estimate_mass_segment(segment: WingSegment):
    profil_innen, profil_außen = gen_profile(
        get_profil(segment.inner_airfoil),
        get_profil(segment.outer_airfoil),
        segment.nose_inner,
        segment.back_inner,
        segment.nose_outer,
        segment.back_outer,
    )
    area, volume = mesh(profil_innen, profil_außen)
    mass = segment.get_mass(volume, area)
    cog = np.array([0,0,0]) * mass
    return mass, cog


def estimate_mass_fuselage(fuselage: Fuselage):
    return 1, np.array([0,0,0])
