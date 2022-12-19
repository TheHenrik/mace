from typing import List
from dataclasses import dataclass
from ..mass import MassTable

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


@dataclass 
class Profil():
    x: List(int) = None
    y: List(int) = None


@dataclass
class Coordinate():
    x: int = None
    y: int = None
    z: int = None

    def __add__(self, next):
        pass

    def __sub__(self, next):
        pass
    
    def __iter__(self):
        pass

    def getDistance(self, next):
        pass

@dataclass()
class Fluegelsegment():
    klappe: Klappe = None
    tiefe_links: int = None        # [m]
    tiefe_rechts: int = None       # [m]
    c_links: Coordinate = None
    c_rechts: Coordinate = None
    länge: int = None               # [m]
    profil: Profil = None


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
