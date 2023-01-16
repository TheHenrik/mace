from dataclasses import dataclass
from typing import List

import numpy as np


@dataclass
class HullProfile:
    hight: int = None
    width: int = None
    position: int = None


@dataclass
class Hull:
    lenght: int = None
    profile: HullProfile = None
    mass: float = 0


@dataclass()
class Flap:
    pass


@dataclass()
class WingSegment:
    nose_inner: np.ndarray = None
    nose_outer: np.ndarray = None
    back_inner: np.ndarray = None
    back_outer: np.ndarray = None
    mass: float = 0
    area: float = 0
    volume: float = 0


@dataclass()
class TEmpennage:
    elevator: List[WingSegment] = None
    airfoil_e: str = None
    rudder: List[WingSegment] = None
    airfoil_r: str = None
    mass: float = 0


@dataclass()
class VEmpennage:
    segments: List[WingSegment] = None
    airfoil = None
    mass: float = 0


@dataclass
class EmpennageType:
    typ: TEmpennage | VEmpennage = None


@dataclass()
class Wing:
    segments: List[WingSegment] = None
    airfoil: str = None
    mass: float = 0


@dataclass()
class Plane:
    name: str = None
    empennage: EmpennageType = None
    wing: Wing = None
    hull: Hull = None
    mass: float = 0
