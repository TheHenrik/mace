import logging
from itertools import product
from multiprocessing import Pool

import matplotlib.pyplot as plt
import numpy as np
from vehicle_setup import vehicle_setup

from mace.aero.flightconditions.climb_scipy import Climb
from mace.aero.flightconditions.efficiency_flight_low_fid import EfficiencyFlight
from mace.aero.flightconditions.horizontalflight import HorizontalFlight
from mace.aero.flightconditions.takeoff_jf import TakeOff
from mace.aero.implementations.avl import (
    geometry_and_mass_files_v2 as geometry_and_mass_files,
)
from mace.utils.mp import get_pid
from time import perf_counter


def main():
    payload = np.linspace(2.0, 3.0, num=2)
    span = (3.0, 3.0)
    aspect_ratio = (13.0,)
    airfoil = ["acc22", "acc22"]
    start = perf_counter()
    logging.info("Started programm")
    with Pool() as p:
        a = p.map(analysis, product(payload, span, aspect_ratio, airfoil))
    end = perf_counter()
    logging.info(f"Finished in: {end-start}")

def analysis(args):
    logging.basicConfig(level=logging.INFO)
    logging.info(f"Start Task {get_pid()}")
    payload, span, aspect_ratio, airfoil = args
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
    takeoff_analysis.v_wind = 3.08
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
    s_cruise = V_max * cruise_time
    logging.debug("S Cruise: %.1f m" % s_cruise)
    logging.info(f"Task finished {get_pid()}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    # main()

    start = perf_counter()
    analysis((3.0,3.0,12.0,"ag19"))
    end = perf_counter()
    logging.info(f"Took {end-start}s")
