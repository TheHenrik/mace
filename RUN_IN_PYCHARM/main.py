from vehicle_setup import vehicle_setup
from mace.domain.parser import PlaneParser
from mace.aero.flightconditions.horizontalflight import HorizontalFlight
from mace.aero.flightconditions.climb import Climb
from mace.aero.flightconditions.takeoff_jf import TakeOff

from mace.aero.implementations.avl import geometry_and_mass_files_v2 as geometry_and_mass_files
import matplotlib.pyplot as plt


if __name__ == '__main__':
    # Define Analysis
    climb_time = 55.

    # Define Aircraft Geometry
    Aircraft = vehicle_setup()

    mass_file = geometry_and_mass_files.MassFile(Aircraft)
    mass_file.build_mass_file()

    geometry_file = geometry_and_mass_files.GeometryFile(plane)
    geometry_file.z_sym = 1
    geometry_file.build_geometry_file()
    
    # Run Take-Off Analysis
    takeoff_analysis = TakeOff(Aircraft)
    takeoff_analysis.flap_angle = 10.
    takeoff_analysis.cl_safety_factor = 1.3
    takeoff_analysis.evaluate()

    # Geometry File with zsym = 0
    geometry_file.z_sym = 0
    geometry_file.build_geometry_file()

    # Run Climb Analysis
    climb_analysis = Climb(Aircraft)
    climb_analysis.flap_angle = 4.
    climb_analysis.cl_start = 0.4
    climb_analysis.cl_step = 0.1
    H = climb_analysis.get_h_max(delta_t=climb_time)
    print("H Climb: %.1f m" % H)

    # Run Cruise Analysis
    cruise_analysis = HorizontalFlight(Aircraft)
    cruise_analysis.flap_angle = 0.
    cruise_analysis.cl_start = 0.07
    cruise_analysis.cl_step = 0.04
    cruise_analysis.cl_end = 0.4
    V_max = cruise_analysis.get_maximum_velocity()
    print("Maximum Velocity: %.1f m/s" %  V_max)
    cruise_analysis.plot_fv_diagramm()