import math
import matplotlib.pyplot as plt
import numpy as np
from mace.domain.general_functions import rotate_vector

rad = np.pi / 180
class WingSegment:
    """
    Wing Segment Class
    """
    def __init__(self) -> None:
        """
        Initialize Wing Segment
        """
        self.span = 1.
        self.dihedral = 0.
        self.area = 0.
        self.flap_chord_ratio = 0.25

        self.inner_chord = 1.
        self.inner_x_offset = 0.
        self.inner_twist = 0.

        self.outer_chord = 1.
        self.outer_x_offset = 0.
        self.outer_twist = 0.

        self.nose_inner = np.array([0., 0., 0.])
        self.nose_outer = np.array([0., 0., 0.])
        self.back_inner = np.array([0., 0., 0.])
        self.back_outer = np.array([0., 0., 0.])
        
        self.n_spanwise = 20 # TODO
        self.s_space = -2 # TODO
        
        self.inner_airfoil = None
        self.outer_airfoil = None
        
        self.control = None # TODO
        self.control_name = 'flap'
        self.hinge_vec = np.array([0., 0., 0.])
        self.c_gain = 1.
        self.sgn_dup = 1.

    def get_area(self) -> float:
        """
        Calculate the area of the wing segment
        """
        self.area = (self.inner_chord + self.outer_chord) * self.span / 2
        return self.area

