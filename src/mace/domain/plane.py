from dataclasses import dataclass
from typing import List
from mace.domain.params import Parameters
import numpy as np


@dataclass()
class MassAndInertia:
    mass: float = 0
    x_location: float = 0
    y_location: float = 0
    z_location: float = 0
    i_xx: float = 0
    i_yy: float = 0
    i_zz: float = 0
    i_xy: float = 0
    i_xz: float = 0
    i_yz: float = 0


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
    mass = MassAndInertia


# ---Wing---


@dataclass()
class Flap:
    pass


@dataclass()
class Naca:
    number_of_naca: int  = 0000

@dataclass()
class AirfoilFile:
    filepath: str = None

@dataclass()
class Airfoil:
    type: Naca | AirfoilFile = None

@dataclass()
class Control:
    c_name: str = None
    c_gain: float = None        # in degrees
    x_hinge: float = None       # between 0 and 1
    hinge_vec: np.ndarray = [0, 0, 0]   #HingeVec most cases 0.0.0 -> along hinge
    sgn_dup: float = 1


@dataclass()
class WingSegment:
    nose_inner: np.ndarray = None   # [x,y,z]
    nose_outer: np.ndarray = None
    back_inner: np.ndarray = None
    back_outer: np.ndarray = None
    mass = MassAndInertia
    chord_inner = ((back_inner[0] - nose_inner[0])**2 + (back_inner[1] - nose_inner[1])**2 + (back_inner[2] - nose_inner[2])**2)**0.5
    chord_outer = ((back_outer[0] - nose_outer[0])**2 + (back_outer[1] - nose_outer[1])**2 + (back_outer[2] - nose_outer[2])**2)**0.5
    area: float = 0
    volume: float = 0
    # for AVL
    a_inc: float = 0
    a_inc_outer: float = 0
    n_spanwise: int = None
    s_space: int  = None
    airfoil = Airfoil
    control = Control


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
    mass = MassAndInertia
    geo_wing_values: GeometricWingValues = None
    # for AVL:
    isactive = False
    name = "Wing"
    n_chordwise: int = 10
    c_space: int = 1        # = cos
    n_spanwise: int = 20
    s_space: int = -2       # = -sin, good for straight, elliptical or slightly tapered wings, in other cases cos (1)
    x_scale: float = 0
    y_scale: float = 0
    z_scale: float = 0
    x_translate: float = 0
    y_translate: float = 0
    z_translate: float = 0
    twist_angle: float = 0
    l_comp: float = 1


# --- Empennage---


@dataclass()
class TEmpennage:
    elevator: List[WingSegment] = None
    airfoil_e: str = None
    rudder: List[WingSegment] = None
    airfoil_r: str = None
    mass = MassAndInertia


@dataclass()
class VEmpennage:
    segments: List[WingSegment] = None
    airfoil = None
    mass = MassAndInertia


@dataclass
class EmpennageType:
    typ: TEmpennage | VEmpennage = None
    mass = typ.mass.mass
    # for AVL, yet not usable because not defferentiated into different surfaces rudder end elevator
    isactive = False
    """name = "Empennage"
    n_chordwise: int = 10
    c_space: int = 1  # = cos
    n_spanwise: int = 20
    s_space: int = -2  # = -sin, good for straight, elliptical or slightly tapered wings, in other cases cos (1)
    x_scale: float = 0
    y_scale: float = 0
    z_scale: float = 0
    x_translate: float = 0
    y_translate: float = 0
    z_translate: float = 0
    twist_angle: float = 0
    l_comp: float = 2"""


# ---Propulsion---


@dataclass()
class Propulsion:
    motor: str = None
    esc: str = None
    propeller: str = None
    thrust: np.ndarray = None
    mass_of_motor = MassAndInertia
    mass_of_esc = MassAndInertia
    mass_of_propeller = MassAndInertia
    mass = MassAndInertia
    mass.mass = mass_of_motor.mass + mass_of_esc.mass + mass_of_propeller.mass


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
    mass = MassAndInertia


@dataclass()
class Electronics:
    servos:
    cabels:
    batteries:
    linkages:

@dataclass()
class ReferenceValues:
    mach: float = 0         # mach number for Prandtl-Glauert correction
    iy_sym: float = 0       # has to be 0 for YDUPLICATE
    iz_sym: float = 0       # 0: no z-symmetry assumed
    z_sym: float = 0        # for iz_sym = 0 ignored
    s_ref: float = 0        # reference wing area
    c_ref: float = 0        # reference chord length
    b_ref: float = 0        # reference wingspan for moment coefficients
    x_ref: float = 0        # must bei CG location for trim calculation
    y_ref: float = 0        # must bei CG location for trim calculation
    z_ref: float = 0        # must bei CG location for trim calculation


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
    # for AVL
    cdp: float = 0          # not used, just in case. Default profile drag coefficient added to geometry.


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
    parameters = Parameters
    electronics = Electronics
    reference_values = ReferenceValues
    list_of_component_names: list = [fuselage, wing, empennage, propulsion, landing_gear, electronics]

