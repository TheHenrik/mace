import inspect
import tomllib

import numpy as np

from mace import domain


class PlaneParser:
    def __init__(self, path) -> None:
        with open(f"./././data/planes/{path}", "rb") as f:
            self.data = tomllib.load(f)
        self.classes = {
            key: val
            for key, val in globals()["domain"].__dict__.items()
            if inspect.isclass(val)
        }

    def get(self, obj):
        return self._rec_par(obj)

    def _rec_par(self, curr):
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
                sup.__dict__[obj] = self._wing_segments()
            elif val in self.classes:
                sup.__dict__[obj] = self._rec_par(val)
            else:
                sup.__dict__[obj] = val
        return sup

    # Works only if no segments on empenage
    def _wing_segments(self):
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
                    sup.__dict__[obj] = self._rec_par(val)
                else:
                    sup.__dict__[obj] = val
            segments.append(sup)
        return segments


if __name__ == "__main__":
    plane = PlaneParser("plane.toml").get()
    print(plane)
