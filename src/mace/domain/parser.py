import inspect
import tomllib
from pathlib import Path
import os
import numpy as np

from mace.domain import plane


class PlaneParser:
    def __init__(self, path) -> None:
        tool_path = Path(__file__).resolve().parents[3]
        file_path = os.path.join(tool_path, "data/planes", path)
        with open(file_path, "rb") as f:
            self.data = tomllib.load(f)
        self.classes = {
            key: val
            for key, val in globals()["plane"].__dict__.items()
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