from dataclasses import dataclass
from typing import List

import numpy as np


# ---Fuselage---

@dataclass
class FuselageProfile:
    height: int = None
    width: int = None
    position: int = None


@dataclass
class Fuselage:
    length: int = None
    profile: FuselageProfile = None
    mass: float = 0


# ---Wing---


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
class GeometricWingValues:
    h: float = 0.4                 # Height wof WingNP above ground for rolling
    b: float = 3.0                 # Spanwidth
    s_ref: float = 1.5             # Wing reference area
    lambd_k: float = 0.4           # Taper ratio (Zuspitzung)
    lambd_g: float = 11            # Aspect ratio (Streckung)


@dataclass()
class Wing:
    segments: List[WingSegment] = None
    airfoil: str = None
    mass: float = 0
    geo_wing_values: GeometricWingValues = None


# --- Empennage---


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


# ---Propulsion---


@dataclass()
class Propulsion:
    motor: str = None
    esc: str = None
    propeller: str = None
    thrust: np.ndarray = None


# ---Landing Gear Configuration---

@dataclass()
class Bipod:                                        # Zweibeinfahrwerk
    alfa_roll: float = None


@dataclass()
class Tricycle:                                     # Dreibeinfahrwerk
    alfa_roll: float = None


@dataclass()
class LandingGearConfig:
    typ: Bipod | Tricycle


@dataclass()
class LandingGear:
    my: float = 0.16                                # Rollreibungskoeffizient
    configuration: LandingGearConfig = Tricycle

# ---Aerodynamic Coefficients---    in Params


@dataclass()
class Ca:
    ca: float = None
    ca_roll: float = 0.4
    ca_abheb: float = 0.6


@dataclass()
class Cw:
    cw_profil: float = 0.01
    cwi: float = 0.02


@dataclass()
class AeroCoeffs:
    lift_coeff: Ca = None
    drag_coeff: Cw = None


# ---Plane itself---


@dataclass()
class Plane:
    name: str = None
    empennage: EmpennageType = None
    wing: Wing = None
    fuselage: Fuselage = None
    mass: float = 5
    propulsion: Propulsion = None
    landing_gear: LandingGear = None
    aero_coeffs: AeroCoeffs = None
