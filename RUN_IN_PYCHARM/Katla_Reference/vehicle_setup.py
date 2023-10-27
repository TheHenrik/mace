import logging
import os
from pathlib import Path

import numpy as np

from mace.aero.implementations.avl.athenavortexlattice import AVL
from mace.domain.fuselage import Fuselage, FuselageSegment
from mace.domain.landing_gear import LandingGear, Strut, Wheel
from mace.domain.vehicle import Vehicle
from mace.domain.wing import Wing, WingSegment, WingSegmentBuild


def vehicle_setup() -> Vehicle:
    vehicle = Vehicle()
    vehicle.payload = 0
    vehicle.mass = 2.25

    vehicle.center_of_gravity = [0.088, 0.0, 0.0]

    main_wing_construction = WingSegmentBuild(
        build_type="Negativ", surface_weight=0.400
    )
    empennage_construction = WingSegmentBuild(
        build_type="Positiv", surface_weight=0.150, core_material_density=37.0
    )

    ####################################################################################################################
    # MAIN WING
    main_wing = Wing()
    main_wing.tag = "main_wing"
    main_wing.origin = [0, 0, 0]
    main_wing.airfoil = "jx-gp-055"
    main_wing.angle = 2.0
    main_wing.symmetric = True

    segment = WingSegment()
    segment.span = 0.5
    segment.inner_chord = 0.235
    segment.outer_chord = 0.222
    segment.dihedral = 3
    segment.inner_x_offset = 0.0
    segment.outer_x_offset = -0.002
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.2
    segment.inner_chord = 0.222
    segment.outer_chord = 0.210
    segment.dihedral = 3
    segment.inner_x_offset = -0.002
    segment.outer_x_offset = 0.002
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.2
    segment.inner_chord = 0.210
    segment.outer_chord = 0.197
    segment.dihedral = 3
    segment.inner_x_offset = 0.004
    segment.outer_x_offset = 0.003
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.2
    segment.inner_chord = 0.197
    segment.outer_chord = 0.174
    segment.dihedral = 3
    segment.inner_x_offset = 0.003
    segment.outer_x_offset = 0.013
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.15
    segment.inner_chord = 0.174
    segment.outer_chord = 0.144
    segment.dihedral = 3
    segment.inner_x_offset = 0.013
    segment.outer_x_offset = 0.028
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.1
    segment.inner_chord = 0.144
    segment.outer_chord = 0.115
    segment.dihedral = 3
    segment.inner_x_offset = 0.028
    segment.outer_x_offset = 0.045
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.07
    segment.inner_chord = 0.115
    segment.outer_chord = 0.08
    segment.dihedral = 3
    segment.inner_x_offset = 0.045
    segment.outer_x_offset = 0.068
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.05
    segment.inner_chord = 0.08
    segment.outer_chord = 0.05
    segment.dihedral = 3
    segment.inner_x_offset = 0.068
    segment.outer_x_offset = 0.09
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    main_wing.build(resize_areas=False, resize_x_offset_from_hinge_angle=False)

    # Get wing properties
    S_ref = main_wing.reference_area
    MAC = main_wing.mean_aerodynamic_chord
    b_ref = main_wing.span
    AR = main_wing.aspect_ratio

    vehicle.add_wing("main_wing", main_wing)
    ####################################################################################################################
    # HORIZONTAL STABILIZER
    horizontal_stabilizer = Wing()
    horizontal_stabilizer.tag = "horizontal_stabilizer"
    horizontal_stabilizer.origin = [0.891, 0, 0.0]
    horizontal_stabilizer.airfoil = "ht14"

    # Segment
    segment = WingSegment()
    segment.span = 0.1
    segment.inner_chord = 0.123
    segment.outer_chord = 0.12
    segment.dihedral = 40.0
    segment.inner_x_offset = 0.0
    segment.outer_x_offset = 0.001
    segment.wsb = empennage_construction
    horizontal_stabilizer.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.05
    segment.inner_chord = 0.12
    segment.outer_chord = 0.117
    segment.dihedral = 40.0
    segment.inner_x_offset = 0.001
    segment.outer_x_offset = 0.003
    segment.wsb = empennage_construction
    horizontal_stabilizer.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.05
    segment.inner_chord = 0.117
    segment.outer_chord = 0.111
    segment.dihedral = 40.0
    segment.inner_x_offset = 0.003
    segment.outer_x_offset = 0.007
    segment.wsb = empennage_construction
    horizontal_stabilizer.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.05
    segment.inner_chord = 0.111
    segment.outer_chord = 0.1
    segment.dihedral = 40.0
    segment.inner_x_offset = 0.007
    segment.outer_x_offset = 0.014
    segment.wsb = empennage_construction
    horizontal_stabilizer.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.05
    segment.inner_chord = 0.1
    segment.outer_chord = 0.077
    segment.dihedral = 40.0
    segment.inner_x_offset = 0.014
    segment.outer_x_offset = 0.03
    segment.wsb = empennage_construction
    horizontal_stabilizer.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.05
    segment.inner_chord = 0.077
    segment.outer_chord = 0.05
    segment.dihedral = 40.0
    segment.inner_x_offset = 0.03
    segment.outer_x_offset = 0.05
    segment.wsb = empennage_construction
    horizontal_stabilizer.add_segment(segment)

    # horizontal_stabilizer.reference_area = 0.08
    horizontal_stabilizer.build(
        resize_areas=False, resize_x_offset_from_hinge_angle=False
    )

    vehicle.add_wing("horizontal_stabilizer", horizontal_stabilizer)

    ####################################################################################################################
    # FUSELAGE
    fuselage = Fuselage()

    fuselage.add_segment(
        origin=[-0.35, 0, 0.0], shape="rectangular", width=0.03, height=0.04
    )
    fuselage.add_segment(
        origin=[1.01, 0, 0.0], shape="rectangular", width=0.02, height=0.02
    )

    fuselage.build()
    logging.debug("f_length: %.3f m" % fuselage.length)
    vehicle.add_fuselage("fuselage", fuselage)
    ####################################################################################################################

    ####################################################################################################################

    # vehicle.build()
    vehicle.get_reference_values()
    vehicle.get_stability_derivatives()
    vehicle.transport_box_dimensions()

    for wing in vehicle.wings.values():
        S = wing.reference_area
        ac = wing.neutral_point
        logging.debug("%s %.1f sqdm" % (wing.tag, S * 100))
        logging.debug(ac)

    logging.debug("Vehicle Mass", round(vehicle.mass, 3))
    # PLOT
    if __name__ == "__main__":
        vehicle.plot_vehicle(azim=180, elev=0)
        vehicle.plot_vehicle(azim=0, elev=90)
        vehicle.plot_vehicle(azim=90, elev=0)
    vehicle.plot_vehicle(azim=230, elev=30)

    return vehicle


if __name__ == "__main__":
    vehicle_setup()
