from vehicle_setup import vehicle_setup
from mace.domain.parser import PlaneParser
from mace.aero.flightconditions.glidingflight_jf import GlidingFlight
from mace.aero.implementations.avl import (
    geometry_and_mass_files_v2 as geometry_and_mass_files,
)
import matplotlib.pyplot as plt
import numpy as np


if __name__ == "__main__":
    # Define Aircraft Geometry
    Aircraft = vehicle_setup()

    # Build AVL input files
    geometry_and_mass_files.GeometryFile(Aircraft).build_geometry_file()
    geometry_and_mass_files.MassFile(Aircraft).build_mass_file()

    # Run Climb Analysis
    efficiency_analysis = GlidingFlight(Aircraft)

    # Plot Results
    fig = plt.figure(dpi=400)
    ax = fig.add_subplot(111)

    flap_angles = [2.0, 4.0, 6.0, 10.0]

    for i, flap_angle in enumerate(flap_angles):

        print("Analysis %s of %s" % (i + 1, len(flap_angles)))

        efficiency_analysis.flap_angle = flap_angle
        efficiency_analysis.cl_start = 0.2
        efficiency_analysis.cl_step = 0.1
        efficiency_analysis.cl_end = 1.2
        climb_data = efficiency_analysis.evaluate()

        ax.plot(
            climb_data[:, 2], climb_data[:, 3], label=f"Flap Angle = {flap_angle-2} deg"
        )

    ax.set_xlabel("V [m/s]")
    ax.set_ylabel("V_z [m/s]")
    plt.legend()
    plt.grid()
    plt.tick_params(which="major", labelsize=6)
    plt.title("Climb Analysis", fontsize=10)
    plt.show()
