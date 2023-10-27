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
    logging.basicConfig(level=logging.INFO)
    payload = 10.5
    vehicle = Vehicle()
    vehicle.payload = payload
    vehicle.mass = 0.
    logging.debug("M Empty: %.2f kg" % vehicle.mass)
    vehicle.mass += vehicle.payload

    vehicle.center_of_gravity = [0.112, 0.0, 0.0]

    main_wing_construction = WingSegmentBuild(
        build_type="Negativ", surface_weight=0.380
    )
    empennage_construction = WingSegmentBuild(
        build_type="Positiv", surface_weight=0.08, core_material_density=30.0
    )

    ####################################################################################################################
    # MAIN WING
    main_wing = Wing()
    main_wing.tag = "main_wing"
    main_wing.origin = [0, 0, 0]
    main_wing.airfoil = "acc22"
    main_wing.angle = 2.0
    main_wing.symmetric = True

    # Inner segment
    segment = WingSegment()
    segment.span = 0.9819
    segment.inner_chord = 0.383
    segment.outer_chord = 0.355
    segment.dihedral = 2
    segment.control = True
    segment.inner_x_offset = 0.
    segment.outer_x_offset = 0.012
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    # Mid segment
    segment = WingSegment()
    segment.span = 0.6217
    segment.inner_chord = 0.355
    segment.outer_chord = 0.249
    segment.dihedral = 4
    segment.control = True
    segment.inner_x_offset = 0.012
    segment.outer_x_offset = 0.040 + 0.012
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    # Outer segment
    segment = WingSegment()
    segment.span = 0.348
    segment.inner_chord = 0.249
    segment.outer_chord = 0.122
    segment.dihedral = 4
    segment.outer_twist = 0
    segment.control = True
    segment.inner_x_offset = 0.040 + 0.012
    segment.outer_x_offset = 0.072 + 0.04 + 0.012
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    # Resize Wing
    main_wing.build(resize_x_offset_from_hinge_angle=False, resize_areas=False)

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
    horizontal_stabilizer.origin = [1.465, 0, 0.36]
    horizontal_stabilizer.airfoil = "ht14"

    # Segment
    segment = WingSegment()
    segment.span = 0.429
    segment.inner_chord = 0.189
    segment.outer_chord = 0.1124
    segment.flap_chord_ratio = 0.4
    segment.inner_x_offset = 0.
    segment.outer_x_offset = 0.049
    segment.dihedral = 0.
    segment.wsb = empennage_construction
    horizontal_stabilizer.add_segment(segment)


    horizontal_stabilizer.build(resize_x_offset_from_hinge_angle=False, resize_areas=False)

    vehicle.add_wing("horizontal_stabilizer", horizontal_stabilizer)
    ####################################################################################################################
    # VERTICAL STABILIZER
    vertical_stabilizer = Wing()
    vertical_stabilizer.tag = "vertical_stabilizer"
    vertical_stabilizer.origin = [1.44, 0, 0]
    vertical_stabilizer.vertical = True
    vertical_stabilizer.symmetric = False
    vertical_stabilizer.airfoil = "ht14"
    vertical_stabilizer.hinge_angle = 0

    # Segment
    segment = WingSegment()
    segment.span = 0.36
    segment.inner_chord = 0.2
    segment.outer_chord = 0.19
    segment.outer_x_offset = 0.02
    segment.flap_chord_ratio = 0.4
    segment.wsb = empennage_construction
    vertical_stabilizer.add_segment(segment)

    # Resize Wing
    vertical_stabilizer.build(resize_x_offset_from_hinge_angle=False, resize_areas=False)

    vehicle.add_wing("vertical_stabilizer", vertical_stabilizer)
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
        origin=[-0.372, 0, 0.0], shape="rectangular", width=0.04, height=0.04
    )
    fuselage.add_segment(
        origin=[1.465, 0, 0.0], shape="rectangular", width=0.04, height=0.04
    )

    fuselage.area_specific_mass = 0.616
    fuselage.build()
    logging.debug("f_length: %.3f m" % fuselage.length)
    vehicle.add_fuselage("fuselage", fuselage)
    ####################################################################################################################
    # CARGO BAY
    cargo_bay = Fuselage()

    # Cargo bay fist segment
    x = 0.
    y = 0
    z = -0.1
    width = 0.1
    height = 0.2
    cargo_bay.add_segment(
        origin=[x, y, z], shape="rectangular", width=width, height=height
    )

    # Cargo bay second segment
    x = 0.36
    z = -0.1
    width = 0.1
    height = 0.2
    cargo_bay.add_segment(
        origin=[x, y, z], shape="rectangular", width=width, height=height
    )

    
    cargo_bay.area_specific_mass = 0.6
    cargo_bay.build()
    logging.debug("f_length: %.3f m" % cargo_bay.length)
    vehicle.add_fuselage("cargo_bay", cargo_bay)
    ####################################################################################################################
    # LANDING GEAR
    landing_gear = LandingGear()
    landing_gear.height = 0.25

    # Nose wheel
    wheel1 = Wheel()
    wheel1.diameter = 0.1
    wheel1.drag_correction = 1.5
    wheel1.origin = np.array(
        [- 0.1, 0.0, -0.25]
    )
    landing_gear.add_wheel(wheel1)

    # Main wheels
    wheel2 = Wheel()
    wheel2.diameter = 0.12
    wheel2.drag_correction = 1.5
    wheel2.origin = np.array(
        [
            0.25,
            0.145,
            -0.24,
        ]
    )
    landing_gear.add_wheel(wheel2)

    # Main wheels
    wheel3 = Wheel()
    wheel3.diameter = wheel2.diameter
    wheel3.drag_correction = 1.5
    wheel3.origin = np.array(
        [0.25, -0.145, -0.24]
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
        "Battery", 0.436, np.array([0, 0, 0])
    )  # SLS Quantum 2200mAh 3S 60C : 201gr inkl. Kabel
    vehicle.add_misc(
        "Servo+Reciever", 0.160, np.array([0, 0, 0])
    )  # 6 Servos a 12gr + 20gr Kabel
    vehicle.add_misc(
        "Motor+Prop+ESC", 0.298, np.array([0, 0, 0])
    )  # T-Motor AT2826 900KV : 175gr inkl. Kabel
    vehicle.add_misc(
        "Screws+Cables+Accessories", 0.110, np.array([0, 0, 0])
    )  # T-Motor AT2826 900KV : 175gr inkl. Kabel

    ####################################################################################################################

    vehicle.build()
    vehicle.print_mass_table()
    vehicle.get_reference_values()
    vehicle.get_stability_derivatives()
    vehicle.transport_box_dimensions()

    logging.debug(f"Vehicle Mass: {vehicle.mass:.3f}")
    # PLOT
    if __name__ == "__main__":
        vehicle.plot_vehicle(azim=230, elev=30)

    return vehicle


if __name__ == "__main__":
    vehicle_setup()
