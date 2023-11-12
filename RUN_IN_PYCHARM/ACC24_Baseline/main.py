import logging
from itertools import product
from multiprocessing import Pool
import sys
import re
from tqdm import tqdm
from operator import mul
from functools import reduce, partial
import numpy as np
from vehicle_setup import vehicle_setup
from pathlib import Path
import os

from mace.aero.flightconditions.climb_scipy import Climb
from mace.aero.flightconditions.efficiency_flight_low_fid import EfficiencyFlight
from mace.aero.flightconditions.horizontalflight import HorizontalFlight
from mace.aero.flightconditions.takeoff_jf import TakeOff
from mace.aero.implementations.avl import (
    geometry_and_mass_files_v2 as geometry_and_mass_files,
)
from mace.utils.mp import get_pid


def main():
    payload = np.arange(3.57 - 0.51 * 3, 3.57 + 0.51 * 3, 0.17)
    span = [2.0,]
    aspect_ratio = [10.0, 10.5, ]
    airfoil = ["ag45c"]
    match sys.argv:
        case _, "0":
            num_fowler_segments = []
        case _, "1":
            num_fowler_segments = [4]
        case _, "2":
            num_fowler_segments = [0]
        case _, "3":
            num_fowler_segments = [1]
        case _, "4":
            num_fowler_segments = [2]
        case _, "5":
            num_fowler_segments = [3]
        case _:
            num_fowler_segments = [1]

    path = Path(Path(__file__).parent, f"results_sweep.csv")
    handler(path, payload, span, aspect_ratio, airfoil, num_fowler_segments)


def handler(file: Path, *args, **kwargs):
    with open(file, "w") as f, Pool(2) as p:
        for r in tqdm(
            p.imap_unordered(partial(worker, **kwargs), product(*args)),
            total=reduce(mul, map(len, args)),
        ):
            f.write(", ".join(map(str, r)) + "\n")
            f.flush()
            os.fsync(f.fileno())


def worker(args, **kwargs):
    log_path = Path(Path(__file__).parents[2], "temporary", "default.log")
    logging.basicConfig(filename=log_path, level=logging.INFO)
    logging.info(f"Started Task{get_pid()}")
    values = analysis(*args, **kwargs)
    clean_temporary(Path("temporary"))
    logging.info(f"Finished Task{get_pid()}")
    return values


def clean_temporary(path: Path):
    pid = get_pid()
    for file in path.glob("*"):
        if re.fullmatch(rf"^[a-z_]+{pid}\.(?:avl|in|mass)$", file.name):
            file.unlink()


def analysis(payload, span, aspect_ratio, airfoil, num_fowler_segments):
    # Define Analysis
    climb_time = 30.0
    cruise_time = 90.0
    transition_time = 3.0
    minimum_height = 10.0

    # Define Aircraft Geometry
    Aircraft = vehicle_setup(
        payload=payload,
        span=span,
        aspect_ratio=aspect_ratio,
        airfoil=airfoil,
        num_fowler_segments=num_fowler_segments,
    )
    logging.debug("M Payload: %.2f kg" % Aircraft.payload)
    return (payload, span, aspect_ratio, airfoil, num_fowler_segments)

    # Build AVL Mass File
    mass_file = geometry_and_mass_files.MassFile(Aircraft)
    mass_file.build_mass_file()

    # Build AVL Geometry File for TakeOff
    geometry_file = geometry_and_mass_files.GeometryFile(Aircraft)
    geometry_file.z_sym = 1
    geometry_file.build_geometry_file()

    # Run Take-Off Analysis
    takeoff_analysis = TakeOff(Aircraft)
    takeoff_analysis.mu = 0.125
    takeoff_analysis.flap_angle = 12.0
    takeoff_analysis.t_step = 0.2
    takeoff_analysis.cl_safety_factor = 1.3
    takeoff_analysis.v_wind = 2.2  # 3.08 average in Aachen
    takeoff_analysis.v_start_counter = 1.333
    takeoff_analysis.show_plot = False
    take_off_length, take_off_time = takeoff_analysis.evaluate()
    logging.debug("S TakeOff: %.1f m" % take_off_length)
    logging.info(f"Finished Task TakeOff")

    # Geometry File with zsym = 0
    geometry_file.z_sym = 0
    geometry_file.build_geometry_file()

    # Run Climb Analysis
    climb_analysis = Climb(Aircraft)
    climb_analysis.optimize_flap_angle = True
    climb_height, climb_ias = climb_analysis.get_h_max(
        delta_t=climb_time - take_off_time - transition_time
    )
    climb_height = min(climb_height, 100.0)
    logging.debug("H Climb: %.1f m, V IAS %.1f m/s" % (climb_height, climb_ias))

    logging.info(f"Finished Task Climb")

    # Run Efficiency Analysis
    efficiency_flight = EfficiencyFlight(Aircraft)
    e_efficiency, eff_v1, eff_t1, eff_v2 = efficiency_flight.optimizer(
        climb_ias, climb_height, I=30.0
    )
    logging.info(f"Finished Task Efficiency")

    # Run Cruise Analysis
    cruise_analysis = HorizontalFlight(Aircraft)
    cruise_analysis.optimize_flap_angle = True
    V_max = cruise_analysis.get_maximum_velocity_scipy()
    s_distance = V_max * cruise_time
    logging.info(f"Finished Task Cruise")

    # Calculate Score
    if take_off_length <= 40.0:
        take_off_factor = 1.05
    elif take_off_length <= 60.0:
        take_off_factor = 1.0
    else:
        take_off_factor = 0.0

    reference_max_payload = 6.0
    score_payload = payload / reference_max_payload * 1000.0

    reference_max_s_distance = 3200.0
    score_distance = 1000.0 * s_distance / reference_max_s_distance

    reference_max_e_efficiency = 0.74
    score_efficiency = 1000.0 * e_efficiency / reference_max_e_efficiency

    t_loading = 8.0
    t_unloading = 8.0
    b_loading = 60 * (1 - (t_loading + t_unloading) / 180)

    penalty_current = 0.0
    penalty_round = 0.0

    score_round = (
        (score_payload + score_efficiency + score_distance) / 3.0
        + b_loading
        - penalty_current
    ) * take_off_factor - penalty_round

    logging.debug("S Cruise: %.1f m" % s_distance)

    wing_area = span**2 / aspect_ratio
    wing_loading = Aircraft.mass / wing_area
    return (
        payload,
        span,
        aspect_ratio,
        airfoil,
        num_fowler_segments,
        Aircraft.mass,
        wing_area,
        wing_loading,
        take_off_length,
        climb_height,
        e_efficiency,
        eff_v1,
        eff_t1,
        eff_v2,
        s_distance,
        score_payload,
        score_efficiency,
        score_distance,
        b_loading,
        penalty_current,
        take_off_factor,
        penalty_round,
        score_round,
    )


if __name__ == "__main__":
    main()
    # worker((3.57, 2.0, 10.0, "ag45c", 0))
