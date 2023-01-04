from typing import List
from dataclasses import dataclass
from mass import MassTable
from vector import Vector

@dataclass
class RumpfProfil():
    höhe: int = None
    breite: int = None
    position: int = None


@dataclass
class Rumpf():
    laenge: int = None
    profile: RumpfProfil = None


@dataclass()
class Klappe():
    tiefe_links: int = None
    tiefe_rechts: int = None


@dataclass()
class Fluegelsegment():
    klappe: Klappe = None
    tiefe_links: int = None
    tiefe_rechts: int = None
    c_links: Vector = None
    c_rechts: Vector = None
    profil: str = None


@dataclass()
class Leitwerk():
    fluegel: List[Fluegelsegment] = None


@dataclass()
class Fluegel():
    fluegelsegment: List[Fluegelsegment] = None


@dataclass()
class Flugzeug():
    name: str = None
    leitwerk: Leitwerk = None
    fluegel: Fluegel = None
    rumpf: Rumpf = None
    mass: MassTable = None


class FlugzeugBuilder():
    def __init__(self):
        self.flugzeug = Flugzeug()

    def leitwerk(self, leitwerk):
        self.flugzeug.leitwerk = leitwerk

        return self

    def fluegel(self, fluegel):
        self.fluegel = fluegel

        return self

    def rumpf(self, rumpf):
        self.rumpf = rumpf

        return self

    def get(self):
        return self.flugzeug


class LeitwerkBuilder():
    def __init__(self):
        self.leitwerk = Leitwerk()

    def addFluegelsegment(self, fluegelsegment):
        if self.leitwerk.fluegelsegment is None:
            self.leitwerk.fluegelsegment = list()
        self.leitwerk.fluegelsegment.append(fluegelsegment)

        return self

    def get(self):
        return self.leitwerk


class FluegelBuilder():
    def __init__(self):
        self.fluegel = Fluegel()

    def addFluegelsegment(self, fluegelsegment):
        if self.fluegel.fluegelsegment is None:
            self.fluegel.fluegelsegment = list()
        self.fluegel.fluegelsegment.append(fluegelsegment)

        return self

    def get(self):
        return self.fluegel
