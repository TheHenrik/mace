import xml.etree.ElementTree as ET

import numpy as np

from mace import domain
from mace.domain import plane


class TOMLParser:
    pass


class XMLParser:
    pass


class PlaneParser:
    def __init__(self, file_name):
        self.plane = None
        self.tree = ET.parse(f"./././data/planes/{file_name}")

    def get(self, obj):
        return self._rec_par(obj)

    def build_leitwerk(self, element):
        pass

    # Works only if no segments on empenage
    def _wing_segments(self):
        segments = []
        for segment in self.data["WingSegment"]:
            sup = plane.WingSegment()
            for obj in self.data["WingSegment"][segment]:
                if obj not in sup.__dict__:
                    raise ValueError(
                        f'Object {obj!r} not attribute of {self.classes["WingSegment"]}'
                    )
                val = self.data["WingSegment"][segment][obj]
                if type(val) is list:
                    sup.__dict__[obj] = np.array(val)
                elif obj == "segments":
                    sup.__dict__[obj] = self._wing_segments()
                elif val in self.classes:
                    sup.__dict__[obj] = self._rec_par(val)
                else:
                    sup.__dict__[obj] = val
            segments.append(sup)
        return segments


if __name__ == "__main__":
    plane = PlaneParser("testplane.toml").get("Plane")
    print(plane)