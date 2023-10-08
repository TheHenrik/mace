from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np

from mace.domain.fuselage import Fuselage, FuselageSegment
from mace.domain.landing_gear import LandingGear, Wheel
from mace.domain.results import (
    AeroCoeffs,
    Avl,
    AvlInputs,
    AvlOutputs,
    Cd,
    Cl,
    Climb,
    ClimbResults,
    FlightConditions,
    HorizontalFlight,
    HorizontalFlightResults,
)
from mace.domain.wing import Wing, WingSegment


class Vehicle:
    def __init__(self):
        self.tag = "Vehicle"
        self.mass = 0.0
        self.center_of_gravity = [0.0, 0.0, 0.0]
        self.wings = {}
        self.fuselages = {}
        self.reference_values = ReferenceValues

        self.flight_conditions = FlightConditions
        self.flight_conditions.climb = Climb
        self.flight_conditions.climb.results = ClimbResults
        self.flight_conditions.horizontal_flight = HorizontalFlight
        self.flight_conditions.horizontal_flight.results = HorizontalFlightResults

        self.avl = Avl
        self.avl.inputs = AvlInputs
        self.avl.outputs = AvlOutputs
        self.aero_coeffs = AeroCoeffs
        self.aero_coeffs.lift_coeff = Cl
        self.aero_coeffs.drag_coeff = Cd

        self.propulsion = Propulsion
        self.landing_gear = LandingGear()

    def add_wing(self, position: str, wing: Wing):
        self.wings[position] = wing

    def add_fuselage(self, position: str, fuselage: Fuselage):
        self.fuselages[position] = fuselage

    def get_reference_values(self):
        if "main_wing" in self.wings.keys():
            main_wing = self.wings["main_wing"]
            self.reference_values.s_ref = main_wing.reference_area
            self.reference_values.c_ref = main_wing.mean_aerodynamic_chord
            self.reference_values.b_ref = main_wing.span
            self.reference_values.h = main_wing.origin[2] + main_wing.neutral_point[2]
            self.reference_values.b = main_wing.span
            self.reference_values.AR = main_wing.aspect_ratio

        self.reference_values.x_ref = self.center_of_gravity[0]
        self.reference_values.y_ref = self.center_of_gravity[1]
        self.reference_values.z_ref = self.center_of_gravity[2]

    def plot_vehicle(
        self,
        color="b",
        zticks=False,
        show_points=False,
        show_landing_gear=True,
        elev=30,
        azim=30,
    ):
        x = []
        y = []
        z = []

        for wing in self.wings.values():
            for segment in wing.segments:
                x.append(
                    [
                        segment.nose_inner[0],
                        segment.nose_outer[0],
                        segment.back_outer[0],
                        segment.back_inner[0],
                    ]
                )
                y.append(
                    [
                        segment.nose_inner[1],
                        segment.nose_outer[1],
                        segment.back_outer[1],
                        segment.back_inner[1],
                    ]
                )
                z.append(
                    [
                        segment.nose_inner[2],
                        segment.nose_outer[2],
                        segment.back_outer[2],
                        segment.back_inner[2],
                    ]
                )
            if wing.symmetric:
                for segment in wing.segments:
                    x.append(
                        [
                            segment.nose_inner[0],
                            segment.nose_outer[0],
                            segment.back_outer[0],
                            segment.back_inner[0],
                        ]
                    )
                    y.append(
                        [
                            -segment.nose_inner[1],
                            -segment.nose_outer[1],
                            -segment.back_outer[1],
                            -segment.back_inner[1],
                        ]
                    )
                    z.append(
                        [
                            segment.nose_inner[2],
                            segment.nose_outer[2],
                            segment.back_outer[2],
                            segment.back_inner[2],
                        ]
                    )

        fig = plt.figure(dpi=400)
        ax = fig.add_subplot(111, projection="3d")

        if show_points:
            ax.scatter(x, y, z, c=color, marker="o")

        for wing in self.wings.values():
            for segment in wing.segments:
                n_i = segment.nose_inner
                n_o = segment.nose_outer
                b_i = segment.back_inner
                b_o = segment.back_outer
                # Leading Edge
                ax.plot([n_i[0], n_o[0]], [n_i[1], n_o[1]], [n_i[2], n_o[2]], color)
                # Trailing Edge
                ax.plot([b_i[0], b_o[0]], [b_i[1], b_o[1]], [b_i[2], b_o[2]], color)
                # Inner chord
                ax.plot([n_i[0], b_i[0]], [n_i[1], b_i[1]], [n_i[2], b_i[2]], color)
                # Outer chord
                ax.plot([n_o[0], b_o[0]], [n_o[1], b_o[1]], [n_o[2], b_o[2]], color)

                if wing.symmetric:
                    # Leading Edge
                    ax.plot(
                        [n_i[0], n_o[0]], [-n_i[1], -n_o[1]], [n_i[2], n_o[2]], color
                    )
                    # Trailing Edge
                    ax.plot(
                        [b_i[0], b_o[0]], [-b_i[1], -b_o[1]], [b_i[2], b_o[2]], color
                    )
                    # Inner chord
                    ax.plot(
                        [n_i[0], b_i[0]], [-n_i[1], -b_i[1]], [n_i[2], b_i[2]], color
                    )
                    # Outer chord
                    ax.plot(
                        [n_o[0], b_o[0]], [-n_o[1], -b_o[1]], [n_o[2], b_o[2]], color
                    )

        for fuse in self.fuselages.values():
            segment_counter = 0
            for segment in fuse.segments:
                if segment.shape == "rectangular":
                    b_l = segment.origin + np.array(
                        [0.0, -segment.width / 2, -segment.height / 2]
                    )
                    b_r = segment.origin + np.array(
                        [0.0, +segment.width / 2, -segment.height / 2]
                    )
                    u_l = segment.origin + np.array(
                        [0.0, -segment.width / 2, +segment.height / 2]
                    )
                    u_r = segment.origin + np.array(
                        [0.0, +segment.width / 2, +segment.height / 2]
                    )

                    ax.plot([u_l[0], u_r[0]], [u_l[1], u_r[1]], [u_l[2], u_r[2]], color)
                    ax.plot([u_r[0], b_r[0]], [u_r[1], b_r[1]], [u_r[2], b_r[2]], color)
                    ax.plot([b_r[0], b_l[0]], [b_r[1], b_l[1]], [b_r[2], b_l[2]], color)
                    ax.plot([b_l[0], u_l[0]], [b_l[1], u_l[1]], [b_l[2], u_l[2]], color)

                    if segment_counter != 0:
                        ax.plot(
                            [u_l[0], last_seg_u_l[0]],
                            [u_l[1], last_seg_u_l[1]],
                            [u_l[2], last_seg_u_l[2]],
                            color,
                        )
                        ax.plot(
                            [u_r[0], last_seg_u_r[0]],
                            [u_r[1], last_seg_u_r[1]],
                            [u_r[2], last_seg_u_r[2]],
                            color,
                        )
                        ax.plot(
                            [b_r[0], last_seg_b_r[0]],
                            [b_r[1], last_seg_b_r[1]],
                            [b_r[2], last_seg_b_r[2]],
                            color,
                        )
                        ax.plot(
                            [b_l[0], last_seg_b_l[0]],
                            [b_l[1], last_seg_b_l[1]],
                            [b_l[2], last_seg_b_l[2]],
                            color,
                        )

                    last_seg_b_l = b_l
                    last_seg_b_r = b_r
                    last_seg_u_l = u_l
                    last_seg_u_r = u_r

                    segment_counter += 1

        if show_landing_gear:
            self.landing_gear.plot(color="b")

        # Achsen beschriften
        ax.set_xlabel("x")
        ax.set_ylabel("y")
        ax.set_zlabel("z")
        ax.set_aspect("equal")
        if zticks:
            ax.set_zticks(zticks)
        else:
            ax.set_zticks([])

        ax.view_init(elev=elev, azim=azim)

        plt.tick_params(which="major", labelsize=6)

        # Titel hinzufügen
        plt.title(self.tag, fontsize=10)

        # Anzeigen des Plots
        plt.show()
    
    def build(self):
        # TODO Stabilität Untersuchung
        pass


