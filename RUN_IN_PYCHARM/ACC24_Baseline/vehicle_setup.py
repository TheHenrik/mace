from mace.domain.wing import Wing, WingSegment
from mace.domain.fuselage import Fuselage, FuselageSegment
from mace.domain.landing_gear import LandingGear, Wheel
from mace.domain.vehicle import Vehicle
import numpy as np

def vehicle_setup() -> Vehicle:
    vehicle = Vehicle()
    vehicle.mass = 2.
    vehicle.center_of_gravity = [0.1, 0.0, 0.0]

    ####################################################################################################################
    # MAIN WING
    main_wing = Wing()
    main_wing.tag = "main_wing"
    main_wing.origin = [0, 0, 0]
    main_wing.airfoil = "ag40"
    main_wing.angle = 2.
    main_wing.symmetric = True

    # Inner segment
    segment = WingSegment()
    segment.span = 0.45
    segment.inner_chord = 1.
    segment.outer_chord = 0.9
    segment.dihedral = 1
    segment.control = True
    main_wing.add_segment(segment)

    # Mid segment
    segment = WingSegment()
    segment.span = 0.3
    segment.inner_chord = 0.9
    segment.outer_chord = 0.7
    segment.dihedral = 5
    segment.control = True
    main_wing.add_segment(segment)

    # Outer segment
    segment = WingSegment()
    segment.span = 0.15
    segment.inner_chord = 0.7
    segment.outer_chord = 0.4
    segment.dihedral = 5
    segment.outer_twist = 0
    segment.control = True
    main_wing.add_segment(segment)

    # Outer segment
    segment = WingSegment()
    segment.span = 0.05
    segment.inner_chord = 0.4
    segment.outer_chord = 0.2
    segment.dihedral = 5
    segment.outer_twist = 0
    segment.control = True
    main_wing.add_segment(segment)

    # Resize Wing
    main_wing.hinge_angle = 1.
    main_wing.span = 3.
    main_wing.aspect_ratio = 15.
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
    segment.dihedral = 40.
    horizontal_stabilizer.add_segment(segment)

    # Segment
    segment = WingSegment()
    segment.inner_chord = 0.228
    segment.outer_chord = 0.12
    segment.flap_chord_ratio = 0.4
    segment.dihedral = 40.
    horizontal_stabilizer.add_segment(segment)

    # Resize Wing
    l_ht = horizontal_stabilizer.origin[0] - main_wing.origin[0]
    v_ht = 0.583*2 * 1.414
    horizontal_stabilizer.aspect_ratio = 7.
    horizontal_stabilizer.get_stabilizer_area_from_volume_coefficient(v_ht, l_ht, S_ref, MAC)
    horizontal_stabilizer.build(resize_x_offset_from_hinge_angle=True)

    vehicle.add_wing("horizontal_stabilizer", horizontal_stabilizer)
    ####################################################################################################################
    # PROPULSION
    # new thrust vector 2023-7-26 with correction factor
    vehicle.propulsion.thrust = 1.25 * np.array([[0., 12.4622], [4.24, 11.657], [9.6, 10.286],
                                          [14.89, 8.771], [19.72, 7.2094], [23.25, 6.075]]) # new thrust vector 2023-7-26
    ####################################################################################################################
    # FUSELAGE
    fuselage = Fuselage()
    x_minus_offset = 0.19
    x_plus_offset = 0.55

    segment = FuselageSegment()
    segment.origin[0] = - b_ref * 0.1
    segment.width = 0.04
    segment.height = 0.04
    fuselage.add_segment(segment)

    segment = FuselageSegment()
    segment.origin[0] = b_ref * 0.35
    segment.width = 0.04
    segment.height = 0.04
    fuselage.add_segment(segment)

    segment = FuselageSegment()
    segment.origin[0] = -0.05 - x_minus_offset


    fuselage.build()
    print("f_length: %.3f m" % fuselage.length)
    vehicle.add_fuselage("fuselage", fuselage)
    ####################################################################################################################
    # LANDING GEAR
    landing_gear = LandingGear()

    Height = 0.25
    landing_gear.height = Height
    
    wheel1 = Wheel()
    wheel1.diameter = 0.1
    wheel1.mass = 0.05
    wheel1.origin = np.array([-0.26, 0., -(Height-wheel1.diameter/2.)])
    landing_gear.add_wheel(wheel1)

    wheel2 = Wheel()
    wheel2.diameter = 0.16
    wheel2.mass = 0.05
    wheel2.origin = np.array([vehicle.center_of_gravity[0] + 0.1, 0.23, -(Height-wheel2.diameter/2.)])
    landing_gear.add_wheel(wheel2)

    wheel3 = Wheel()
    wheel3.diameter = wheel2.diameter
    wheel3.mass = wheel2.mass
    wheel3.origin = np.array([vehicle.center_of_gravity[0] + 0.1, -wheel2.origin[1], wheel2.origin[2]])
    wheel3.origin[1] = -wheel2.origin[1]
    landing_gear.add_wheel(wheel3)

    landing_gear.finalize()

    landing_gear.effective_drag_length = 0.
    landing_gear.length_specific_cd = 0.0033

    vehicle.landing_gear = landing_gear
    ####################################################################################################################
    vehicle.get_reference_values()

    for wing in vehicle.wings.values():
        S = wing.reference_area
        print("%s %.1f sqdm" % (wing.tag, S * 100))
    
    # PLOT
    if __name__ == "__main__":
        vehicle.plot_vehicle(azim=180, elev=0)
        vehicle.plot_vehicle(azim=230, elev=30)
        vehicle.plot_vehicle(azim=0, elev=90)
        vehicle.plot_vehicle(azim=90, elev=0)
    return vehicle


if __name__ == "__main__":
    vehicle_setup()

