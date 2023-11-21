import logging
import math
from collections import defaultdict

import matplotlib.pyplot as plt
import numpy as np

from mace.domain.general_functions import rotate_vector
from mace.utils.mesh import gen_profile, get_profil, get_profil_thickness, mesh
from mace.utils.weight import moment_at_position

rad = np.pi / 180


class Spar:
    lenght: int = None
    height: int = None
    rovings: int = None


class WingBinder:
    position: float
    height: float
    mass: float
    roving_count: float

    def __init__(self, position, height, moment_at_position) -> None:
        self.position = position
        self.height = height
        self.get_rovings(moment_at_position)
        self.get_mass()

    def get_mass(self):
        dens = 375
        lenght = 60 / 1000
        width = (self.roving_count + 1) / 100
        # CONST = 375 / 1_000 * 6
        # self.mass =  * self.height**2 * CONST
        self.mass = dens * lenght * self.height * width

    def get_rovings(self, moment_at_position):
        # TODO Test me pls
        max_height = self.height
        D100 = moment_at_position
        sigma = 700 * (10**6)
        H100 = D100 / sigma
        C100 = 10 / 1_000
        G100 = max_height# - 0.4 / 1_000
        J100 = np.cbrt(((C100 * (G100**3)) - (6 * G100 * H100)) / C100)
        K100 = (G100 - J100) / 2
        m = K100 * C100 * 10**6
        n = np.ceil(m)
        self.roving_count = n


class WingSegmentBuild:
    materials: np.ndarray = None
    build_type: str = None
    surface_weight: str = None
    density: str = None
    spar: Spar = None

    def __init__(
        self, build_type, surface_weight, *args, core_material_density=0
    ) -> None:
        self.build_type = build_type
        self.surface_weight = surface_weight
        self.materials = np.array(args) / 1_000 * 2.2
        self.density = core_material_density


class WingSegment:
    """
    Wing Segment Class
    """

    mass: float = None
    roving_count: int = None
    mass_breakdown: defaultdict[str, float] = None
    cog_breakdown: defaultdict[str, np.ndarray] = None

    def __init__(self) -> None:
        """
        Initialize Wing Segment
        """
        self.span = 1.0
        self.dihedral = 0.0
        self.area = 0.0
        self.flap_chord_ratio = 0.25

        self.inner_chord = 1.0
        self.inner_x_offset = 0.0
        self.inner_twist = 0.0

        self.outer_chord = 1.0
        self.outer_x_offset = 0.0
        self.outer_twist = 0.0

        self.nose_inner = np.array([0.0, 0.0, 0.0])
        self.nose_outer = np.array([0.0, 0.0, 0.0])
        self.back_inner = np.array([0.0, 0.0, 0.0])
        self.back_outer = np.array([0.0, 0.0, 0.0])

        self.n_spanwise = 20  # TODO
        self.s_space = -2  # TODO

        self.inner_airfoil = None
        self.outer_airfoil = None

        self.control = None  # TODO
        self.control_name = "flap"
        self.hinge_vec = np.array([0.0, 0.0, 0.0])
        self.c_gain = 1.0
        self.sgn_dup = 1.0

        self.wsb: WingSegmentBuild = None

    def get_area(self) -> float:
        """
        Calculate the area of the wing segment
        """
        self.area = (self.inner_chord + self.outer_chord) * self.span / 2
        return self.area

    def get_mass(self):
        self.mass_breakdown = {}
        self.cog_breakdown = {}
        profil_innen, profil_außen = gen_profile(
            get_profil(self.inner_airfoil),
            get_profil(self.outer_airfoil),
            self.nose_inner,
            self.back_inner,
            self.nose_outer,
            self.back_outer,
        )
        area, volume, cog = mesh(profil_innen, profil_außen)

        if self.wsb.build_type == "Positiv":
            self.mass_breakdown["Kern"] = volume * self.wsb.density
        elif self.wsb.build_type == "Balsa":
            self.mass_breakdown["Kern"] = volume * self.wsb.density * 0.1
        elif self.wsb.build_type == "Negativ":
            self.mass_breakdown["Kern"] = 0
        self.cog_breakdown["Kern"] = (
            self.nose_inner
            + (self.nose_outer - self.nose_inner) * 0.5
            + (self.back_inner - self.nose_inner) * 0.33
        )
        self.cog_breakdown["Kern"] *= self.mass_breakdown["Kern"]

        if not self.roving_count is None:
            self.mass_breakdown["Holm"] = self.span * (self.roving_count * 0.009 + 0.03)
            self.cog_breakdown["Holm"] = (
                self.nose_inner
                + (self.nose_outer - self.nose_inner) * 0.5
                + (self.back_inner - self.nose_inner) * 0.25
            )
            self.cog_breakdown["Holm"] *= self.mass_breakdown["Holm"]

        self.mass_breakdown["Schale"] = area * self.wsb.surface_weight
        for material in self.wsb.materials:
            self.mass_breakdown["Schale"] += material * area
        self.cog_breakdown["Schale"] = cog * self.mass_breakdown["Schale"]

        if self.control_name == "fowler":
            self.mass_breakdown["Flap"] = self.span * 0.25
            self.cog_breakdown["Flap"] = cog * self.mass_breakdown["Flap"]

        self.mass = sum(self.mass_breakdown.values())
        self.cog = sum(self.cog_breakdown.values()) / self.mass
        return self.mass, self.cog * self.mass

    def get_rovings(self, total_mass: float, plane_half_wing_span: float):
        # TODO Change var names
        max_height = self.inner_chord * get_profil_thickness(self.inner_airfoil)
        D100 = moment_at_position(total_mass, self.nose_inner[1], plane_half_wing_span)
        sigma = 700 * (10**6)
        H100 = D100 / sigma
        C100 = 10 / 1_000
        G100 = max_height  # - 0.4 / 1_000
        J100 = np.cbrt(((C100 * (G100**3)) - (6 * G100 * H100)) / C100)
        K100 = (G100 - J100) / 2
        m = K100 * C100 * 10**6
        n = int(np.ceil(m))
        self.roving_count = n
        return n


