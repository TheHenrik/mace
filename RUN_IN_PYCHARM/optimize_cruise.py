import logging

import matplotlib.pyplot as plt
import numpy as np
from vehicle_setup import vehicle_setup

from mace.aero.flightconditions.climb import Climb
from mace.aero.flightconditions.horizontalflight import HorizontalFlight
from mace.aero.implementations.avl import (
    geometry_and_mass_files_v2 as geometry_and_mass_files,
)
from mace.domain.parser import PlaneParser

if __name__ == "__main__":
    # Define Aircraft Geometry
    Aircraft = vehicle_setup()

    # Build AVL input files
    geometry_and_mass_files.GeometryFile(Aircraft).build_geometry_file()
    geometry_and_mass_files.MassFile(Aircraft).build_mass_file()

    # Run Climb Analysis
    cruise_analysis = HorizontalFlight(Aircraft)

    # Plot Results
    fig = plt.figure(dpi=400)
    ax = fig.add_subplot(111)

    flap_angles = [-4.0, -2.0, 0.0, 2.0, 4.0]
    max_velocity = np.zeros(len(flap_angles))

    for i, flap_angle in enumerate(flap_angles):

        logging.debug("Analysis %s of %s" % (i + 1, len(flap_angles)))

        cruise_analysis.flap_angle = flap_angle
        cruise_analysis.cl_start = 0.05
        cruise_analysis.cl_step = 0.04
        cruise_analysis.cl_end = 0.4
        cruise_analysis.fv_diagramm()
        max_velocity[i] = cruise_analysis.get_maximum_velocity()

    ax.plot(flap_angles, max_velocity)

    ax.set_xlabel("Flap angle [deg]")
    ax.set_ylabel("V_max [m/s]")
    plt.grid()
    plt.tick_params(which="major", labelsize=6)
    plt.title("Cruise Analysis", fontsize=10)
    plt.show()
