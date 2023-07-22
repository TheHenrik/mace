from mace.domain.wing import Wing, WingSegment
from mace.domain.fuselage import Fuselage, FuselageSegment
from mace.domain.landing_gear import LandingGear, Wheel
from mace.domain.vehicle import Vehicle
import numpy as np

def vehicle_setup() -> Vehicle:
    vehicle = Vehicle()
    vehicle.mass = 2.7 + 3.
    vehicle.center_of_gravity = [0.1, 0.0, 0.0]

    ####################################################################################################################
    # MAIN WING
    main_wing = Wing()
    main_wing.tag = "main_wing"
    main_wing.origin = [0, 0, 0]
    main_wing.airfoil = "acc22"
    main_wing.angle = 2.
    main_wing.symmetric = True

    # Inner segment
    segment = WingSegment()
    segment.span = 1.039 / 2
    segment.inner_chord = 0.320
    segment.outer_chord = 0.299
    segment.dihedral = 1
    segment.control = True
    main_wing.add_segment(segment)

    # Mid segment
    segment = WingSegment()
    segment.span = 0.4
    segment.inner_chord = 0.299
    segment.outer_chord = 0.230
    segment.dihedral = 5
    segment.control = True
    main_wing.add_segment(segment)

    # Outer segment
    segment = WingSegment()
    segment.span = 2.32/2 - 0.4 - 1.039/2
    segment.inner_chord = 0.230
    segment.outer_chord = 0.14
    segment.dihedral = 5
    segment.outer_twist = 0
    segment.control = True
    main_wing.add_segment(segment)

    # Resize Wing
    main_wing.hinge_angle = -3
    # main_wing.aspect_ratio = 4.
    main_wing.build()

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
    horizontal_stabilizer.origin = [0.7, 0, 0]
    horizontal_stabilizer.airfoil = "ht14"

    # Segment
    segment = WingSegment()
    segment.inner_chord = 1.
    segment.outer_chord = 0.6
    segment.flap_chord_ratio = 0.4
    horizontal_stabilizer.add_segment(segment)

    # Resize Wing
    horizontal_stabilizer.aspect_ratio = 4.
    l_ht = horizontal_stabilizer.origin[0] - main_wing.origin[0]
    v_ht = 0.583*2
    horizontal_stabilizer.get_stabilizer_area_from_volume_coefficient(v_ht, l_ht, S_ref, MAC)
    horizontal_stabilizer.build()

    vehicle.add_wing("horizontal_stabilizer", horizontal_stabilizer)
    ####################################################################################################################
    # VERTICAL STABILIZER
    vertical_stabilizer = Wing()
    vertical_stabilizer.tag = "vertical_stabilizer"
    vertical_stabilizer.origin = [0.7, 0, 0]
    vertical_stabilizer.vertical = True
    vertical_stabilizer.symmetric = False
    vertical_stabilizer.airfoil = "ht14"
    vertical_stabilizer.hinge_angle = 0

    # Segment
    segment = WingSegment()
    segment.inner_chord = 1.
    segment.outer_chord = 0.5
    segment.flap_chord_ratio = 0.4
    vertical_stabilizer.add_segment(segment)

    # Resize Wing
    vertical_stabilizer.aspect_ratio = 1.5
    l_vt = vertical_stabilizer.origin[0] - main_wing.origin[0]
    v_vt = 0.018
    vertical_stabilizer.get_stabilizer_area_from_volume_coefficient(v_vt, l_vt, S_ref, b_ref)
    vertical_stabilizer.build()

    vehicle.add_wing("vertical_stabilizer", vertical_stabilizer)
    
    vehicle.get_reference_values()
    
    for wing in vehicle.wings.values():
        S = wing.reference_area
        print("%s %.1f sqdm" % (wing.tag, S*100))


    ####################################################################################################################
    # PROPULSION
    vehicle.propulsion.thrust = np.array([[0., 14.42], [3., 13.82], [6., 12.89], [9., 11.85], [12., 10.58], [15., 9.19],
                                          [18., 7.79], [21., 5.86], [24., 4.01]])
    ####################################################################################################################
    # FUSELAGE
    fuselage = Fuselage()

    segment = FuselageSegment()
    segment.origin[0] = -0.4
    segment.width = 0.1
    segment.height = 0.1
    fuselage.add_segment(segment)

    segment = FuselageSegment()
    segment.origin[0] = -0.4 + 0.15
    segment.width = 0.1
    segment.height = 0.15
    fuselage.add_segment(segment)

    segment = FuselageSegment()
    segment.origin[0] = -0.4 + 0.15 + 0.56
    segment.width = 0.1
    segment.height = 0.15
    fuselage.add_segment(segment)

    segment = FuselageSegment()
    segment.origin[0] = 1.
    segment.width = 0.05
    segment.height = 0.05
    fuselage.add_segment(segment)

    fuselage.build()
    vehicle.add_fuselage("fuselage", fuselage)
    ####################################################################################################################
    # LANDING GEAR
    landing_gear = LandingGear()

    Height = 0.25
    landing_gear.height = Height
    
    wheel1 = Wheel()
    wheel1.diameter = 0.1
    wheel1.mass = 0.05
    wheel1.origin = np.array([-0.3, 0., -(Height-wheel1.diameter/2.)])
    landing_gear.add_wheel(wheel1)

    wheel2 = Wheel()
    wheel2.diameter = 0.16
    wheel2.mass = 0.05
    wheel2.origin = np.array([vehicle.center_of_gravity[0] + 0.1, 0.3, -(Height-wheel2.diameter/2.)])
    landing_gear.add_wheel(wheel2)

    wheel3 = Wheel()
    wheel3.diameter = wheel2.diameter
    wheel3.mass = wheel2.mass
    wheel3.origin = np.array([vehicle.center_of_gravity[0] + 0.1, -wheel2.origin[1], wheel2.origin[2]])
    wheel3.origin[1] = -wheel2.origin[1]
    landing_gear.add_wheel(wheel3)

    landing_gear.finalize()

    vehicle.landing_gear = landing_gear
    ####################################################################################################################
    # PLOT

    #vehicle.plot_vehicle(azim=180, elev=0)
    vehicle.plot_vehicle(azim=230, elev=30)
    #vehicle.plot_vehicle(azim=0, elev=90)
    #vehicle.plot_vehicle(azim=90, elev=0)
    return vehicle


if __name__ == "__main__":
    vehicle_setup()

