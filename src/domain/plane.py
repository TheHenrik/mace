from typing import List
from dataclasses import dataclass


@dataclass
class RumpfProfil():
    höhe: int = None                # [m]
    breite: int = None              # [m]
    position: int = None            # [ ]


@dataclass
class Rumpf():
    laenge: int = None              # [m]
    profile: RumpfProfil = None


@dataclass()
class Klappe():
    tiefe_links: int = None         # [m]
    tiefe_rechts: int = None        # [m]


@dataclass()
class Fluegelsegment():
    klappe: Klappe = None
    breite_links: int = None        # [m]
    breite_rechts: int = None       # [m]
    delta_rechts: int = None        # [m]
    länge: int = None               # [m]


@dataclass()
class Leitwerk():
    fluegel: List[Fluegelsegment] = None


@dataclass()
class Fluegel():
    fluegelsegment: List[Fluegelsegment] = None


@dataclass()
class Flugzeug():
    leitwerk: Leitwerk = None
    fluegel: Fluegel = None
    rumpf: Rumpf = None


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




