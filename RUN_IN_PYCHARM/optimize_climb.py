import matplotlib.pyplot as plt
import numpy as np
from vehicle_setup import vehicle_setup

from mace.aero.flightconditions.climb import Climb
from mace.aero.flightconditions.horizontalflight import HorizontalFlight
from mace.aero.implementations.avl import (
    geometry_and_mass_files_v2 as geometry_and_mass_files,
)
from mace.domain.parser import PlaneParser

from mace.mass.mass import get_mass_plane

if __name__ == "__main__":
    # Define Analysis
    climb_time = 50.0

    # Define Aircraft Geometry
    Aircraft = vehicle_setup()

    mass = get_mass_plane(Aircraft)

    # Build AVL input files
    geometry_and_mass_files.GeometryFile(Aircraft).build_geometry_file()
    geometry_and_mass_files.MassFile(Aircraft).build_mass_file()
    

    # Run Climb Analysis
    climb_analysis = Climb(Aircraft)

    # Plot Results
    fig = plt.figure(dpi=400)
    ax = fig.add_subplot(111)

    flap_angles = [0.0, 2.0, 4.0, 10.0]

    for i, flap_angle in enumerate(flap_angles):

        print("Analysis %s of %s" % (i + 1, len(flap_angles)))

        climb_analysis.flap_angle = flap_angle
        climb_analysis.cl_start = 0.4
        climb_analysis.cl_step = 0.1
        climb_data = climb_analysis.evaluate()

        ax.plot(
            climb_data[:, 1], climb_data[:, 2], label=f"Flap Angle = {flap_angle} deg"
        )

    ax.set_xlabel("V [m/s]")
    ax.set_ylabel("V_z [m/s]")
    plt.legend()
    plt.grid()
    plt.tick_params(which="major", labelsize=6)
    plt.title("Climb Analysis", fontsize=10)
    plt.show()
