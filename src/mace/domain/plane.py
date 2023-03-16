from dataclasses import dataclass
#from mace.domain.params import Parameters
import numpy as np


# ---Fuselage---

@dataclass
class FuselageProfile:
    height: int = None
    width: int = None
    position: int = None


@dataclass
class Fuselage:
    profile: FuselageProfile = None
    length: int = None
    mass:float = None


# ---Wing---


@dataclass()
class Flap:
    pass


@dataclass()
class Control:
    c_name: str = None
    c_gain: float = None  # in degrees
    x_hinge: float = None  # between 0 and 1
    sgn_dup: float = 1


@dataclass()
class WingSegment:
    nose_inner: np.ndarray = None  # [x,y,z]
    nose_outer: np.ndarray = None
    back_inner: np.ndarray = None
    back_outer: np.ndarray = None
    # chord_inner = ((back_inner[0] - nose_inner[0]) ** 2 + (back_inner[1] - nose_inner[1]) ** 2 + (
    #             back_inner[2] - nose_inner[2]) ** 2) ** 0.5
    # chord_outer = ((back_outer[0] - nose_outer[0]) ** 2 + (back_outer[1] - nose_outer[1]) ** 2 + (
    #             back_outer[2] - nose_outer[2]) ** 2) ** 0.5
    area: float = 0
    volume: float = 0
    a_inc: float = 0
    a_inc_outer: float = 0
    n_spanwise: int = None
    s_space: int = None
    control = Control


@dataclass()
class Wing:
    segments: list[WingSegment] = None
    airfoil: str = None
    mass: float = None
    # for AVL:
    isactive = False
    name = "Wing"
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
    l_comp: float = 1


# --- Empennage---


@dataclass()
class TEmpennage:
    elevator: list[WingSegment] = None
    rudder: list[WingSegment] = None
    mass: float = None


@dataclass()
class VEmpennage:
    segments: list[WingSegment] = None
    mass: float = None


@dataclass
class EmpennageType:
    typ: TEmpennage | VEmpennage = None
    isactive = False


# ---Propulsion---


@dataclass()
class Propulsion:
    motor: str = None
    esc: str = None
    propeller: str = None
    thrust: np.ndarray = None
    mass: float = None


# ---Landing Gear Configuration---


@dataclass()
class LandingGear:
    my: float = 0.16  # Rollreibungskoeffizient
    configuration: str = None
    mass: float = None
    alpha_roll = None


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
    lambd_k: float = 0.4  # Taper ratio (Zuspitzung)
    lambd_g: float = 11  # Aspect ratio (Streckung)

# ---Aerodynamic Coefficients---


@dataclass()
class Cl:
    cl_tot: float = None


@dataclass()
class Cd:
    cd_tot: float = 0
    cd_vis: float = 0
    cd_ind: float = 0
    cd_viscous: float = 0


@dataclass()
class AeroCoeffs:
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
    cl_roll: float = 0
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
    gamma_max: float = None
    v_vertical_max: float = None


@dataclass()
class Climb:
    results: ClimbResults = None

@dataclass()
class HorizontalFlightResults:
    thrust_velocity_correlation: np.ndarray = None
    minimum_thrust: np.ndarray = None
    maximum_flight_velocity: tuple = None

@dataclass()
class HorizontalFlight:
    results: HorizontalFlightResults = None

@dataclass()
class GlidingFlightResults:
    gliding_data: np.ndarray = None
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
    empennage: EmpennageType = None
    wing: Wing = None
    fuselage: Fuselage = None
    mass: float = 5
    propulsion: Propulsion = None
    landing_gear: LandingGear = None
    aero_coeffs: AeroCoeffs = None
    #parameters = Parameters
    electronics = Electronics
    reference_values = ReferenceValues
    avl: Avl = None
    flightconditions: FlightConditions = None
