import inspect
import tomllib
import xml.etree.ElementTree as ET

import numpy as np

from mace import domain


class PlaneParser:
    def __init__(self, path) -> None:
        with open(f"./././data/planes/{path}", "rb") as f:
            self.data = tomllib.load(f)
        glb = globals()["domain"].__dict__
        self.classes = {clas: glb[clas] for clas in glb if inspect.isclass(glb[clas])}

    def get(self):
        return self.rec_par("Plane")

    def rec_par(self, curr):
        sup = self.classes[curr]()
        for obj in self.data[curr]:
            if obj not in sup.__dict__:
                raise ValueError(
                    f"Object {obj!r} not attribute of {self.classes[curr]}"
                )
            val = self.data[curr][obj]
            if type(val) is list:
                sup.__dict__[obj] = np.array(val)
            elif obj == "segments":
                sup.__dict__[obj] = self.wing_segments()
            elif val in self.classes:
                sup.__dict__[obj] = self.rec_par(val)
            else:
                sup.__dict__[obj] = val
        return sup

    def wing_segments(self):
        segments = []
        for segment in self.data["WingSegment"]:
            sup = domain.WingSegment()
            for obj in self.data["WingSegment"][segment]:
                if obj not in sup.__dict__:
                    raise ValueError(
                        f'Object {obj!r} not attribute of {self.classes["WingSegment"]}'
                    )
                val = self.data["WingSegment"][segment][obj]
                if type(val) is list:
                    sup.__dict__[obj] = np.array(val)
                elif obj == "segments":
                    sup.__dict__[obj] = self.wing_segments()
                elif val in self.classes:
                    sup.__dict__[obj] = self.rec_par(val)
                else:
                    sup.__dict__[obj] = val
            segments.append(sup)
        return segments


if __name__ == "__main__":
    plane = PlaneParser("plane.toml").get()
    print(plane)
