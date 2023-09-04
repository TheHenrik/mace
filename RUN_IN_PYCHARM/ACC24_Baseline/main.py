from vehicle_setup import vehicle_setup
from mace.domain.parser import PlaneParser
from mace.aero.flightconditions.horizontalflight import HorizontalFlight
from mace.aero.flightconditions.climb_scipy import Climb
from mace.aero.flightconditions.takeoff_jf import TakeOff
from mace.aero.flightconditions.glidingflight_jf import GlidingFlight

from mace.aero.implementations.avl import geometry_and_mass_files_v2 as geometry_and_mass_files
import matplotlib.pyplot as plt


if __name__ == '__main__':
    payload = 4.8
    span = 3.
    aspect_ratio = 12.

    # Define Analysis
    climb_time = 30.
    cruise_time = 90.
    transition_time = 3.
    minimum_height = 10.

    # Define Aircraft Geometry
    Aircraft = vehicle_setup(payload=payload, span=span, aspect_ratio=aspect_ratio)
    print('\n')
    print('M Payload: %.2f kg' % Aircraft.payload)

    # Build AVL Mass File
    mass_file = geometry_and_mass_files.MassFile(Aircraft)
    mass_file.build_mass_file()

    # Build AVL Geometry File for TakeOff
    geometry_file = geometry_and_mass_files.GeometryFile(Aircraft)
    geometry_file.z_sym = 1
    geometry_file.build_geometry_file()

    # Run Take-Off Analysis
    takeoff_analysis = TakeOff(Aircraft)
    takeoff_analysis.mu = 0.08
    takeoff_analysis.flap_angle = 12.
    takeoff_analysis.cl_safety_factor = 1.3
    takeoff_analysis.v_wind = 1.
    takeoff_analysis.v_start_counter = 1.333
    take_off_length, take_off_time = takeoff_analysis.evaluate()
    print("S TakeOff: %.1f m" % take_off_length)

    # Geometry File with zsym = 0
    geometry_file.z_sym = 0
    geometry_file.build_geometry_file()

    # Run Climb Analysis
    climb_analysis = Climb(Aircraft)
    climb_analysis.optimize_flap_angle = False
    climb_analysis.flap_angle = 2.
    climb_analysis.cl_start = 0.2
    climb_analysis.cl_step = 0.1
    climb_analysis.cl_end = 1.5
    climb_height = climb_analysis.get_h_max(delta_t=climb_time-take_off_time-transition_time)
    climb_height = min(climb_height, 100.)
    print("H Climb: %.1f m" % climb_height)

    # Run Efficiency Analysis
    efficiency_analysis = GlidingFlight(Aircraft)
    efficiency_analysis.flap_angle = 6.
    efficiency_analysis.cl_start = 0.5
    efficiency_analysis.cl_step = 0.05
    efficiency_analysis.cl_end = 1.5
    glide_time = efficiency_analysis.get_glide_time(climb_height-minimum_height)
    print("T Glide: %.1f s" % glide_time)

    # Run Cruise Analysis
    cruise_analysis = HorizontalFlight(Aircraft)
    cruise_analysis.flap_angle = 0.
    cruise_analysis.cl_start = 0.07
    cruise_analysis.cl_step = 0.05
    cruise_analysis.cl_end = 1.
    V_max = cruise_analysis.get_maximum_velocity_scipy()
    s_cruise = V_max * cruise_time
    print("S Cruise: %.1f m" %  s_cruise)
