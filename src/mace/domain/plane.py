from dataclasses import dataclass
from typing import List
from mace.domain.params import Parameters
from mace.domain.wing import Wing, WingSegment
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
class Naca:
    number_of_naca: int = 0000
    filepath: str = None

@dataclass()
class AirfoilFile:
    filepath: str = None


@dataclass()
class Airfoil:
    type: Naca | AirfoilFile = None
    name: str = None


@dataclass()
class Control:
    c_name: str = None
    c_gain: float = None  # in degrees
    x_hinge: float = None  # between 0 and 1
    # hinge_vec: np.ndarray = [0, 0, 0]  # HingeVec most cases 0.0.0 -> along hinge
    sgn_dup: float = 1


@dataclass()
class WingSegment:
    nose_inner: np.ndarray = None  # [x,y,z]
    nose_outer: np.ndarray = None
    back_inner: np.ndarray = None
    back_outer: np.ndarray = None
    mass: float = 0
    area: float = 0
    volume: float = 0
    # for AVL
    a_inc: float = 0
    a_inc_outer: float = 0
    n_spanwise: int = None
    s_space: int = None
    inner_airfoil: Airfoil = None
    outer_airfoil: Airfoil = None
    control: Control = None

@dataclass()
class Wing:
    segments: List[WingSegment] = None
    airfoil: str = None
    mass: float = 0
    # for AVL:
    isactive = True
    name = "Wing"
    n_chordwise: int = 10
    c_space: int = 1  # = cos
    n_spanwise: int = 20
    s_space: int = -2  # = -sin, good for straight, elliptical or slightly tapered wings, in other cases cos (1)
    x_scale: float = 0
    y_scale: float = 0
    z_scale: float = 0
    # scale = np.array([0, 0, 0])
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
    # mass = typ.mass.mass
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
    thrust: np.ndarray = None       # [[v0, f0], [v1, f1], [v2, f2], [v3, f3], ...]
    mass_of_motor: float = 0
    mass_of_esc: float = 0
    mass_of_propeller: float = 0
    mass: float = 0
    # mass = mass_of_motor + mass_of_esc + mass_of_propeller


# ---Landing Gear Configuration---

@dataclass()
class Bipod:  # Zweibeinfahrwerk
    alfa_roll: float = None


@dataclass()
class Tricycle:  # Dreibeinfahrwerk
    alfa_roll: float = None


@dataclass()
class LandingGearConfig:
    typ: Bipod | Tricycle


@dataclass()
class LandingGear:
    my: float = 0.16  # Rollreibungskoeffizient
    configuration: LandingGearConfig = Tricycle
    mass = MassAndInertia


@dataclass()
class Electronics:
    servos = None
    cabels = None
    batteries = None
    linkages = None

@dataclass()
class ReferenceValues:
    number_of_surfaces: float = 0
    mach: float = 0  # mach number for Prandtl-Glauert correction
    iy_sym: float = 0  # has to be 0 for YDUPLICATE
    iz_sym: float = 0  # 0: no z-symmetry assumed
    z_sym: float = 0  # for iz_sym = 0 ignored
    s_ref: float = 0  # reference wing area
    c_ref: float = 0  # reference chord length
    b_ref: float = 0  # reference wingspan for moment coefficients
    x_ref: float = 0  # must bei CG location for trim calculation
    y_ref: float = 0  # must bei CG location for trim calculation
    z_ref: float = 0  # must bei CG location for trim calculation
    h: float = 0  # Height wof WingNP above ground for rolling
    b: float = 0  # Spanwidth
    lambd_k: float = 0  # Taper ratio (Zuspitzung)
    lambd_g: float = 0  # Aspect ratio (Streckung) b^2 / S


# ---Aerodynamic Coefficients---


@dataclass()
class Cl:
    # cl: float = None
    cl_roll: float = None
    # cl_take_off: float = None
    # --- from AVL:
    cl_tot: float = None


@dataclass()
class Cd:
    # cd_profil: float = None
    # cdi: float = None
    # --- from AVL:
    cd_tot: float = 0
    cd_vis: float = 0
    cd_ind: float = 0


