import logging
import os
from pathlib import Path

import numpy as np

from mace.aero.implementations.avl.athenavortexlattice import AVL
from mace.domain.battery import Battery
from mace.domain.fuselage import Fuselage, FuselageSegment
from mace.domain.landing_gear import LandingGear, Strut, Wheel
from mace.domain.propeller import Propeller
from mace.domain.vehicle import Vehicle
from mace.domain.wing import Wing, WingSegment, WingSegmentBuild


def vehicle_setup(
    payload=0.,
    wing_area=0.65, #ACC17=1.22, ACC22=0.61
    aspect_ratio=10., #ACC17=12.52, ACC22=9.6
    airfoil="LAK24_v3", #acc22
    num_fowler_segments=0, #ACC17=0, ACC22=4
    battery_capacity=3.,
    propeller="freudenthaler14x8",
    main_wing_x=0.20,
) -> Vehicle:

    vehicle = Vehicle()
    vehicle.payload = payload
    vehicle.center_of_gravity_payload = np.array([0.390, 0.0, 0.0])

    vehicle.mass = 2.0
    vehicle.mass += vehicle.payload

    vehicle.center_of_gravity = [0.112, 0.0, 0.0]

    main_wing_construction = WingSegmentBuild(
        build_type="Negativ", surface_weight=0.190
    )
    empennage_construction = WingSegmentBuild(
        build_type="Positiv", surface_weight=0.08, core_material_density=37.0
    )
    pylon_construction = WingSegmentBuild(build_type="Negativ", surface_weight=0.500)

    ####################################################################################################################
    # MAIN WING
    main_wing = Wing()
    main_wing.tag = "main_wing"
    main_wing.origin = [main_wing_x, 0, -0.04]
    main_wing.airfoil = airfoil
    main_wing.angle = 2.0
    main_wing.symmetric = True

    segment = WingSegment()
    segment.flap_chord_ratio = 0.25
    segment.span = 0.25
    segment.inner_chord = 0.222
    segment.outer_chord = 0.222
    segment.dihedral = 0
    segment.inner_x_offset = 0.0
    segment.outer_x_offset = -0.001
    segment.control = True
    if num_fowler_segments >= 1:
        segment.control_name = "fowler"
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.flap_chord_ratio = 0.25
    segment.span = 0.25
    segment.inner_chord = 0.222
    segment.outer_chord = 0.222
    segment.dihedral = 0
    segment.inner_x_offset = -0.001
    segment.outer_x_offset = -0.002
    segment.control = True
    if num_fowler_segments >= 1:
        segment.control_name = "fowler"
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.flap_chord_ratio = 0.25
    segment.span = 0.2
    segment.inner_chord = 0.222
    segment.outer_chord = 0.210
    segment.dihedral = 5
    segment.inner_x_offset = -0.002
    segment.outer_x_offset = 0.002
    segment.control = True
    if num_fowler_segments >= 2:
        segment.control_name = "fowler"
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.flap_chord_ratio = 0.25
    segment.span = 0.2
    segment.inner_chord = 0.210
    segment.outer_chord = 0.197
    segment.dihedral = 5
    segment.inner_x_offset = 0.004
    segment.outer_x_offset = 0.003
    segment.control = True
    if num_fowler_segments >= 2:
        segment.control_name = "fowler"
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.flap_chord_ratio = 0.25
    segment.span = 0.2
    segment.inner_chord = 0.197
    segment.outer_chord = 0.174
    segment.dihedral = 5
    segment.inner_x_offset = 0.003
    segment.outer_x_offset = 0.013
    segment.control = True
    if num_fowler_segments >= 3:
        segment.control_name = "fowler"
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.flap_chord_ratio = 0.25
    segment.span = 0.15
    segment.inner_chord = 0.174
    segment.outer_chord = 0.144
    segment.dihedral = 5
    segment.inner_x_offset = 0.013
    segment.outer_x_offset = 0.028
    segment.control = True
    if num_fowler_segments >= 3:
        segment.control_name = "fowler"
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.flap_chord_ratio = 0.25
    segment.span = 0.1
    segment.inner_chord = 0.144
    segment.outer_chord = 0.115
    segment.dihedral = 5
    segment.inner_x_offset = 0.028
    segment.outer_x_offset = 0.045
    segment.control = True
    if num_fowler_segments >= 4:
        segment.control_name = "fowler"
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.flap_chord_ratio = 0.25
    segment.span = 0.07
    segment.inner_chord = 0.115
    segment.outer_chord = 0.08
    segment.dihedral = 5
    segment.inner_x_offset = 0.045
    segment.outer_x_offset = 0.068
    segment.control = True
    if num_fowler_segments >= 4:
        segment.control_name = "fowler"
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.flap_chord_ratio = 0.25
    segment.span = 0.05
    segment.inner_chord = 0.08
    segment.outer_chord = 0.05
    segment.dihedral = 5
    segment.inner_x_offset = 0.068
    segment.outer_x_offset = 0.09
    segment.control = True
    if num_fowler_segments >= 4:
        segment.control_name = "fowler"
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    # Resize Wing
    main_wing.hinge_angle = 0.
    # main_wing.span = span
    main_wing.reference_area = wing_area
    main_wing.aspect_ratio = aspect_ratio
    main_wing.build(resize_x_offset_from_hinge_angle=True, resize_areas=True)

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
    horizontal_stabilizer.origin = [1.3, 0, 0]
    horizontal_stabilizer.airfoil = "ht14"

    # Segment
    segment = WingSegment()
    segment.inner_chord = 1.
    segment.outer_chord = 0.8
    segment.span = 0.6
    segment.flap_chord_ratio = 0.4
    segment.wsb = empennage_construction
    horizontal_stabilizer.add_segment(segment)

    # Segment
    segment = WingSegment()
    segment.inner_chord = 0.8
    segment.outer_chord = 0.4
    segment.span = 0.4
    segment.flap_chord_ratio = 0.4
    segment.wsb = empennage_construction
    horizontal_stabilizer.add_segment(segment)

    # Resize Wing
    horizontal_stabilizer.aspect_ratio = 5.
    horizontal_stabilizer.hinge_angle = 0.
    l_ht = horizontal_stabilizer.origin[0] - main_wing.origin[0]
    v_ht = 0.45
    horizontal_stabilizer.get_stabilizer_area_from_volume_coefficient(v_ht, l_ht, S_ref, MAC)
    horizontal_stabilizer.build(resize_x_offset_from_hinge_angle=True)

    vehicle.add_wing("horizontal_stabilizer", horizontal_stabilizer)

    ####################################################################################################################
    # VERTICAL STABILIZER
    vertical_stabilizer = Wing()
    vertical_stabilizer.tag = "vertical_stabilizer"
    vertical_stabilizer.origin = [1.3, 0, 0]
    vertical_stabilizer.vertical = True
    vertical_stabilizer.symmetric = False
    vertical_stabilizer.airfoil = "ht14"
    vertical_stabilizer.hinge_angle = 0

    # Segment
    segment = WingSegment()
    segment.inner_chord = 1.
    segment.outer_chord = 0.8
    segment.span = 0.6
    segment.flap_chord_ratio = 0.4
    segment.wsb = empennage_construction
    vertical_stabilizer.add_segment(segment)

    # Segment
    segment = WingSegment()
    segment.inner_chord = 0.8
    segment.outer_chord = 0.4
    segment.span = 0.4
    segment.flap_chord_ratio = 0.4
    segment.wsb = empennage_construction
    vertical_stabilizer.add_segment(segment)

    # Resize Wing
    vertical_stabilizer.aspect_ratio = 1.5

    l_vt = vertical_stabilizer.origin[0] - main_wing.origin[0]
    v_vt = 0.027

    vertical_stabilizer.hinge_angle = 0.
    vertical_stabilizer.get_stabilizer_area_from_volume_coefficient(v_vt, l_vt, S_ref, b_ref)
    vertical_stabilizer.build(resize_x_offset_from_hinge_angle=True)

    vehicle.add_wing("vertical_stabilizer", vertical_stabilizer)
    ####################################################################################################################
    # PROPULSION
    prop = Propeller(propeller)
    vehicle.propeller = prop

    battery = Battery()
    battery.capacity = battery_capacity
    battery.origin = np.array([-0.1, 0, 0])

    vehicle.battery = battery
    ####################################################################################################################
    # FUSELAGE
    fuselage = Fuselage()

    fuselage.add_segment(
        origin=[-0.25, 0, 0.0], shape="rectangular", width=0.04, height=0.04
    )
    fuselage.add_segment(
        origin=[-0.15, 0, 0.0], shape="rectangular", width=0.09, height=0.06
    )
    fuselage.add_segment(
        origin=[0., 0, 0], shape="rectangular", width=0.11, height=0.07
    )
    fuselage.add_segment(
        origin=[0.85, 0, 0], shape="rectangular", width=0.11, height=0.07
    )
    fuselage.add_segment(
        origin=[0.85 + 0.2, 0, 0.0], shape="rectangular", width=0.09, height=0.06
    )
    fuselage.add_segment(
        origin=[0.85 + 0.3, 0, 0.0], shape="rectangular", width=0.04, height=0.04
    )
    fuselage.add_segment(
        origin=[0.85 + 0.6, 0, 0.0], shape="rectangular", width=0.04, height=0.04
    )

    fuselage.area_specific_mass = 0.616
    fuselage.build()
    logging.debug("f_length: %.3f m" % fuselage.length)
    vehicle.add_fuselage("fuselage", fuselage)
    ####################################################################################################################
    # LANDING GEAR
    Height = 0.3
    landing_gear = LandingGear()
    landing_gear.height = Height

    # Nose wheel
    wheel1 = Wheel()
    wheel1.diameter = 0.09
    wheel1.drag_correction = 0. #3.
    wheel1.origin = np.array(
        [1.35, 0.0, -0.07]
    )
    landing_gear.add_wheel(wheel1)

    # Main wheels
    wheel2 = Wheel()
    wheel2.diameter = 0.14
    wheel2.drag_correction = 0. # 3.
    wheel2.origin = np.array(
        [
            main_wing_x + 0.1,
            0.25,
            -(Height - wheel2.diameter / 2.0),
        ]
    )
    landing_gear.add_wheel(wheel2)

    # Main wheels
    wheel3 = Wheel()
    wheel3.diameter = wheel2.diameter
    wheel3.drag_correction = 0. #3.
    wheel3.origin = np.array(
        [
            main_wing_x + 0.1,
            -wheel2.origin[1],
            wheel2.origin[2]]
    )
    wheel3.origin[1] = -wheel2.origin[1]
    landing_gear.add_wheel(wheel3)

    # Landing gear strut
    strut = Strut()
    strut.mass = 0.08
    strut.origin = np.array([vehicle.center_of_gravity[0] + 0.1, 0, wheel2.origin[2]])
    strut.effective_drag_length = (wheel2.origin[1]**2 + wheel2.origin[2]**2)**0.5 * 2 + abs(wheel1.origin[2])
    strut.length_specific_cd = 0. #0.003
    landing_gear.add_strut(strut)

    landing_gear.finalize()

    vehicle.landing_gear = landing_gear

    ####################################################################################################################

    vehicle.add_misc("ESC", 0.093, np.array([-0.05, 0, 0]))  # YGE 95A : 93gr inkl. Kabel
    vehicle.add_misc(
        "Servo", 0.092, np.array([0.5, 0, 0])
    )  # 6 Servos a 12gr + 20gr Kabel
    vehicle.add_misc(
        "Receiver", 0.020, np.array([0.5, 0, 0])
    )  # bel. Hersteller circa 10gr
    vehicle.add_misc(
        "Motor", 0.175, np.array([-0.3, 0, 0])
    )  # T-Motor AT2826 900KV : 175gr inkl. Kabel
    vehicle.add_misc("Prop+Spinner", 0.025, np.array([-0.3, 0, 0]))  # Assumption
    vehicle.add_misc("MeasurementBox", 0.150, np.array([-0.05, 0, 0]))  # Assumption
    vehicle.add_misc("Screws+Cables+Accessories", 0.090, np.array([0.5, 0, 0]))  # Assumption
    vehicle.add_misc("ReceiverBattery", 0.030, np.array([0.5, 0, 0]))  # Assumption

    ####################################################################################################################

    vehicle.build()
    # vehicle.wings["main_wing"].part_wing_into(4, vehicle.mass, override=True)
    vehicle.print_mass_table()
    vehicle.get_reference_values()
    CLa, Cma, Cnb, XNP, SM, percentMAC = vehicle.get_stability_derivatives()
    box_height, box_width, box_length = vehicle.transport_box_dimensions()

    logging.debug(f"Vehicle Mass: {vehicle.mass:.3f}")
    # PLOT
    if __name__ == "__main__":
        vehicle.plot_vehicle(azim=230, elev=30)

    # Return results
    vehicle.results.span = vehicle.reference_values.b_ref
    vehicle.results.aspect_ratio = vehicle.reference_values.AR
    vehicle.results.mean_aerodynamic_chord = vehicle.reference_values.c_ref
    vehicle.results.wing_area = vehicle.reference_values.s_ref
    vehicle.results.horizontal_stabilizer_area = vehicle.wings[
        "horizontal_stabilizer"
    ].reference_area
    vehicle.results.wing_loading = vehicle.mass / vehicle.reference_values.s_ref
    vehicle.results.battery_capacity = vehicle.battery.capacity
    vehicle.results.propeller = vehicle.propeller.propeller_tag
    vehicle.results.main_wing_airfoil = vehicle.wings["main_wing"].airfoil
    vehicle.results.horizontal_stabilizer_airfoil = vehicle.wings[
        "horizontal_stabilizer"
    ].airfoil

    eta_fowler = 0.0
    span_fowler = 0.0
    area_fowler = 0.0
    for segment in vehicle.wings["main_wing"].segments:
        if segment.control_name == "fowler":
            eta_fowler += 2 * segment.span / vehicle.wings["main_wing"].span
            span_fowler += 2 * segment.span
            area_fowler += 2 * segment.area

    vehicle.results.fowler_affected_span = span_fowler
    vehicle.results.fowler_affected_span_ratio = eta_fowler
    vehicle.results.fowler_affected_area = area_fowler
    vehicle.results.fowler_affected_area_ratio = (
        area_fowler / vehicle.reference_values.s_ref
    )

    vehicle.results.fuselage_wetted_area = vehicle.fuselages["fuselage"].area
    vehicle.results.fuselage_length = vehicle.fuselages["fuselage"].length
    vehicle.results.fuselage_diameter = vehicle.fuselages["fuselage"].diameter

    #vehicle.results.cargo_bay_length = vehicle.fuselages["cargo_bay"].length
    #vehicle.results.cargo_bay_wetted_area = vehicle.fuselages["cargo_bay"].area

    vehicle.results.mass_total = vehicle.mass
    vehicle.results.mass_empty = vehicle.mass - vehicle.payload
    vehicle.results.mass_payload = vehicle.payload
    vehicle.results.mass_battery = vehicle.battery.get_mass()
    vehicle.results.mass_fuselage = vehicle.fuselages["fuselage"].mass
#    vehicle.results.mass_cargo_bay = vehicle.fuselages["cargo_bay"].mass
    vehicle.results.mass_wing = vehicle.wings["main_wing"].mass
    vehicle.results.mass_horizontal_stabilizer = vehicle.wings[
        "horizontal_stabilizer"
    ].mass
#    vehicle.results.mass_pylon = vehicle.wings["pylon"].mass
    vehicle.results.mass_landing_gear = vehicle.landing_gear.mass
    vehicle.results.mass_misc = 0
    for misc in vehicle.miscs:
        vehicle.results.mass_misc += misc.mass

    vehicle.results.x_center_of_gravity = vehicle.center_of_gravity[0]
    vehicle.results.c_m_alpha = Cma
    vehicle.results.c_l_alpha = CLa
    vehicle.results.c_n_beta = Cnb
    vehicle.results.x_neutral_point = XNP
    vehicle.results.static_margin = SM
    vehicle.results.percent_mac = percentMAC

    print('percent mac', vehicle.results.percent_mac)

    vehicle.results.transport_box_height = box_height
    vehicle.results.transport_box_width = box_width
    vehicle.results.transport_box_length = box_length

    return vehicle


if __name__ == "__main__":
    vehicle_setup()
