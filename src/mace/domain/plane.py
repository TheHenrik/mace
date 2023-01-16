import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class RumpfProfil:
    höhe: int = None
    breite: int = None
    position: int = None


@dataclass
class Rumpf:
    laenge: int = None
    profile: RumpfProfil = None
    mass: float = 0


@dataclass()
class Klappe:
    tiefe_links: int = None
    tiefe_rechts: int = None


@dataclass()
class Fluegelsegment:
    nose_inner: np.ndarray = None
    nose_outer: np.ndarray = None
    back_inner: np.ndarray = None
    back_outer: np.ndarray = None


@dataclass()
class TLeitwerk:
    hoehenleitwerk: List[Fluegelsegment] = None
    airfoilhl: str = None
    seitenleitwerk: List[Fluegelsegment] = None
    airfoilsl: str = None
    mass: float = 0


@dataclass()
class VLeitwerk:
    leitwerk: List[Fluegelsegment] = None
    airfoil = None
    mass: float = 0


@dataclass
class Leitwerktyp:
    typ: TLeitwerk | VLeitwerk = None


@dataclass()
class Fluegel:
    fluegelsegment: List[Fluegelsegment] = None
    airfoil: str = None
    mass: float = 0


@dataclass()
class Flugzeug:
    name: str = None
    leitwerk: Leitwerktyp = None
    fluegel: Fluegel = None
    rumpf: Rumpf = None
    mass: float = 0


class FlugzeugParser:
    def __init__(self, file_name):
        self.flugzeug = Flugzeug()
        self.tree = ET.parse(f"./././data/planes/{file_name}")

    def build_plane(self):
        root = self.tree.getroot()
        self.flugzeug.name = root.attrib["Name"]
        for element in root:
            if element.tag == "Fluegel":
                self.flugzeug.fluegel = self.build_fluegel(element)
            elif element.tag == "Leitwerk":
                self.build_leitwerk(element)
        return self.flugzeug

    def build_leitwerk(self, element):
        pass

    def build_fluegel(self, tree):
        fluegel = Fluegel()
        for element in tree:
            if element.tag == "Airfoil":
                fluegel.airfoil = element.text
            elif element.tag == "Fluegelsegment":
                if fluegel.fluegelsegment is None:
                    fluegel.fluegelsegment = []
                fluegel.fluegelsegment.append(self.build_fluegelsegment(element))
        return fluegel

    def build_fluegelsegment(self, tree):
        segment = Fluegelsegment()
        for element in tree:
            if element.tag == "NaseInnen":
                segment.nose_inner = self.build_vector(element)
            elif element.tag == "NaseAußen":
                segment.nose_outer = self.build_vector(element)
            elif element.tag == "BackInner":
                segment.back_inner = self.build_vector(element)
            elif element.tag == "BackOuter":
                segment.back_outer = self.build_vector(element)
        return segment

    def build_vector(self, element):
        return np.array(
            list(map(float, [element[0].text, element[1].text, element[2].text]))
        )
