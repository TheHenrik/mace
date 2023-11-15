from dataclasses import dataclass

import numpy as np


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
    cd_fuse: float = 0
    cd_wheels: float = 0


@dataclass()
class AeroCoeffs:
    velocity: float = None
    lift_coeff: Cl = None
    drag_coeff: Cd = None
    flap_angle: float = None
    # for AVL
    cdp: float = (
        0  # not used, just in case. Default profile drag coefficient added to geometry.
    )


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
    first_and_last_strips = {}  # Dictionary
    surface_dictionary = {}
    strip_forces: np.ndarray = None


@dataclass()
class Avl:
    inputs: AvlInputs = None
    outputs: AvlOutputs = None


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
    gliding_data: np.ndarray = None  # [cl, cd, cd_viscous, cd_induced, velocity, vertical_velocity] in each row
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

class Data:
    def as_csv_line(self, delimitter = ";", header = False) -> str:
        line = f"{delimitter} ".join(map(str, self.__dict__.values())) + "\n"
        if header:
            line = f"{delimitter} ".join(map(str, self.__dict__.keys())) + "\n" + line
        return line
    


if __name__ == '__main__':
    results = Data()
    results.cl = 0.5
    results.cd = 0.3
    results.mass = 0.7

    print(results.as_csv_line(header=False))