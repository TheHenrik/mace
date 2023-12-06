import logging
import os
import re
import sys
from functools import partial, reduce
from itertools import product
from multiprocessing import Pool, freeze_support
from operator import mul
from pathlib import Path

import numpy as np
from tqdm import tqdm
from vehicle_setup import vehicle_setup

from mace.aero.flightconditions.climb_scipy import Climb
from mace.aero.flightconditions.efficiency_flight_low_fid import EfficiencyFlight
from mace.aero.flightconditions.horizontalflight import HorizontalFlight
from mace.aero.flightconditions.takeoff_jf import TakeOff
from mace.aero.implementations.avl import (
    geometry_and_mass_files_v2 as geometry_and_mass_files,
)
from mace.domain.params import Constants
from mace.utils.file_path import root
from mace.utils.mp import get_pid


def handler(file: Path, threads: int, *args, **kwargs):
    first_line = True
    with open(file, "w") as f, Pool(threads) as p:
        for r in tqdm(
            p.imap_unordered(partial(worker, **kwargs), product(*args)),
            total=reduce(mul, map(len, args)),
        ):
            if first_line:
                lines = r
                first_line = False
            else:
                lines = r.split("\n", 1)[1]
            f.write(lines)
            f.flush()
            os.fsync(f.fileno())


def worker(args, **kwargs):
    log_path = Path(root(), "temporary", "default.log")
    logging.basicConfig(filename=log_path, level=logging.INFO)
    logging.info(f"Started Task{get_pid()}")
    values = analysis(*args, **kwargs)
    clean_temporary_pid(Path(root(), "temporary"))
    logging.info(f"Finished Task{get_pid()}")
    return values


def clean_temporary_pid(path: Path):
    pid = get_pid()
    for file in path.glob("*"):
        if re.fullmatch(rf"^[a-z_]+{pid}\.(?:avl|in|mass)$", file.name):
            file.unlink()


def clean_temporary(path: Path):
    for file in path.glob("*"):
        if re.fullmatch(rf"^[a-z_]+\d*\.(?:avl|in|mass)$", file.name):
            file.unlink()


def analysis(
    payload,
    wing_area,
    aspect_ratio,
    airfoil,
    num_fowler_segments,
    battery_capacity,
    propeller,
):
    # Define Analysis
    climb_time = 30.0
    cruise_time = 90.0
    transition_time = 3.0
    minimum_height = 10.0

    # Define Aircraft Geometry
    Aircraft = vehicle_setup(
        payload=payload,
        wing_area=wing_area,
        aspect_ratio=aspect_ratio,
        airfoil=airfoil,
        num_fowler_segments=num_fowler_segments,
        battery_capacity=battery_capacity,
        propeller=propeller,
    )

    logging.debug("M Payload: %.2f kg" % Aircraft.payload)
    # return (payload, span, aspect_ratio, airfoil, num_fowler_segments)

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
    climb_analysis.mid_time = (
        (climb_time - take_off_time - transition_time) / 2
        + take_off_time
        + transition_time
    )
    climb_height, climb_ias = climb_analysis.get_h_max(
        delta_t=climb_time - take_off_time - transition_time
    )
    climb_height = min(climb_height, 100.0)
    logging.debug("H Climb: %.1f m, V IAS %.1f m/s" % (climb_height, climb_ias))

    logging.info(f"Finished Task Climb")

    # Run Efficiency Analysis
    efficiency_flight = EfficiencyFlight(Aircraft)
    efficiency_flight.batt_time_at_start = climb_time
    e_efficiency, eff_v1, eff_t1, eff_v2 = efficiency_flight.optimizer(
        climb_ias, climb_height, I=30.0
    )
    logging.info(f"Finished Task Efficiency")

    # Run Cruise Analysis
    cruise_analysis = HorizontalFlight(Aircraft)
    cruise_analysis.batt_time_at_start = efficiency_flight.batt_time_at_start + eff_t1
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

    t_loading = 0.6 * payload / 0.170
    t_unloading = 0.4 * payload / 0.170
    b_loading = 60 * (1 - (t_loading + t_unloading) / 180)

    penalty_current = 0.0
    penalty_round = 0.0

    score_round = (
        (score_payload + score_efficiency + score_distance) / 3.0
        + b_loading
        - penalty_current
    ) * take_off_factor - penalty_round

    results = Aircraft.results
    results.score_factor_take_off = take_off_factor
    results.score_payload = score_payload
    results.max_payload = reference_max_payload
    results.score_efficiency = score_efficiency
    results.max_efficiency = reference_max_e_efficiency
    results.score_distance = score_distance
    results.max_distance = reference_max_s_distance
    results.t_loading = t_loading
    results.t_unloading = t_unloading
    results.b_loading = b_loading
    results.penalty_current = penalty_current
    results.penalty_round = penalty_round
    results.score_round = score_round

    return results.as_csv_line(header=True, delimitter=",")


def main():
    log_path = Path(root(), "temporary", "default.log")
    clean_temporary(Path(root(), "temporary"))
    logging.basicConfig(filename=log_path, level=logging.INFO)
    logging.info("Started programm")
    while True:
        print("Gebe die dir zugeteilte Nummer ein (Mehrfacheingabe möglich):")
        try:
            input_number = input()
            input_number = map(int, re.findall(r"\d+", input_number))
        except ValueError: 
            print("Fehler in der Eingabe")

        print("Anzahl der zu nutzenden Threads:")
        print(
            "(Gebe Null ein, um alle Threads zu nutzen, der Computer wird dann für die nächste Zeit nicht benutzbar sein)"
        )
        print(
            "(Eine Negative Zahl bestimmt die Anzahl der Threads, die nicht genutzt werden sollen)"
        )
        try:
            input_threads = int(input())
            cpu_count = os.cpu_count()
            if input_threads <= 0:
                threads = cpu_count + input_threads
            else:
                threads = input_threads
            if threads == 0 or threads > cpu_count:
                print("Anzahl der eingegebenen Threads kontrollieren.")
                continue 
        except ValueError:
            print("Bitte eine Positive Ganzzahl eingeben.")
            continue

        for number in input_number:
            payload = list(np.linspace(3.57, 4.57, 50))
            aspect_ratio = [10.0, 9.0]
            wing_area = [0.5, 0.6, 0.7]
            airfoil = ["ag45c"]
            battery_capacity = [2.4]
            propeller = ["aeronaut16x8"]
            num_fowler_segments = [0, 1]

            first, second = divmod(number, 1_000)
            airfoil = [airfoil[first]]
            payload = [payload[second]]


            path = Path(root(), f"results_sweep_{number}.csv")
            logging.info("Finished Input")
            handler(
                path,
                threads,
                payload,
                wing_area,
                aspect_ratio,
                airfoil,
                num_fowler_segments,
                battery_capacity,
                propeller,
            )
            print("Durchlauf erfolgreich beendet. Lade die Datei hoch in den Google Drive.")

        print("Weiterer Durchlauf? (j/N)")
        r = input()
        if r.lower() == "j":
            continue
        else:
            break


if __name__ == "__main__":
    if sys.platform.startswith("win"):
        freeze_support()
    main()
    # worker((3.57, 0.61, 8.82, "acc22", 4, 1.6, "aeronaut14x8"))
