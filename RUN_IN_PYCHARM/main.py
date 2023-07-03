from vehicle_setup import vehicle_setup
from mace.domain.parser import PlaneParser
from mace.aero.flightconditions.horizontalflight import HorizontalFlight
from mace.aero.flightconditions.climb_jf import Climb
from mace.aero.implementations.avl import geometry_and_mass_files_v2 as geometry_and_mass_files
import matplotlib.pyplot as plt


if __name__ == '__main__':
    # Define Analysis
    climb_time = 60.0

    # Define Aircraft Geometry
    Aircraft = vehicle_setup()
    #Aircraft = PlaneParser("aachen.toml").get("Plane")

    # Build AVL input files
    geometry_and_mass_files.GeometryFile(Aircraft).build_geometry_file()
    geometry_and_mass_files.MassFile(Aircraft).build_mass_file()
    
    # Run Take-Off Analysis

    # TODO: Add Take-Off Analysis

    # Run Climb Analysis
    climb_analysis = Climb(Aircraft)
    H = climb_analysis.get_h_max(delta_t=climb_time)
    print("H Climb: %.1f m" % H)

    # Run Cruise Analysis
    cruise_analysis = HorizontalFlight(Aircraft)
    cruise_analysis.CL_start = 0.06
    V_max = cruise_analysis.get_maximum_velocity()
    print("Maximum Velocity: %.1f m/s" %  V_max)
    cruise_analysis.plot_fv_diagramm()