class Wing:
    """
    Wing Class
    """

    wing_binder: list[WingBinder] = None
    segments: list[WingSegment] = None

    def __init__(self) -> None:
        """
        Initialize Wing
        :param name: Name of the wing
        """
        self.spar = None
        self.tag = None  # Wing name as string
        self.segments = []  # List of wing segments
        self.symmetric = True  # True if wing is symmetric
        self.vertical = False  # True if wing is vertical (eg vertical stabilizer)
        self.origin = np.array(
            [0.0, 0.0, 0.0]
        )  # Origin of the wing (x,y,z) (most forward point of root chord)
        self.span = None  # Wing span
        self.reference_area = None  # Wing reference area
        self.aspect_ratio = None  # Wing aspect ratio
        self.mean_aerodynamic_chord = None  # Wing mean aerodynamic chord
        self.neutral_point = np.array(
            [0.0, 0.0, 0.0]
        )  # Wing neutral point (x,y,z) in local coordinates
        self.hinge_angle = (
            0.0  # Wing hinge angle (in degrees). Positive means towards leading edge
        )
        self.volume_coefficient = None  # Stabilizer volume coefficient
        self.airfoil = None  # Wing airfoil
        self.angle = 0.0  # Wing angle of attack (in degrees)

        # AVL
        self.n_chordwise: int = 10
        self.c_space: int = 1  # = cos
        self.n_spanwise: int = 20
        self.s_space: int = (
            -2
        )  # = -sin, good for straight, elliptical or slightly tapered wings, in other cases cos (1)

        # Mass estimation
        self.number_of_parts = 1

    def add_segment(self, segment: WingSegment) -> None:
        """
        Add a segment to the wing
        :param segment: Wing segment to add
        """
        self.segments.append(segment)

    def print_wing(self) -> None:
        """
        Print the wing information
        """
        logging.debug(f"Wing Name: {self.name}")
        logging.debug("Segment Information:")
        for i, segment in enumerate(self.segments):
            logging.debug(f"Segment {i + 1}:")
            logging.debug(f"    Inner Chord: {segment.inner_chord}")
            logging.debug(f"    Outer Chord: {segment.outer_chord}")
            logging.debug(f"    Inner Sweep: {segment.inner_x_offset}")
            logging.debug(f"    Outer Sweep: {segment.outer_x_offset}")
            logging.debug(f"    Inner Twist: {segment.inner_twist}")
            logging.debug(f"    Outer Twist: {segment.outer_twist}")
            logging.debug(f"    Dihedral: {segment.dihedral}")

    def get_area(self) -> float:
        """
        Calculate the area of the wing
        """
        area = 0
        for segment in self.segments:
            area += (1 + self.symmetric) * segment.get_area()
        return area

    def get_span(self) -> float:
        """
        Calculate the span of the wing
        """
        span = 0
        for segment in self.segments:
            span += (1 + self.symmetric) * segment.span
        return span

    def get_aspect_ratio(self) -> float:
        """
        Calculate the aspect ratio of the wing
        """
        return self.get_span() ** 2 / self.get_area()

    def get_mean_aerodynamic_chord(self) -> float:
        """
        Calculate the mean aerodynamic chord of the wing
        """
        mac = 0
        for segment in self.segments:
            lbda = segment.outer_chord / segment.inner_chord
            mac += (
                2
                * segment.get_area()
                * 2
                / 3
                * segment.inner_chord
                * (1 + lbda + lbda**2)
                / (1 + lbda)
            )  # Equation from Strohmayer FZE1
            # mac += segment.get_area() * (1 + self.symmetric) * (segment.inner_chord + segment.outer_chord) / 2
        mac /= self.get_area()
        return mac

    def get_neutral_point(self) -> float:
        """
        Calculate the neutral point of the wing. Method from SUAVE
        """
        Cxys = []
        As = []
        for segment in self.segments:
            a = segment.outer_chord
            b = segment.inner_chord
            c = segment.outer_x_offset - segment.inner_x_offset
            dx = c
            dy = segment.span
            dz = np.tan(segment.dihedral) * dy
            taper = segment.outer_chord / segment.inner_chord
            dihedral = segment.dihedral

            cx = (2 * a * c + a**2 + c * b + a * b + b**2) / (3 * (a + b))
            cy = segment.span / 3.0 * ((1.0 + 2.0 * taper) / (1.0 + taper))
            cz = cy * np.tan(dihedral)

            Cxys.append(np.array([cx + dx, cy + dy, cz + dz]))
            As.append(segment.area)

        aerodynamic_center = np.dot(np.transpose(Cxys), As) / (
            self.reference_area / (1 + self.symmetric)
        )

        single_side_aerodynamic_center = np.array(aerodynamic_center) * 1.0
        single_side_aerodynamic_center[0] = (
            single_side_aerodynamic_center[0] - self.mean_aerodynamic_chord * 0.25
        )
        if self.symmetric == True:
            aerodynamic_center[1] = 0
        aerodynamic_center[0] = single_side_aerodynamic_center[0]
        self.neutral_point = aerodynamic_center
        return self.neutral_point

    def resize_to_given_span(self, new_span):
        """
        :param new_span: The new span of the wing.
        Resizes the wing segments so that the span is equal to the given span.
        The chord is held constant. Aspect ratio and span change.
        """
        old_span = self.get_span()
        span_factor = new_span / old_span
        for segment in self.segments:
            segment.span *= span_factor

    def resize_to_given_aspect_ratio(self, new_aspect_ratio):
        """
        :param new_aspect_ratio: The new aspect ratio of the wing.
        Resizes the wing segments so that the aspect ratio is equal to the given aspect ratio.
        The span is held constant. Aspect ratio and chord change.
        """
        old_aspect_ratio = self.get_aspect_ratio()
        aspect_ratio_factor = new_aspect_ratio / old_aspect_ratio
        for segment in self.segments:
            segment.inner_chord *= 1 / aspect_ratio_factor
            segment.outer_chord *= 1 / aspect_ratio_factor

    def resize_to_given_area(self, new_area):
        """
        :param new_area: The new area of the wing.
        Resizes the wing segments so that the area is equal to the given area.
        The aspect ratio is held constant. Area and span change.
        """
        old_area = self.get_area()
        area_factor = new_area / old_area
        for segment in self.segments:
            segment.span *= math.sqrt(area_factor)
            segment.inner_chord *= math.sqrt(area_factor)
            segment.outer_chord *= math.sqrt(area_factor)

    def resize_sweep_to_constant_flap_chord_ratio(self, hinge_angle: float):
        """
        Resizes the wing segments such that the flap chord ratio is constant.
        :param hinge_angle: The angle of the flap hinge line in degrees.
        """
        hinge_angle = math.radians(hinge_angle)
        for i, segment in enumerate(self.segments):
            if i == 0:
                segment.inner_x_offset = 0
                root_chord = segment.inner_chord
                x_flap_root = root_chord * (1 - segment.flap_chord_ratio)

                y = segment.span
                x_flap = x_flap_root - np.arctan(hinge_angle) * y
                segment.outer_x_offset = x_flap - segment.outer_chord * (
                    1 - segment.flap_chord_ratio
                )
            else:
                x_flap = x_flap_root - np.arctan(hinge_angle) * y
                segment.inner_x_offset = x_flap - segment.inner_chord * (
                    1 - segment.flap_chord_ratio
                )
                y += segment.span
                x_flap = x_flap_root - np.arctan(hinge_angle) * y
                segment.outer_x_offset = x_flap - segment.outer_chord * (
                    1 - segment.flap_chord_ratio
                )

    def resize_wing(self, new_span=None, new_aspect_ratio=None, new_area=None):
        """
        Resizes the wing to the given span, aspect ratio, or area. One or two parameters must be specified.
        It is recommended to use two parameters to avoid unwanted geometry changes.
        :param new_span: The new span of the wing.
        :param new_aspect_ratio: The new aspect ratio of the wing.
        :param new_area: The new area of the wing.
        """
        if new_span is None and new_aspect_ratio is None and new_area is None:
            logging.debug("No parameters specified. Wing will stay in original shape.")
        elif new_span is None and new_aspect_ratio is None:
            self.resize_to_given_area(new_area)
        elif new_span is None and new_area is None:
            self.resize_to_given_aspect_ratio(new_aspect_ratio)
        elif new_aspect_ratio is None and new_area is None:
            self.resize_to_given_span(new_span)
        elif new_span is None:
            self.resize_to_given_aspect_ratio(new_aspect_ratio)
            self.resize_to_given_area(new_area)
        elif new_aspect_ratio is None:
            self.resize_to_given_span(new_span)
            self.resize_to_given_area(new_area)
        elif new_area is None:
            self.resize_to_given_span(new_span)
            self.resize_to_given_aspect_ratio(new_aspect_ratio)
        else:
            raise ValueError("Only one or two of the parameters can be specified.")

    def get_stabilizer_area_from_volume_coefficient(
        self, volume_coefficient: float, l_stab: float, S_ref: float, l_ref: float
    ) -> float:
        """
        Returns the area of the stabilizer.
        :param volume_coefficient: The volume coefficient of the stabilizer.
        :param l_stab: Stabilizer lever.
        :param S_ref: Reference area of the main wing.
        :param l_ref: Reference length of the main wing. Can be Span for vertical stabilizer or MAC for horizontal stabilizer.
        """
        self.reference_area = volume_coefficient * S_ref * l_ref / l_stab
        return self.reference_area

    def get_segment_coordinates(self):
        """
        Calculates the coordinates of the segments of the wing.
        """
        y = 0.0
        z = 0.0

        for i, segment in enumerate(self.segments):
            segment.nose_inner[0] = self.origin[0] + segment.inner_x_offset
            segment.nose_inner[1] = self.origin[1] + y
            segment.nose_inner[2] = self.origin[2] + z

            segment.back_inner[0] = segment.nose_inner[
                0
            ] + segment.inner_chord * np.cos(segment.inner_twist * rad)
            segment.back_inner[1] = segment.nose_inner[1]
            segment.back_inner[2] = segment.nose_inner[
                2
            ] - segment.inner_chord * np.sin(segment.inner_twist * rad)

            if self.vertical == False:
                y += segment.span
            else:
                z += segment.span

            segment.nose_outer[0] = self.origin[0] + segment.outer_x_offset
            segment.nose_outer[1] = self.origin[1] + y
            segment.nose_outer[2] = self.origin[2] + z

            segment.back_outer[0] = segment.nose_outer[
                0
            ] + segment.outer_chord * np.cos(segment.outer_twist * rad)
            segment.back_outer[1] = segment.nose_outer[1]
            segment.back_outer[2] = segment.nose_outer[
                2
            ] - segment.outer_chord * np.sin(segment.outer_twist * rad)

        # Dihedral rotation
        overall_translation = np.array([0, 0, 0])
        for i, segment in enumerate(self.segments):
            reference_point = segment.nose_outer

            segment.nose_inner = segment.nose_inner + overall_translation
            segment.nose_outer = segment.nose_outer + overall_translation
            segment.back_inner = segment.back_inner + overall_translation
            segment.back_outer = segment.back_outer + overall_translation

            segment.nose_inner = segment.nose_inner + rotate_vector(
                segment.nose_inner - segment.nose_inner, segment.dihedral, 0, 0
            )
            segment.nose_outer = segment.nose_inner + rotate_vector(
                segment.nose_outer - segment.nose_inner, segment.dihedral, 0, 0
            )
            segment.back_inner = segment.nose_inner + rotate_vector(
                segment.back_inner - segment.nose_inner, segment.dihedral, 0, 0
            )
            segment.back_outer = segment.nose_inner + rotate_vector(
                segment.back_outer - segment.nose_inner, segment.dihedral, 0, 0
            )

            overall_translation = segment.nose_outer - reference_point

        # Angle of attack rotation
        for i, segment in enumerate(self.segments):
            segment.nose_inner = self.origin + rotate_vector(
                segment.nose_inner - self.origin, 0, self.angle, 0
            )
            segment.nose_outer = self.origin + rotate_vector(
                segment.nose_outer - self.origin, 0, self.angle, 0
            )
            segment.back_inner = self.origin + rotate_vector(
                segment.back_inner - self.origin, 0, self.angle, 0
            )
            segment.back_outer = self.origin + rotate_vector(
                segment.back_outer - self.origin, 0, self.angle, 0
            )

    def build(self, resize_areas=True, resize_x_offset_from_hinge_angle=True) -> None:
        """
        Builds the wing by calculating the wing geometry.
        """
        if resize_areas:
            self.resize_wing(
                new_span=self.span,
                new_aspect_ratio=self.aspect_ratio,
                new_area=self.reference_area,
            )
        if resize_x_offset_from_hinge_angle:
            self.resize_sweep_to_constant_flap_chord_ratio(self.hinge_angle)

        for segment in self.segments:
            segment.inner_airfoil = self.airfoil
            segment.outer_airfoil = self.airfoil

        self.get_segment_coordinates()
        self.reference_area = self.get_area()
        self.span = self.get_span()
        self.aspect_ratio = self.get_aspect_ratio()
        self.mean_aerodynamic_chord = self.get_mean_aerodynamic_chord()
        self.neutral_point = self.get_neutral_point()

    def plot_wing_geometry(self):
        """
        Plots the wing geometry.
        """
        x_le_coords = []
        x_te_coords = []
        x_hinge_coords = []
        y_coords = []
        y = 0

        for segment in self.segments:
            y_coords.append(y)
            x_le_coords.append(segment.inner_x_offset)
            x_te_coords.append(segment.inner_x_offset + segment.inner_chord)
            x_hinge_coords.append(
                segment.inner_x_offset
                + segment.inner_chord * (1 - segment.flap_chord_ratio)
            )
            y += segment.span
            y_coords.append(y)
            x_le_coords.append(segment.outer_x_offset)
            x_hinge_coords.append(
                segment.outer_x_offset
                + segment.outer_chord * (1 - segment.flap_chord_ratio)
            )
            x_te_coords.append(segment.outer_x_offset + segment.outer_chord)

        if self.symmetric == True and self.vertical == False:
            x_le_coords_other_wing = np.flip(x_le_coords)
            x_te_coords_other_wing = np.flip(x_te_coords)
            x_hinge_coords_other_wing = np.flip(x_hinge_coords)
            y_coords_other_wing = -1 * np.flip(y_coords)

            x_le_coords = np.concatenate((x_le_coords_other_wing, x_le_coords))
            x_te_coords = np.concatenate((x_te_coords_other_wing, x_te_coords))
            x_hinge_coords = np.concatenate((x_hinge_coords_other_wing, x_hinge_coords))
            y_coords = np.concatenate((y_coords_other_wing, y_coords))

        plt.figure(figsize=(10, 6))
        plt.plot(
            y_coords,
            x_le_coords,
            "b",
            y_coords,
            x_te_coords,
            "b",
            y_coords,
            x_hinge_coords,
            "b",
        )
        plt.xlabel("y")
        plt.ylabel("x")
        plt.axis("equal")
        plt.grid(True)
        plt.show()

    def get_mass(self):
        masses = []
        cogs = []
        for segment in self.segments:
            tmp_mass, tmp_cogs = segment.get_mass()
            masses.append(tmp_mass)
            cogs.append(tmp_cogs)
        if not self.wing_binder is None:
            for wb in self.wing_binder:
                masses.append(wb.mass)
                cogs.append(np.array([0, wb.position, 0]))

        faktor = 2 if self.symmetric else 1
        self.mass = faktor * sum(masses)
        self.cog = sum(cogs) / self.mass
        return self.mass, self.cog * self.mass * np.array([2, 0, 2])

    def get_height_position(self, position: float) -> float:
        position = abs(position)
        for segment in self.segments:
            if not (segment.nose_outer[1] > position and segment.nose_inner[1] <= position):
                continue
            l = (
                np.sqrt(np.sum(np.square(segment.nose_inner - segment.back_inner)))
                * (segment.nose_outer[1] - position)
                + np.sqrt(np.sum(np.square(segment.nose_outer - segment.back_outer)))
                * (segment.nose_inner[1] - position)
            ) / np.sqrt(np.sum(np.square(segment.nose_outer - segment.nose_inner)))
            th = get_profil_thickness(segment.inner_airfoil)
            return l * th
        return 0

    def part_wing_into(self, total_mass, into_parts: int = 1, max_lenght: float = 1E100, override=True):
        wing_span = self.segments[-1].nose_outer[1]
        part_len = min(2 * wing_span / into_parts, max_lenght)
        current = 0 if (wing_span//part_len)%2==0 else part_len/2
        pos = []
        while current < wing_span:
            pos.append(current)
            current += part_len
        self.part_wing(pos, total_mass, mirror=True, override=override)

    def part_wing(
        self, positions: list[float], total_mass: float, mirror=True, override=False
    ):
        if self.wing_binder is None or override:
            self.wing_binder = []
        if mirror:
            rev = [-pos for pos in positions if not pos == 0]
            positions.extend(rev)
        for position in positions:
            height = self.get_height_position(position)
            wing_span = self.segments[-1].nose_outer[1]
            moment = moment_at_position(total_mass, position, wing_span)
            self.wing_binder.append(WingBinder(position, height, moment))


# Example usage:
if __name__ == "__main__":
    # Create a wing object
    main_wing = Wing()

    # Add segments to the wing

    # Inner segment
    segment1 = WingSegment()

    segment1.span = 1.3
    segment1.inner_chord = 0.175
    segment1.outer_chord = 0.155
    segment1.flap_chord_ratio = 0.3

    main_wing.add_segment(segment1)

    # Mid segment
    segment2 = WingSegment()

    segment2.span = 1
    segment2.inner_chord = segment1.outer_chord
    segment2.outer_chord = 0.11
    segment2.flap_chord_ratio = 0.3

    main_wing.add_segment(segment2)

    # Outer segment
    segment3 = WingSegment()

    segment3.span = 0.3
    segment3.inner_chord = segment2.outer_chord
    segment3.outer_chord = 0.05
    segment3.flap_chord_ratio = 0.3

    main_wing.add_segment(segment3)

    # Resize Wing
    main_wing.span = 1.49
    main_wing.aspect_ratio = 13.2
    main_wing.hinge_angle = 1.0
    main_wing.build()

    # Get wing properties
    S = main_wing.reference_area
    b = main_wing.span
    AR = main_wing.aspect_ratio

    # Print wing properties
    logging.debug(f"Area: {round(S, 4)}")
    logging.debug(f"Span: {round(b, 3)}")
    logging.debug(f"Aspect Ratio: {round(AR, 3)}")

    # Plot wing geometry
    main_wing.plot_wing_geometry()
