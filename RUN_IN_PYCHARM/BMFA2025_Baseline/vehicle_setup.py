import mace.domain.vehicle
from mace.domain.battery import Battery
from mace.domain.fuselage import Fuselage, FuselageSegment
from mace.domain.landing_gear import LandingGear, Strut, Wheel
from mace.domain.propeller import Propeller
from mace.domain.vehicle import Vehicle
from mace.domain.wing import Wing, WingSegment, WingSegmentBuild

import numpy as np
def vehicle_setup(center_wing_span = 1., add_payload = 4., shorter_outer_wing = True):
    vehicle = mace.domain.vehicle.Vehicle()
    main_wing_construction = WingSegmentBuild(
        build_type="Negativ", surface_weight=0.25
    )
    empennage_construction = WingSegmentBuild(
        build_type="Positiv", surface_weight=0.17, core_material_density=40
    )

    max_length = max(0.98, center_wing_span)
    vehicle.payload = add_payload
    ####################################################################################################################
    # MAIN WING
    ####################################################################################################################
    main_wing = Wing()
    main_wing.tag = "main_wing"
    main_wing.origin = [0, 0, 0]
    main_wing.airfoil = "acc22"
    main_wing.angle = 2.0
    main_wing.symmetric = True
    
    if center_wing_span > 0:
        # Center Wing
        segment = WingSegment()
        segment.span = center_wing_span / 2
        chord = 0.302 if shorter_outer_wing else 0.347
        segment.inner_chord = chord
        segment.outer_chord = chord
        segment.dihedral = 0
        segment.control = True
        segment.wsb = main_wing_construction
        main_wing.add_segment(segment)

    # Outer Wing from ACC17
    if not shorter_outer_wing:
        segment = WingSegment()
        segment.span = 0.35
        segment.inner_chord = 0.347
        segment.outer_chord = 0.302
        segment.outer_x_offset = 0.012
        segment.dihedral = 3
        segment.control = True
        segment.wsb = main_wing_construction
        main_wing.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.25
    segment.inner_chord = 0.302
    segment.outer_chord = 0.250
    segment.inner_x_offset = 0.012
    segment.outer_x_offset = 0.047
    segment.dihedral = 3
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.2
    segment.inner_chord = 0.250
    segment.outer_chord = 0.185
    segment.inner_x_offset = 0.047
    segment.outer_x_offset = 0.08
    segment.dihedral = 3
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    segment = WingSegment()
    segment.span = 0.175
    segment.inner_chord = 0.185
    segment.outer_chord = 0.09
    segment.inner_x_offset = 0.08
    segment.outer_x_offset = 0.14
    segment.dihedral = 3
    segment.control = True
    segment.wsb = main_wing_construction
    main_wing.add_segment(segment)

    main_wing.build()

    S_ref = main_wing.reference_area
    MAC = main_wing.mean_aerodynamic_chord
    b_ref = main_wing.span

    vehicle.add_wing("main_wing", main_wing)

    ####################################################################################################################
    # HORIZONTAL STABILIZER
    ####################################################################################################################

    horizontal_stabilizer = Wing()
    horizontal_stabilizer.tag = "horizontal_stabilizer"
    horizontal_stabilizer.origin = [0.9, 0, 0]
    horizontal_stabilizer.airfoil = "ht14"
    horizontal_stabilizer.symmetric = True
    horizontal_stabilizer.hinge_angle = 0

    # Segment
    segment = WingSegment()
    segment.inner_chord = 1.
    segment.outer_chord = 0.6
    segment.span = 1.
    segment.flap_chord_ratio = 0.4
    segment.wsb = empennage_construction
    horizontal_stabilizer.add_segment(segment)

    # Resize Wing
    horizontal_stabilizer.aspect_ratio = 6.
    horizontal_stabilizer.reference_area = 0.07
    #horizontal_stabilizer.get_stabilizer_area_from_volume_coefficient(v_ht, l_ht, S_ref, MAC)
    horizontal_stabilizer.build(resize_x_offset_from_hinge_angle=True, resize_areas=True)

    vehicle.add_wing("horizontal_stabilizer", horizontal_stabilizer)

    ####################################################################################################################
    # VERTICAL STABILIZER
    ####################################################################################################################

    vertical_stabilizer = Wing()
    vertical_stabilizer.tag = "vertical_stabilizer"
    vertical_stabilizer.origin = [0.9, 0, 0]
    vertical_stabilizer.airfoil = "ht14"
    vertical_stabilizer.vertical = True
    vertical_stabilizer.symmetric = False
    vertical_stabilizer.hinge_angle = 0


    # Segment
    segment = WingSegment()
    segment.inner_chord = 1.
    segment.outer_chord = 0.6
    segment.span = 1.
    segment.flap_chord_ratio = 0.4
    segment.wsb = empennage_construction
    vertical_stabilizer.add_segment(segment)

    # Resize Wing
    vertical_stabilizer.aspect_ratio = 2
    vertical_stabilizer.reference_area = 0.02
    #l_vt = vertical_stabilizer.origin[0] - main_wing.origin[0]
    #v_vt = 0.021
    #vertical_stabilizer.get_stabilizer_area_from_volume_coefficient(v_vt, l_vt, S_ref, b_ref)
    vertical_stabilizer.build(resize_x_offset_from_hinge_angle=True, resize_areas=True)
    vehicle.add_wing("vertical_stabilizer", vertical_stabilizer)

    ####################################################################################################################
    # FUSELAGE
    ####################################################################################################################
    fuselage = Fuselage()

    fuselage.add_segment(
        origin=[-0.2, 0, 0.0], shape="rectangular", width=0.04, height=0.04
    )
    fuselage.add_segment(
        origin=[0.9, 0, 0.0], shape="rectangular", width=0.04, height=0.04
    )

    fuselage.area_specific_mass = 0.616
    fuselage.build()
    vehicle.add_fuselage("fuselage", fuselage)

    ####################################################################################################################
    # PROPULSION
    ####################################################################################################################
    prop = Propeller('aeronaut16x8')
    vehicle.propeller = prop

    battery = Battery()
    battery.capacity = 2.2
    battery.mass = 0.17
    vehicle.battery = battery

    ####################################################################################################################
    # LANDING GEAR
    ####################################################################################################################

    landing_gear = LandingGear()
    landing_gear.height = 0.2

    # Nose wheel
    wheel1 = Wheel()
    wheel1.diameter = 0.1
    wheel1.drag_correction = 1.5
    wheel1.origin = np.array(
        [-0.15, 0.0, -(landing_gear.height - wheel1.diameter / 2.0)]
    )
    landing_gear.add_wheel(wheel1)

    # Main wheels
    wheel2 = Wheel()
    wheel2.diameter = 0.16
    wheel2.drag_correction = 1.5
    wheel2.origin = np.array(
        [
            0.25,
            0.2,
            -(landing_gear.height - wheel2.diameter / 2.0),
        ]
    )
    landing_gear.add_wheel(wheel2)

    # Main wheels
    wheel3 = Wheel()
    wheel3.diameter = wheel2.diameter
    wheel3.drag_correction = 1.5
    wheel3.origin = np.array(
        [wheel2.origin[0], -wheel2.origin[1], wheel2.origin[2]]
    )
    landing_gear.add_wheel(wheel3)

    # Landing gear strut
    strut = Strut()
    strut.mass = 0.08
    strut.origin = np.array([vehicle.center_of_gravity[0] + 0.1, 0, wheel2.origin[2]])
    landing_gear.add_strut(strut)

    landing_gear.finalize()

    vehicle.landing_gear = landing_gear

    ####################################################################################################################
    # MISCELLANEOUS
    ####################################################################################################################

    vehicle.add_misc("ESC", 0.041, np.array([0, 0, 0]))  # YGE 95A : 93gr inkl. Kabel
    vehicle.add_misc("Servo", 0.060, np.array([0, 0, 0]))  # 6 Servos a 12gr + 20gr Kabel
    vehicle.add_misc("Receiver", 0.010, np.array([0, 0, 0]))  # bel. Hersteller circa 10gr
    vehicle.add_misc("Motor", 0.127, np.array([0, 0, 0]))  # T-Motor AT2826 900KV : 175gr inkl. Kabel
    vehicle.add_misc("Prop+Spinner", 0.025, np.array([0, 0, 0]))  # Assumption
    vehicle.add_misc("Screws+Cables+Accessories", 0.060, np.array([0, 0, 0]))  # Assumption

    vehicle.build(length=max_length)
    vehicle.get_reference_values()

    print('Reference Area:', vehicle.reference_values.s_ref)
    print('Reference Span:', vehicle.reference_values.b)
    vehicle.print_mass_table()
    if __name__ == '__main__':
        vehicle.plot_vehicle()
    
    return vehicle

if __name__ == '__main__':
    vehicle_setup(center_wing_span=0., add_payload=0., shorter_outer_wing=True)
    vehicle_setup(center_wing_span=0.75, add_payload=3.8, shorter_outer_wing=True)