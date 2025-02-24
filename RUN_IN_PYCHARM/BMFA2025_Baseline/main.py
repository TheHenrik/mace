from vehicle_setup import vehicle_setup
from mace.aero.flightconditions.takeoff_jf import TakeOff
from mace.aero.implementations.avl import (geometry_and_mass_files_v2 as geometry_and_mass_files)
if __name__ == '__main__':
    empty_ac = vehicle_setup(center_wing_span=0., add_payload=0.)

    mass_file = geometry_and_mass_files.MassFile(empty_ac)
    mass_file.build_mass_file()

    geometry_file = geometry_and_mass_files.GeometryFile(empty_ac)
    geometry_file.z_sym = 1
    geometry_file.build_geometry_file()

    # Run Take-Off Analysis
    takeoff_analysis = TakeOff(empty_ac)
    takeoff_analysis.mu = 0.125
    takeoff_analysis.flap_angle = 12.0
    takeoff_analysis.t_step = 0.1
    takeoff_analysis.cl_safety_factor = 1.3
    takeoff_analysis.v_wind = 0.
    takeoff_analysis.v_start_counter = 0
    takeoff_analysis.show_plot = False
    takeoff_analysis.cl_max_factor = 1.0
    take_off_length, take_off_time = takeoff_analysis.evaluate()
    print('Empty A/C')
    print(' Take-Off Length: %.1f m' % take_off_length)

    full_ac = vehicle_setup(center_wing_span=0.75, add_payload=3.8)

    mass_file = geometry_and_mass_files.MassFile(full_ac)
    mass_file.build_mass_file()

    geometry_file = geometry_and_mass_files.GeometryFile(full_ac)
    geometry_file.z_sym = 1
    geometry_file.build_geometry_file()

    # Run Take-Off Analysis
    takeoff_analysis = TakeOff(full_ac)
    takeoff_analysis.mu = 0.125
    takeoff_analysis.flap_angle = 12.0
    takeoff_analysis.t_step = 0.3
    takeoff_analysis.cl_safety_factor = 1.3
    takeoff_analysis.v_wind = 0.
    takeoff_analysis.v_start_counter = 0
    takeoff_analysis.show_plot = False
    takeoff_analysis.cl_max_factor = 1.0
    take_off_length, take_off_time = takeoff_analysis.evaluate()
    print('Full A/C')
    print(' Take-Off Length: %.1f m' % take_off_length)

