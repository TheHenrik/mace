import xml.etree.ElementTree as ET

import numpy as np
from mace.domain import Plane, Wing, WingSegment


class PlaneParser:
    def __init__(self, file_name):
        self.plane = Plane()
        self.tree = ET.parse(f"./././data/planes/{file_name}")

    def build_plane(self):
        root = self.tree.getroot()
        self.plane.name = root.attrib["Name"]
        for element in root:
            if element.tag == "Fluegel":
                self.plane.wing = self.build_fluegel(element)
            elif element.tag == "Leitwerk":
                self.build_leitwerk(element)
        return self.plane

    def build_leitwerk(self, element):
        pass

    def build_fluegel(self, tree):
        wing = Wing()
        for element in tree:
            if element.tag == "Airfoil":
                wing.airfoil = element.text
            elif element.tag == "Fluegelsegment":
                if wing.segments is None:
                    wing.segments = []
                wing.segments.append(self.build_fluegelsegment(element))
        return wing

    def build_fluegelsegment(self, tree):
        segment = WingSegment()
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
