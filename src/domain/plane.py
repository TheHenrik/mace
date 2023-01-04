from typing import List
from dataclasses import dataclass
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
    nose_inner: Vector = None
    nose_outer: Vector = None
    back_inner: Vector = None
    back_outer: Vector = None
    profile_name: str = None


@dataclass()
class TLeitwerk():
    hoehenleitwerk: List[Fluegelsegment] = None
    seitenleitwerk: List[Fluegelsegment] = None


@dataclass()
class VLeitwerk():
    leitwerk: List[Fluegelsegment] = None


@dataclass
class Leitwerktyp():
    typ: TLeitwerk|VLeitwerk = None


@dataclass()
class Fluegel():
    fluegelsegment: List[Fluegelsegment] = None


@dataclass()
class Flugzeug():
    name: str = None
    leitwerk: Leitwerktyp = None
    fluegel: Fluegel = None
    rumpf: Rumpf = None


class FlugzeugBuilder():
    def __init__(self, fluegel, leitwerk, rumpf):
        self.flugzeug = Flugzeug()
        self.flugzeug.fluegel = fluegel
        self.flugzeug.leitwerk = leitwerk
        self.flugzeug.rumpf = rumpf

    def get(self):
        return self.flugzeug
