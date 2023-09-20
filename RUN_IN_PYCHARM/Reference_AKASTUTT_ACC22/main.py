import matplotlib.pyplot as plt
from vehicle_setup_acc22_akastutt import vehicle_setup

from mace.aero.flightconditions.climb import Climb
from mace.aero.flightconditions.horizontalflight import HorizontalFlight
from mace.aero.flightconditions.takeoff_jf import TakeOff
from mace.aero.implementations.avl import (
    geometry_and_mass_files_v2 as geometry_and_mass_files,
)
from mace.domain.parser import PlaneParser

if __name__ == '__main__':
    # Define Analysis
    climb_time = 60.
    cruise_time = 120.
    transition_time = 5.

    # Define Aircraft Geometry
    Aircraft = vehicle_setup()

    mass_file = geometry_and_mass_files.MassFile(Aircraft)
    mass_file.build_mass_file()

    geometry_file = geometry_and_mass_files.GeometryFile(Aircraft)
    geometry_file.z_sym = 1
    geometry_file.build_geometry_file()
    
    # Run Take-Off Analysis
    takeoff_analysis = TakeOff(Aircraft)
    takeoff_analysis.mu = 0.125
    takeoff_analysis.flap_angle = 10.
    takeoff_analysis.cl_safety_factor = 1.3
    takeoff_analysis.v_wind = 1.
    takeoff_analysis.v_start_counter = 1.3

    take_off_length, take_off_time = takeoff_analysis.evaluate()

    # Geometry File with zsym = 0
    geometry_file.z_sym = 0
    geometry_file.build_geometry_file()

    # Run Climb Analysis
    climb_analysis = Climb(Aircraft)
    climb_analysis.flap_angle = 0. #0 for akastutt, 4 for addi
    climb_analysis.cl_start = 0.2
    climb_analysis.cl_step = 0.1
    climb_analysis.cl_end = 1.5
    H = climb_analysis.get_h_max(delta_t=climb_time-take_off_time-transition_time)
    v_s = H / (climb_time - take_off_time - transition_time)
    print("V_s: %.3f m/s" % v_s)
    print("H Climb: %.1f m" % H)

    # Run Cruise Analysis
    cruise_analysis = HorizontalFlight(Aircraft)
    cruise_analysis.flap_angle = 0.
    cruise_analysis.cl_start = 0.1
    cruise_analysis.cl_step = 0.05
    cruise_analysis.cl_end = 0.7
    V_max = cruise_analysis.get_maximum_velocity()
    print("V_max: %.1f m/s" % V_max)
    s_cruise = V_max * cruise_time
    print("S Cruise: %.1f m" %  s_cruise)
    cruise_analysis.plot_fv_diagramm()