class Wing:
    """
    Wing Class
    """
    def __init__(self) -> None:
        """
        Initialize Wing
        :param name: Name of the wing
        """
        self.tag = None # Wing name as string
        self.segments = [] # List of wing segments
        self.symmetric = True # True if wing is symmetric
        self.vertical = False # True if wing is vertical (eg vertical stabilizer)
        self.origin = np.array([0., 0., 0.]) # Origin of the wing (x,y,z) (most forward point of root chord)
        self.span = None # Wing span
        self.reference_area = None # Wing reference area
        self.aspect_ratio = None # Wing aspect ratio
        self.mean_aerodynamic_chord = None # Wing mean aerodynamic chord
        self.neutral_point = np.array([0., 0., 0.]) # Wing neutral point (x,y,z) in local coordinates
        self.hinge_angle = 0. # Wing hinge angle (in degrees). Positive means towards leading edge 
        self.volume_coefficient = None # Stabilizer volume coefficient
        self.airfoil = None # Wing airfoil
        self.angle = 0. # Wing angle of attack (in degrees)
        
        # AVL
        self.n_chordwise: int = 10
        self.c_space: int = 1  # = cos
        self.n_spanwise: int = 20
        self.s_space: int = -2  # = -sin, good for straight, elliptical or slightly tapered wings, in other cases cos (1)
        
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
        print(f"Wing Name: {self.name}")
        print("Segment Information:")
        for i, segment in enumerate(self.segments):
            print(f"Segment {i + 1}:")
            print(f"    Inner Chord: {segment.inner_chord}")
            print(f"    Outer Chord: {segment.outer_chord}")
            print(f"    Inner Sweep: {segment.inner_x_offset}")
            print(f"    Outer Sweep: {segment.outer_x_offset}")
            print(f"    Inner Twist: {segment.inner_twist}")
            print(f"    Outer Twist: {segment.outer_twist}")
            print(f"    Dihedral: {segment.dihedral}")
            print()

    def get_area(self) -> float:
        """
        Calculate the area of the wing
        """
        area = 0
        for segment in self.segments:
            area += (1+self.symmetric) * segment.get_area()
        return area

    def get_span(self) -> float:
        """
        Calculate the span of the wing
        """
        span = 0
        for segment in self.segments:
            span += (1+self.symmetric) * segment.span
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
            mac += segment.get_area() * (1 + self.symmetric) * (segment.inner_chord + segment.outer_chord) / 2
        mac /= self.get_area()
        return mac

    def get_neutral_point(self) -> float:
        """
        Calculate the neutral point of the wing
        """
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
            segment.inner_chord *= 1/aspect_ratio_factor
            segment.outer_chord *= 1/aspect_ratio_factor

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
                segment.outer_x_offset = x_flap - segment.outer_chord * (1 - segment.flap_chord_ratio)
            else:
                x_flap = x_flap_root - np.arctan(hinge_angle) * y
                segment.inner_x_offset = x_flap - segment.inner_chord * (1 - segment.flap_chord_ratio)
                y += segment.span
                x_flap = x_flap_root - np.arctan(hinge_angle) * y
                segment.outer_x_offset = x_flap - segment.outer_chord * (1 - segment.flap_chord_ratio)
    def resize_wing(self, new_span=None, new_aspect_ratio=None, new_area=None):
        """
        Resizes the wing to the given span, aspect ratio, or area. One or two parameters must be specified.
        It is recommended to use two parameters to avoid unwanted geometry changes.
        :param new_span: The new span of the wing.
        :param new_aspect_ratio: The new aspect ratio of the wing.
        :param new_area: The new area of the wing.
        """
        if new_span is None and new_aspect_ratio is None and new_area is None:
            print("No parameters specified. Wing will stay in original shape.")
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

    def get_stabilizer_area_from_volume_coefficient(self, volume_coefficient: float, l_stab: float,
                                                    S_ref: float, l_ref: float) -> float:
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
        y = 0.
        z = 0.

        for i, segment in enumerate(self.segments):
            segment.nose_inner[0] = self.origin[0] + segment.inner_x_offset
            segment.nose_inner[1] = self.origin[1] + y
            segment.nose_inner[2] = self.origin[2] + z

            segment.back_inner[0] = segment.nose_inner[0] + segment.inner_chord*np.cos(segment.inner_twist*rad)
            segment.back_inner[1] = segment.nose_inner[1]
            segment.back_inner[2] = segment.nose_inner[2] - segment.inner_chord*np.sin(segment.inner_twist*rad)

            if self.vertical == False:
                y += segment.span
            else:
                z += segment.span

            segment.nose_outer[0] = self.origin[0] + segment.outer_x_offset
            segment.nose_outer[1] = self.origin[1] + y
            segment.nose_outer[2] = self.origin[2] + z

            segment.back_outer[0] = segment.nose_outer[0] + segment.outer_chord*np.cos(segment.outer_twist*rad)
            segment.back_outer[1] = segment.nose_outer[1]
            segment.back_outer[2] = segment.nose_outer[2] - segment.outer_chord*np.sin(segment.outer_twist*rad)


        # Dihedral rotation
        overall_translation = np.array([0, 0, 0])
        for i, segment in enumerate(self.segments):
            reference_point = segment.nose_outer

            segment.nose_inner = segment.nose_inner + overall_translation
            segment.nose_outer = segment.nose_outer + overall_translation
            segment.back_inner = segment.back_inner + overall_translation
            segment.back_outer = segment.back_outer + overall_translation

            segment.nose_inner = segment.nose_inner + rotate_vector(segment.nose_inner - segment.nose_inner, segment.dihedral, 0, 0)
            segment.nose_outer = segment.nose_inner + rotate_vector(segment.nose_outer - segment.nose_inner, segment.dihedral, 0, 0)
            segment.back_inner = segment.nose_inner + rotate_vector(segment.back_inner - segment.nose_inner, segment.dihedral, 0, 0)
            segment.back_outer = segment.nose_inner + rotate_vector(segment.back_outer - segment.nose_inner, segment.dihedral, 0, 0)

            overall_translation = segment.nose_outer - reference_point

        # Angle of attack rotation
        for i, segment in enumerate(self.segments):
            segment.nose_inner = self.origin + rotate_vector(segment.nose_inner - self.origin, 0, self.angle, 0)
            segment.nose_outer = self.origin + rotate_vector(segment.nose_outer - self.origin, 0, self.angle, 0)
            segment.back_inner = self.origin + rotate_vector(segment.back_inner - self.origin, 0, self.angle, 0)
            segment.back_outer = self.origin + rotate_vector(segment.back_outer - self.origin, 0, self.angle, 0)

    def build(self, resize_areas=True, resize_x_offset_from_hinge_angle=True) -> None:
        """
        Builds the wing by calculating the wing geometry.
        """
        if resize_areas:
            self.resize_wing(new_span=self.span, new_aspect_ratio=self.aspect_ratio, new_area=self.reference_area)
        if resize_x_offset_from_hinge_angle:
            self.resize_sweep_to_constant_flap_chord_ratio(self.hinge_angle)
        
        for segment in self.segments:
            segment.inner_airfoil = self.airfoil
            segment.outer_airfoil = self.airfoil
        
        self.get_segment_coordinates()
        self.reference_area = self.get_area()
        self.span = self.get_span()
        self.aspect_ratio = self.get_aspect_ratio()
        self.neutral_point = self.get_neutral_point()
        self.mean_aerodynamic_chord = self.get_mean_aerodynamic_chord()


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
            x_hinge_coords.append(segment.inner_x_offset + segment.inner_chord * (1 - segment.flap_chord_ratio))
            y += segment.span
            y_coords.append(y)
            x_le_coords.append(segment.outer_x_offset)
            x_hinge_coords.append(segment.outer_x_offset + segment.outer_chord * (1 - segment.flap_chord_ratio))
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
        plt.plot(y_coords, x_le_coords, 'b', y_coords, x_te_coords, 'b', y_coords, x_hinge_coords, 'b', )
        plt.xlabel('y')
        plt.ylabel('x')
        plt.axis('equal')
        plt.grid(True)
        plt.show()


# Example usage:
if __name__ == '__main__':
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
    main_wing.hinge_angle = 1.
    main_wing.build()

    # Get wing properties
    S = main_wing.reference_area
    b = main_wing.span
    AR = main_wing.aspect_ratio

    # Print wing properties
    print(f"Area: {round(S, 4)}")
    print(f"Span: {round(b, 3)}")
    print(f"Aspect Ratio: {round(AR, 3)}")

    # Plot wing geometry
    main_wing.plot_wing_geometry()

