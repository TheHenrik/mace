# Getting Started

This guide assumes you are using uv.

## Installation & Setup

Create a new project using:

```sh
uv init -p 3.13 test-pymace
cd test-pymace
```

Than install the dependencies needed

```sh
uv add pymace
```

If your are on linux you might need to add ```pyqt6``` aswell.

## Run your fist vehicle Setup

For your first vehicle setup just copy the following into the vehicle.py and execute.

```py
from pymace.domain.vehicle import Vehicle
from pymace.domain.wing import Wing, WingSegment, WingSegmentBuild


def vehicle_setup() -> Vehicle:
    vehicle = Vehicle()
    vehicle.payload = 0
    vehicle.mass = 2.25

    vehicle.center_of_gravity = [0.088, 0.0, 0.0]

    main_wing_construction = WingSegmentBuild(
        build_type="Negativ", surface_weight=0.400
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

    vehicle.add_wing("main_wing", main_wing)
    vehicle.get_reference_values()

    return vehicle


if __name__ == "__main__":
    vehicle = vehicle_setup()
    vehicle.plot_vehicle(azim=230, elev=30)
```

You should see a 3D-Image of the main wing.