@dataclass()
class AeroCoeffs:
    velocity: float = None
    lift_coeff: Cl = None
    drag_coeff: Cd = None
    # for AVL
    cdp: float = 0  # not used, just in case. Default profile drag coefficient added to geometry.


# --- AVL ---


@dataclass()
class AvlInputs:
    avl_file = None
    mass_file = None


@dataclass()
class AvlOutputs:
    # Trefftz plane
    clff: float = 0
    cdff: float = 0
    cyff: float = 0
    oswaldfactor: float = 0
    # Reference data
    s_ref: float = 0
    c_ref: float = 0
    b_ref: float = 0
    x_ref: float = 0
    y_ref: float = 0
    z_ref: float = 0
    # Overall data
    number_of_strips: int = 0
    number_of_surfaces: int = 0
    number_of_vortices: int = 0
    # Surface data
    surface_data: np.ndarray = None
    first_and_last_strips = {}          # Dictionary
    surface_dictionary = {}
    strip_forces: np.ndarray = None


@dataclass()
class Avl:
    inputs: AvlInputs = None
    outputs: AvlOutputs = None


# ---Flightconditions---

@dataclass()
class TakeOffResults:
    v_max_rolling: float = None
    v_timer_start: float = 0
    rolling_distance: float = None
    rolling_time: float = None


@dataclass()
class TakeOff:
    my: float = 0
    # cl_roll: float = 0
    cd_viscous: float = 0
    cd_induced: float = 0
    phi_a: float = 0
    phi_w: float = 0
    delta_a: float = 0
    delta_w: float = 0
    beta_a: float = 0
    beta_w: float = 0
    results: TakeOffResults = None


@dataclass()
class ClimbResults:
    climb_data: np.ndarray = None
    gamma_max: float() = None
    v_vertical_max: float() = None


@dataclass()
class Climb:
    results: ClimbResults = None

@dataclass()
class HorizontalFlightResults:
    thrust_velocity_correlation: np.ndarray = None  # [[v1, t1], [v2, t2], [...], ...]
    minimum_thrust: np.ndarray = None
    maximum_flight_velocity: tuple = None

@dataclass()
class HorizontalFlight:
    results: HorizontalFlightResults = None

@dataclass()
class GlidingFlightResults:
    gliding_data: np.ndarray = None      # [cl, cd, cd_viscous, cd_induced, velocity, vertical_velocity] in each row
    data_best_glide_ratio: np.ndarray = None
    data_smallest_decline: np.ndarray = None
    best_glide_ratio: float = None
    row_index_best_glide_ratio: int = None
    smallest_decline: float = None
    row_index_smallest_decline: int = None
@dataclass()
class GlidingFlight:
    results: GlidingFlightResults = None

@dataclass()
class FlightConditions:
    takeoff: TakeOff = None
    climb: Climb = None
    horizontalflight: HorizontalFlight = None
    glidingflight: GlidingFlight = None

# ---Plane itself---


@dataclass()
class Plane:
    name: str = None
    wings = {}
    fuselage: Fuselage = None
    mass: np.ndarray = None                 # [mass   x     y     z    [ Ixx     Iyy    Izz     Ixy   Ixz   Iyz ]
    propulsion: Propulsion = None
    landing_gear: LandingGear = None
    aero_coeffs: AeroCoeffs = None
    parameters = Parameters
    electronics = Electronics
    reference_values: ReferenceValues = None
    avl: Avl = None
    flightconditions: FlightConditions = None
    
    def add_wing(self, position: str, wing: Wing):
        self.wings[position] = wing

# ------ Initialize Test Airplane ------

def build_plane() -> Plane:
    avl_outputs = AvlOutputs()
    avl_inputs = AvlInputs()
    avl = Avl(avl_inputs, avl_outputs)
    cl = Cl()
    cd = Cd()
    aero_coeffs = AeroCoeffs(cl, cd)

    plane = Plane(name='airbus', empennage=EmpennageType(), wing=Wing(), fuselage=Fuselage(),
                  mass=5, aero_coeffs=aero_coeffs, avl=avl)
    return plane
