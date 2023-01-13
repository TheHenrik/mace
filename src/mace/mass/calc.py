import re
from functools import cache
from operator import attrgetter

import numpy as np

from mace.domain.plane import Fluegel, Fluegelsegment, Flugzeug, Leitwerktyp, TLeitwerk
from mace.mass.mesh import gen_profile, get_profil, mesh


def get_mass_wing(wing: Fluegel):
    mass = 0
    profil = get_profil(wing.airfoil)

    for segment in wing.fluegelsegment:
        profil_innen, profil_außen = gen_profile(
            profil,
            segment.nose_inner,
            segment.back_inner,
            segment.nose_outer,
            segment.back_outer,
        )

        area, volume = mesh(profil_innen, profil_außen)
        mass += area * 1
        mass += volume * 10_000

    return mass


def get_mass_empennage(empennage: Leitwerktyp):
    mass = 0
    if type(empennage.typ) is TLeitwerk:
        segments = empennage.typ.hoehenleitwerk
    profil = get_profil(empennage.typ.hoehenleitwerk)

    for segment in segments:
        profil_innen, profil_außen = gen_profile(
            profil,
            segment.nose_inner,
            segment.back_inner,
            segment.nose_outer,
            segment.nose_outer,
        )

        area, volume = mesh(profil_innen, profil_außen)
        mass += area * 1
        mass += volume * 10_000

    return mass


def get_mass_aircraft(aircraft: Flugzeug):
    mass = 0
    mass += get_mass_wing(aircraft.fluegel)
    # mass += get_mass_empennage(aircraft.leitwerk)

    return mass
