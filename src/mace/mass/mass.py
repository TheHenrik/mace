import re
from functools import cache
from operator import attrgetter

from mace.domain.vector import Vector, Vectorcalc
from mace.domain.plane import Fluegel, Fluegelsegment, Flugzeug, Leitwerktyp, TLeitwerk


class Calcmass:
    mass: float = None

    def __init__(self, arg) -> None:
        if type(arg) is Flugzeug:
            self.plane(arg)
        else:
            raise ValueError

    def plane():
        pass

    def wing():
        pass

    def segment():
        pass

    def empannage():
        pass
