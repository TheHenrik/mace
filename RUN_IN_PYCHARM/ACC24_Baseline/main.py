import logging
from itertools import product
from multiprocessing import Pool
from time import perf_counter
import sys

import matplotlib.pyplot as plt
import numpy as np
from vehicle_setup import vehicle_setup
from pathlib import Path

from mace.aero.flightconditions.climb_scipy import Climb
from mace.aero.flightconditions.efficiency_flight_low_fid import EfficiencyFlight
from mace.aero.flightconditions.horizontalflight import HorizontalFlight
from mace.aero.flightconditions.takeoff_jf import TakeOff
from mace.aero.implementations.avl import (
    geometry_and_mass_files_v2 as geometry_and_mass_files,
)
from mace.utils.mp import get_pid
from mace.test.perftest import performance_report


# TODO logging config
# TODO Test on different os
# TODO Airfoils not in gitignore
def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("Started programm")
    payload = np.linspace(2.0, 3.0, num=2)
    span = (3.0,)
    aspect_ratio = (13.0,)
    match sys.argv:
        case _, "dimi", "0":
            airfoil = ["acc22"]
        case _, "dimi", "1":
            airfoil = ["acc22"]
        case _, "jannik", "0":
            airfoil = ["acc22"]
        case _, "jannik", "1":
            airfoil = ["acc22"]
        case _, "tjalf", "0":
            airfoil = ["acc22"]
        case _, "tjalf", "1":
            airfoil = ["acc22"]
        case _:
            airfoil = ["acc22"]

    start = perf_counter()
    path = Path(Path(__file__).parent, "results.csv")
    handler(path, payload, span, aspect_ratio, airfoil)
    end = perf_counter()
    logging.info(f"Finished in: {end-start}")


def handler(file: Path, *args):
    with open(file, "w") as f, Pool() as p:
        for r in p.imap_unordered(worker, product(*args)):
            f.write(", ".join(map(str, r)) + "\n")


def worker(args):
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Started Task{get_pid()}")
    values = analysis(*args)
    logging.info(f"Finished Task{get_pid()}")
    return values


def analysis(payload, span, aspect_ratio, airfoil):
    # Define Analysis
    climb_time = 30.0
    cruise_time = 90.0
    transition_time = 3.0
    minimum_height = 10.0

    # Define Aircraft Geometry
    Aircraft = vehicle_setup(
        payload=payload, span=span, aspect_ratio=aspect_ratio, airfoil=airfoil
    )
    logging.debug("\n")
    logging.debug("M Payload: %.2f kg" % Aircraft.payload)

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
    takeoff_analysis.t_step = 0.4
    takeoff_analysis.cl_safety_factor = 1.3
    takeoff_analysis.v_wind = 2.2  # 3.08 average in Aachen
    takeoff_analysis.v_start_counter = 1.333
    takeoff_analysis.show_plot = False
    take_off_length, take_off_time = takeoff_analysis.evaluate()
    logging.debug("S TakeOff: %.1f m" % take_off_length)

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

    # Run Efficiency Analysis
    efficiency_flight = EfficiencyFlight(Aircraft)
    e_efficiency = efficiency_flight.optimizer(climb_ias, climb_height, I=30.0)

    # Run Cruise Analysis
    cruise_analysis = HorizontalFlight(Aircraft)
    cruise_analysis.optimize_flap_angle = True
    V_max = cruise_analysis.get_maximum_velocity_scipy()
    s_distance = V_max * cruise_time

    # Calculate Score
    if take_off_length <= 40.0:
        take_off_factor = 1.05
    else:
        take_off_factor = 1.0

    reference_max_payload = 5.0
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

    return (
        payload,
        span,
        aspect_ratio,
        airfoil,
        Aircraft.mass,
        take_off_length,
        climb_height,
        e_efficiency,
        s_distance,
        score_payload,
        score_efficiency,
        score_distance,
        b_loading,
        penalty_current,
        take_off_factor,
        penalty_round,
        score_round
    )


if __name__ == "__main__":
    main()
