from mace.domain.wing import Wing, WingSegment
from mace.domain.vehicle import Vehicle

def vehicle_setup() -> Vehicle:
    vehicle = Vehicle()
    vehicle.mass = 5.626
    vehicle.center_of_gravity = [0.1, 0.0, 0.0]

    ####################################################################################################################
    # MAIN WING
    main_wing = Wing()
    main_wing.tag = "main_wing"
    main_wing.origin = [0, 0, 0]
    main_wing.airfoil = "ag19"
    main_wing.angle = 10.

    dihedral = 3.

    # Inner segment
    segment1 = WingSegment()
    segment1.span = 0.52
    segment1.inner_chord = 0.292
    segment1.outer_chord = 0.290
    segment1.flap_chord_ratio = 0.3
    segment1.dihedral = dihedral
    main_wing.add_segment(segment1)

    # Mid segment
    segment2 = WingSegment()
    segment2.span = 0.32
    segment2.inner_chord = segment1.outer_chord
    segment2.outer_chord = 0.230
    segment2.flap_chord_ratio = 0.3
    segment2.dihedral = dihedral
    main_wing.add_segment(segment2)

    # Outer segment
    segment3 = WingSegment()
    segment3.span = 0.192
    segment3.inner_chord = segment2.outer_chord
    segment3.outer_chord = 0.08
    segment3.flap_chord_ratio = 0.3
    segment3.dihedral = dihedral
    segment3.outer_twist = 0.
    main_wing.add_segment(segment3)

    # Resize Wing
    main_wing.hinge_angle = 1.
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
    horizontal_stabilizer.origin = [0.8, 0, 0]
    horizontal_stabilizer.airfoil = "n0012"

    # Segment
    segment = WingSegment()
    segment.inner_chord = 1.
    segment.outer_chord = 0.6
    segment.flap_chord_ratio = 0.4
    horizontal_stabilizer.add_segment(segment)

    # Resize Wing
    horizontal_stabilizer.aspect_ratio = 4.
    l_ht = horizontal_stabilizer.origin[0] - main_wing.origin[0]
    v_ht = 0.9
    horizontal_stabilizer.get_stabilizer_area_from_volume_coefficient(v_ht, l_ht, S_ref, MAC)
    horizontal_stabilizer.build()

    vehicle.add_wing("horizontal_stabilizer", horizontal_stabilizer)
    ####################################################################################################################
    # VERTICAL STABILIZER
    vertical_stabilizer = Wing()
    vertical_stabilizer.tag = "vertical_stabilizer"
    vertical_stabilizer.origin = [1., 0, 0]
    vertical_stabilizer.vertical = True
    vertical_stabilizer.symmetric = False
    vertical_stabilizer.airfoil = "n0012"
    vertical_stabilizer.hinge_angle = -15

    # Segment
    segment = WingSegment()
    segment.inner_chord = 1.
    segment.outer_chord = 0.5
    segment.flap_chord_ratio = 0.4
    vertical_stabilizer.add_segment(segment)

    # Resize Wing
    vertical_stabilizer.aspect_ratio = 1.5
    l_vt = vertical_stabilizer.origin[0] - main_wing.origin[0]
    v_vt = 0.05
    vertical_stabilizer.get_stabilizer_area_from_volume_coefficient(v_vt, l_vt, S_ref, b_ref)
    vertical_stabilizer.build()

    vehicle.add_wing("vertical_stabilizer", vertical_stabilizer)
    
    vehicle.get_reference_values()
    
    for wing in vehicle.wings.values():
        S = wing.reference_area
        print("%s %.1f sqdm" % (wing.tag, S*100))

    vehicle.plot_vehicle()

    return vehicle
    ####################################################################################################################


if __name__ == "__main__":
    vehicle_setup()