@dataclass()
class Propulsion:
    mass: float = 0
    center_of_gravity: np.ndarray = None
    thrust: np.ndarray = None


@dataclass()
class ReferenceValues:
    number_of_surfaces: float = 30
    mach: float = 0  # mach number for Prandtl-Glauert correction
    iy_sym: float = 0  # has to be 0 for YDUPLICATE
    iz_sym: float = 0  # 0: no z-symmetry assumed
    z_sym: float = 0  # for iz_sym = 0 ignored
    s_ref: float = 0  # reference wing area
    c_ref: float = 0  # reference chord length
    b_ref: float = 0  # reference wingspan for moment coefficients
    x_ref: float = 0  # must bei CG location for trim calculation
    y_ref: float = 0  # must bei CG location for trim calculation
    z_ref: float = 0  # must bei CG location for trim calculation
    h: float = 0  # Height wof WingNP above ground for rolling
    b: float = 0  # Spanwidth
    AR: float = 0  # Aspect ratio (Streckung) b^2 / S


@dataclass()
class AvlInputs:
    avl_file = None
    mass_file = None


@dataclass()
class AvlOutputs:
    # Trefftz plane
    clff: float = 0
    cdff: float = 0
    cyff: float = 0
    oswaldfactor: float = 0
    # Reference data
    s_ref: float = 0
    c_ref: float = 0
    b_ref: float = 0
    x_ref: float = 0
    y_ref: float = 0
    z_ref: float = 0
    # Overall data
    number_of_strips: int = 0
    number_of_surfaces: int = 0
    number_of_vortices: int = 0
    # Surface data
    surface_data: np.ndarray = None
    first_and_last_strips = {}  # Dictionary
    surface_dictionary = {}
    strip_forces: np.ndarray = None


@dataclass()
class Avl:
    inputs: AvlInputs = None
    outputs: AvlOutputs = None
