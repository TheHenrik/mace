import re
from functools import cache
from operator import attrgetter

import numpy as np

from mace.domain.plane import Fluegel, Fluegelsegment, Flugzeug, Leitwerktyp, TLeitwerk
from mace.mass.mesh import gen_profile, get_profil, mesh

class GetMass:
    def __init__(self, *args) -> int:
        self.mass = 0.0
        for arg in args:
            if type(arg) is Flugzeug:
                self.aircraft(arg)
    
    def wing(self, wing: Fluegel):
        self.segments(wing.fluegelsegment, wing.airfoil)

    def empennage(self, empennage: Leitwerktyp):
        if type(empennage.typ) is TLeitwerk:
            self.segments(empennage.typ.hoehenleitwerk, empennage.typ.airfoilhl)
            self.segments(empennage.typ.seitenleitwerk, empennage.typ.airfoilsl)

    def segments(self, segments: list[Fluegelsegment], profil_name: str):
        profil = get_profil(profil_name)

        for segment in segments:
            profil_innen, profil_außen = gen_profile(
                profil,
                segment.nose_inner,
                segment.back_inner,
                segment.nose_outer,
                segment.back_outer,
            )

            area, volume = mesh(profil_innen, profil_außen)
            self.mass += area * 1
            self.mass += volume * 10_000

    def aircraft(self, aircraft: Flugzeug):
        if not aircraft.fluegel == None:
            self.wing(aircraft.fluegel)
        if not aircraft.leitwerk == None:
            self.empennage(aircraft.leitwerk)
