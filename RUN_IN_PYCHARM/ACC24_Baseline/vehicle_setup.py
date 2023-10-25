import logging
import os
from pathlib import Path

import numpy as np

from mace.aero.implementations.avl.athenavortexlattice import AVL
from mace.domain.fuselage import Fuselage, FuselageSegment
from mace.domain.landing_gear import LandingGear, Strut, Wheel
from mace.domain.vehicle import Vehicle
from mace.domain.wing import Wing, WingSegment, WingSegmentBuild


def vehicle_setup(payload=3.0, span=3.0, aspect_ratio=15.0, airfoil="ag19") -> Vehicle:
    vehicle = Vehicle()
    vehicle.payload = payload
    vehicle.mass = 2.0 * (span / 3.0) ** 2
    logging.debug("M Empty: %.2f kg" % vehicle.mass)
    vehicle.mass += vehicle.payload

    vehicle.center_of_gravity = [0.112, 0.0, 0.0]

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
    main_wing.airfoil = airfoil
    main_wing.angle = 2.0
    main_wing.symmetric = True

    # Inner segment
    segment = WingSegment()
    segment.span = 0.45
    segment.inner_chord = 1.0
    segment.outer_chord = 0.9
    segment.dihedral = 1
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    # Mid segment
    segment = WingSegment()
    segment.span = 0.3
    segment.inner_chord = 0.9
    segment.outer_chord = 0.7
    segment.dihedral = 5
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    # Outer segment
    segment = WingSegment()
    segment.span = 0.15
    segment.inner_chord = 0.7
    segment.outer_chord = 0.4
    segment.dihedral = 5
    segment.outer_twist = 0
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    # Outer segment
    segment = WingSegment()
    segment.span = 0.05
    segment.inner_chord = 0.4
    segment.outer_chord = 0.2
    segment.dihedral = 5
    segment.outer_twist = 0
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    # Resize Wing
    main_wing.hinge_angle = 1.0
    main_wing.span = span
    main_wing.aspect_ratio = aspect_ratio
    main_wing.build(resize_x_offset_from_hinge_angle=True)

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
    horizontal_stabilizer.origin = [b_ref * 0.35, 0, 0.0]
    horizontal_stabilizer.airfoil = "ht14"

    # Segment
    segment = WingSegment()
    segment.inner_chord = 0.25
    segment.outer_chord = 0.228
    segment.flap_chord_ratio = 0.4
    segment.dihedral = 40.0
    segment.wsb = empennage_construction
    horizontal_stabilizer.add_segment(segment)

    # Segment
    segment = WingSegment()
    segment.inner_chord = 0.228
    segment.outer_chord = 0.12
    segment.flap_chord_ratio = 0.4
    segment.dihedral = 40.0
    segment.wsb = empennage_construction
    horizontal_stabilizer.add_segment(segment)

    # Resize Wing
    l_ht = horizontal_stabilizer.origin[0] - main_wing.origin[0]

    v_ht = 0.75  # 0.583*2 * 1.414
    horizontal_stabilizer.aspect_ratio = 7.0
    horizontal_stabilizer.get_stabilizer_area_from_volume_coefficient(
        v_ht, l_ht, S_ref, MAC
    )

    horizontal_stabilizer.build(resize_x_offset_from_hinge_angle=True)

    vehicle.add_wing("horizontal_stabilizer", horizontal_stabilizer)
    ####################################################################################################################
    # PROPULSION
    tool_path = Path(__file__).resolve().parents[2]
    prop_surrogate_path = os.path.join(
        tool_path, "data", "prop_surrogates", "aeronaut14x8.csv"
    )
    vehicle.propulsion.thrust = np.loadtxt(prop_surrogate_path, skiprows=1)
    ####################################################################################################################
    # FUSELAGE
    fuselage = Fuselage()

    fuselage.add_segment(
        origin=[-b_ref * 0.1, 0, 0.0], shape="rectangular", width=0.04, height=0.04
    )
    fuselage.add_segment(
        origin=[b_ref * 0.35, 0, 0.0], shape="rectangular", width=0.04, height=0.04
    )

    fuselage.build()
    logging.debug("f_length: %.3f m" % fuselage.length)
    vehicle.add_fuselage("fuselage", fuselage)
    ####################################################################################################################
    # CARGO BAY
    cargo_bay = Fuselage()
    Height = 0.25
    cargo_bay_length = np.ceil(vehicle.payload / 0.17 / 3) * 0.06
    logging.debug("cargo_bay_length: %.3f m" % cargo_bay_length)
    cargo_bay_height = 0.06
    cargo_bay_width = 0.2
    x_minus_offset = vehicle.center_of_gravity[0] - cargo_bay_length / 2
    x_plus_offset = vehicle.center_of_gravity[0] + cargo_bay_length / 2

    # Cargo bay fist segment
    x = x_minus_offset - 0.05
    y = 0
    z = -Height + cargo_bay_height / 2 + 0.05
    width = cargo_bay_width * 0.5
    height = cargo_bay_height * 0.5
    cargo_bay.add_segment(
        origin=[x, y, z], shape="rectangular", width=width, height=height
    )

    # Cargo bay second segment
    x = x_minus_offset
    z = -Height + cargo_bay_height / 2 + 0.05
    width = cargo_bay_width
    height = cargo_bay_height
    cargo_bay.add_segment(
        origin=[x, y, z], shape="rectangular", width=width, height=height
    )

    # Cargo bay third segment
    x = x_plus_offset
    z = -Height + cargo_bay_height / 2 + 0.05
    width = cargo_bay_width
    height = cargo_bay_height
    cargo_bay.add_segment(
        origin=[x, y, z], shape="rectangular", width=width, height=height
    )

    # Cargo bay fourth segment
    x = x_plus_offset + 0.1
    z = -Height + cargo_bay_height / 2 + 0.05
    width = cargo_bay_width * 0.2
    height = cargo_bay_height * 0.2
    cargo_bay.add_segment(
        origin=[x, y, z], shape="rectangular", width=width, height=height
    )

    cargo_bay.build()
    logging.debug("f_length: %.3f m" % cargo_bay.length)
    vehicle.add_fuselage("cargo_bay", cargo_bay)
    ####################################################################################################################
    # LANDING GEAR
    landing_gear = LandingGear()
    landing_gear.height = Height

    # Nose wheel
    wheel1 = Wheel()
    wheel1.diameter = 0.1
    wheel1.drag_correction = 1.5
    wheel1.origin = np.array(
        [x_minus_offset - 0.1, 0.0, -(Height - wheel1.diameter / 2.0)]
    )
    landing_gear.add_wheel(wheel1)

    # Main wheels
    wheel2 = Wheel()
    wheel2.diameter = 0.16
    wheel2.drag_correction = 1.5
    wheel2.origin = np.array(
        [
            vehicle.center_of_gravity[0] + 0.1,
            cargo_bay_width / 2,
            -(Height - wheel2.diameter / 2.0),
        ]
    )
    landing_gear.add_wheel(wheel2)

    # Main wheels
    wheel3 = Wheel()
    wheel3.diameter = wheel2.diameter
    wheel3.drag_correction = 1.5
    wheel3.origin = np.array(
        [vehicle.center_of_gravity[0] + 0.1, -wheel2.origin[1], wheel2.origin[2]]
    )
    wheel3.origin[1] = -wheel2.origin[1]
    landing_gear.add_wheel(wheel3)

    # Landing gear strut
    strut = Strut()
    strut.mass = 0.08
    strut.origin = np.array([vehicle.center_of_gravity[0] + 0.1, 0, wheel2.origin[2]])
    landing_gear.add_strut(strut)

    landing_gear.finalize()

    vehicle.landing_gear = landing_gear

    ####################################################################################################################

    vehicle.add_misc(
        "Battery", 0.201, np.array([0, 0, 0])
    )  # SLS Quantum 2200mAh 3S 60C : 201gr inkl. Kabel
    vehicle.add_misc("ESC", 0.093, np.array([0, 0, 0]))  # YGE 95A : 93gr inkl. Kabel
    vehicle.add_misc(
        "Servo", 0.092, np.array([0, 0, 0])
    )  # 6 Servos a 12gr + 20gr Kabel
    vehicle.add_misc(
        "Receiver", 0.010, np.array([0, 0, 0])
    )  # bel. Hersteller circa 10gr
    vehicle.add_misc(
        "Motor", 0.175, np.array([0, 0, 0])
    )  # T-Motor AT2826 900KV : 175gr inkl. Kabel

    ####################################################################################################################

    vehicle.build()
    vehicle.print_mass_table()
    vehicle.get_reference_values()
    vehicle.get_stability_derivatives()
    vehicle.transport_box_dimensions()

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
