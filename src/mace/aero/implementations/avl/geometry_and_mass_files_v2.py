import logging
import os
from pathlib import Path

# from mace.domain.vehicle import Vehicle
from mace.domain.params import Constants, Units
from mace.utils.mp import get_pid

# ========== Geometry File ==========


class GeometryFile:
    def __init__(self, plane) -> None:
        self.plane = plane
        self.z_sym = 0

    def build_geo_header(self, geometry_file):
        if self.plane.tag is not None:
            geometry_file.write(f"{self.plane.tag}\n")
        geometry_file.write(f"# Mach\n")
        geometry_file.write(f"{round(self.plane.reference_values.mach,5)}\n")
        geometry_file.write(f"#IYsym\tIZsym\tZsym\n")
        geometry_file.write(
            f"{round(self.plane.reference_values.iy_sym,5):<10}"
            f"{round(self.z_sym):<10}"
            f"{round(-self.plane.landing_gear.height,3):<10}\n\n"
        )  # iYsym has to be 0 for YDUPLICATE
        geometry_file.write(f"#Sref\tCref\tBref\n")
        geometry_file.write(
            f"{round(self.plane.reference_values.s_ref,5):<10}"
            f"{round(self.plane.reference_values.c_ref,5):<10}"
            f"{round(self.plane.reference_values.b_ref,5):<10}\n"
        )
        geometry_file.write(f"#Xref\tYref\tZref\n")
        geometry_file.write(
            f"{round(self.plane.reference_values.x_ref,5):<10}"
            f"{round(self.plane.reference_values.y_ref,5):<10}"
            f"{round(self.plane.reference_values.z_ref,5):<10}\n"
        )

    def build_geo_surface_section_control(self, geometry_file, segment):
        # geometry_file.write(f'\t\t#++++++++++++++++++++\n')
        geometry_file.write(f"CONTROL\n")
        geometry_file.write(f"#Cname\tCgain\tXhinge\tHingeVec\t \t \tSgnDup\n")
        geometry_file.write(
            f"{segment.control_name}\t{segment.c_gain}\t{(1-segment.flap_chord_ratio)}\t"
            f'{"0. 0. 0."}\t'
            f"{segment.sgn_dup}\n"
        )  # HingeVec most cases 0 0 0 -> along hinge

    def get_chord(self, element):
        chord_inner = (
            (element.back_inner[0] - element.nose_inner[0]) ** 2
            + (element.back_inner[1] - element.nose_inner[1]) ** 2
            + (element.back_inner[2] - element.nose_inner[2]) ** 2
        ) ** 0.5
        chord_outer = (
            (element.back_outer[0] - element.nose_outer[0]) ** 2
            + (element.back_outer[1] - element.nose_outer[1]) ** 2
            + (element.back_outer[2] - element.nose_outer[2]) ** 2
        ) ** 0.5
        return chord_inner, chord_outer

    def build_geo_surface_section(self, geometry_file, wing):
        tool_path = Path(__file__).resolve().parents[5]
        airfoil_path = os.path.join(tool_path, "data", "airfoils")

        chord_outer = 0
        for i, segment in enumerate(wing.segments):
            geometry_file.write(f"SECTION\n")
            geometry_file.write(f"#Xle\tYle\tZle\tChord\tAinc\tNspanwise\tSspace\n")
            geometry_file.write(
                f"{round(segment.nose_inner[0],5)}  "
                f"{round(segment.nose_inner[1],5)}  "
                f"{round(segment.nose_inner[2],5)}  "
                f"{round(segment.inner_chord,5)}  "
                f"{round(segment.inner_twist,5)}"
            )
            if segment.n_spanwise is not None:
                geometry_file.write(f"{  segment.n_spanwise}")
            if segment.s_space is not None:
                geometry_file.write(f"{  segment.s_space}")
            geometry_file.write(f"\n\n")
            geometry_file.write(f"AFIL  0.0  1.0\n")
            segment_airfoil_path = os.path.join(airfoil_path, segment.inner_airfoil, ".dat")
            geometry_file.write(
                f'segment_airfoil_path\n\n'
            )

            if segment.control is not None:
                GeometryFile.build_geo_surface_section_control(
                    self, geometry_file, segment
                )

        index = len(wing.segments) - 1
        geometry_file.write(f"SECTION\n")
        geometry_file.write(f"#Xle\tYle\tZle\tChord\tAinc\tNspanwise\tSspace\n")
        geometry_file.write(
            f"{round(wing.segments[index].nose_outer[0],5)}  "
            f"{round(wing.segments[index].nose_outer[1],5)}  "
            f"{round(wing.segments[index].nose_outer[2],5)}  "
            f"{round(wing.segments[index].outer_chord,5)}  "
            f"{round(wing.segments[index].outer_twist,5)}\n\n"
        )

        geometry_file.write(f"AFIL  0.0  1.0\n")
        geometry_file.write(
            f'{airfoil_path + "/" + wing.segments[index].outer_airfoil + ".dat"}\n\n'
        )

        if segment.control is not None:
            GeometryFile.build_geo_surface_section_control(self, geometry_file, segment)

    def build_geo_surface(self, geometry_file):
        # surface_name e.g wing or empennage
        for i, wing in enumerate(
            self.plane.wings.values()
        ):  # [... , self.plane.empennage]
            geometry_file.write(f"SURFACE\n")
            geometry_file.write(f"{wing.tag}\n")  # for example "Main Wing"
            geometry_file.write(
                f"{wing.n_chordwise}  {wing.c_space}  "
                f"{wing.n_spanwise}  {wing.s_space}\n\n"
            )
            geometry_file.write(f"Component\n")
            geometry_file.write(f"{i+1}\n\n")  # component value/index
            if wing.symmetric:
                geometry_file.write(f"YDUPLICATE\n")
                geometry_file.write(f"0.0\n\n")
            geometry_file.write(f"TRANSLATE\n")
            geometry_file.write(f"{0}\t{0}\t{0}\n\n")
            geometry_file.write(f"ANGLE\n")
            geometry_file.write(f"{wing.angle:.5f}\n\n")
            geometry_file.write(f"#--------------------\n")

            GeometryFile.build_geo_surface_section(self, geometry_file, wing)

    def build_geometry_file(self, plane_name=None, cdp=0, mach=0):
        """
        This method creates a geometry file as input for AVL.

        Coordinate system: X downstream, Y out the right wing, Z up
        """
        tool_path = Path(__file__).resolve().parents[5]
        file_path = Path(tool_path, "temporary", f"geometry_file{get_pid()}.avl")
        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, "w") as geometry_file:
            GeometryFile.build_geo_header(self, geometry_file)
            geometry_file.write(f"\n#======================\n")
            GeometryFile.build_geo_surface(self, geometry_file)

        # self.plane.avl.inputs.avl_file = file_path


# ========== Mass File ==========


class MassFile:
    """
    Mass Input File -- xxx.mass
    ===========================

    This optional file describes the mass and inertia properties of the
    configuration.  It also defines units to be used for run case setup.
    These units may want to be different than those used to define
    the geometry.  Sample input xxx.mass files are in the runs/ subdirectory.


    Coordinate system
    -----------------
    The geometry axes used in the xxx.mass file are exactly the same as those used
    in the xxx.avl file.


    File format
    -----------
    A sample file for an RC glider is shown below.  Comment lines begin
    with a "#".  Everything after and including a "!" is ignored.
    Blank lines are ignored.



    #  SuperGee
    #
    #  Dimensional unit and parameter data.
    #  Mass & Inertia breakdown.

    #  Names and scalings for units to be used for trim and eigenmode calculations.
    #  The Lunit and Munit values scale the mass, xyz, and inertia table data below.
    #  Lunit value will also scale all lengths and areas in the AVL input file.
    Lunit = 0.0254 m
    Munit = 0.001  kg
    Tunit = 1.0    s

    #-------------------------
    #  Gravity and density to be used as default values in trim setup (saves runtime typing).
    #  Must be in the unit names given above (i.e. m,kg,s).
    g   = 9.81
    rho = 1.225

    #-------------------------
    #  Mass & Inertia breakdown.
    #  x y z  is location of item's own CG.
    #  Ixx... are item's inertias about item's own CG.
    #
    #  x,y,z system here must be exactly the same one used in the .avl input file
    #     (same orientation, same origin location, same length units)
    #
    #  mass   x     y     z    [ Ixx     Iyy    Izz     Ixy   Ixz   Iyz ]
    *   1.    1.    1.    1.     1.     1.      1.      1.    1.    1.
    +   0.    0.    0.    0.     0.     0.      0.      0.    0.    0.
       58.0   3.34  12.0  1.05   4400   180     4580        ! right wing
       58.0   3.34 -12.0  1.05   4400   180     4580        ! left wing
       16.0  -5.2   0.0   0.0       0    80       80        ! fuselage pod
       18.0  13.25  0.0   0.0       0   700      700        ! boom+rods
       22.0  -7.4   0.0   0.0       0     0        0        ! battery
        2.0  -2.5   0.0   0.0       0     0        0        ! jack
        9.0  -3.8   0.0   0.0       0     0        0        ! RX
        9.0  -5.1   0.0   0.0       0     0        0        ! rud servo
        6.0  -5.9   0.0   0.0       0     0        0        ! ele servo
        9.0   2.6   1.0   0.0       0     0        0        ! R wing servo
        9.0   2.6  -1.0   0.0       0     0        0        ! L wing servo
        2.0   1.0   0.0   0.5       0     0        0        ! wing connector
        1.0   3.0   0.0   0.0       0     0        0        ! wing pins
        6.0  29.0   0.0   1.0      70     2       72        ! stab
        6.0  33.0   0.0   2.0      35    39        4        ! rudder
        0.0  -8.3   0.0   0.0       0     0        0        ! nose wt.


    Units
    - - -
    The first three lines

      Lunit = 0.0254 m
      Munit = 0.001  kg
      Tunit = 1.0    s

    give the magnitudes and names of the units to be used for run case setup
    and possibly for eigenmode calculations.  In this example, standard SI units
    (m,kg,s) are chosen.  But the data in xxx.avl and xxx.mass is given in units
    of Lunit = 1 inch, which is therefore declared here to be equal to "0.0254 m".
    If the data was given in centimeters, the statement would read

      Lunit = 0.01 m

    and if it was given directly in meters, it would read

      Lunit = 1.0 m

    Similarly, Munit used here in this file is the gram, but since the kilogram (kg)
    is to be used for run case calculations, the Munit declaration is

      Munit = 0.001 kg

    If the masses here were given in ounces, the declaration would be

      Munit = 0.02835 kg

    The third line gives the time unit name and magnitude.

    If any of the three unit lines is absent, that unit's magnitude will
    be set to 1.0, and the unit name will simply remain as "Lunit",
    "Munit", or "Tunit".


    The moments of inertia and products of inertia components above are defined as

      Ixx  =  int (y^2 + z^2) dm
      Iyy  =  int (x^2 + z^2) dm
      Izz  =  int (x^2 + y^2) dm
      Ixy  =  int  x y  dm
      Ixz  =  int  x y  dm
      Iyz  =  int  x y  dm

    where the integral is over all the mass elements dm with locations x,y,z.
    The symmetric moment of inertia tensor is given in terms of these
    components as follows.

                             2
                  | 0 -z  y |          | Ixx -Ixy -Ixz |
      =           |         |          |               |
      I  =  - int | z  0 -x | dm   =   |-Ixy  Iyy -Iyz |
                  |         |          |               |
                  |-y  x  0 |          |-Ixz -Iyz  Izz |



    Constants
    - - - - -
    The 4th and 5th lines give the default gravitational acceleration and
    air density, in the units given above.  If these statements are absent,
    these constants default to 1.0, and will need to be changed manually at runtime.


    Mass, Position, and Inertia Data
    - - - - - - - - - - - - - - - - -
    A line which begins with a "*" specifies multipliers to be applied
    to all subsequent data.  If such a line is absent, these default to 1.
    A line which begins with a "+" specifies added constants to be applied
    to all subsequent data.  If such a line is absent, these default to 0.

    Lines with only numbers are interpreted as mass, position, and inertia data.
    Each such line contains values for

      mass   x     y     z      Ixx    Iyy    Izz    Ixz    Ixy    Iyz

    as described in the file comments above.  Note that the inertias are
    taken about that item's own mass centroid given by x,y,z.  The finer
    the mass breakdown, the less important these self-inertias become.
    The inertia values on each line are optional, and any ones which
    are absent will be assumed to be zero.

    Additional multiplier or adder lines can be put anywhere in the data lines,
    and these then re-define these mulipliers and adders for all subsequent lines.
    For example:

    #  mass   x     y     z      Ixx     Iyy     Izz    Ixz

    *   1.2   1.    1.    1.     1.     1.       1.     1.
    +   0.    0.2   0.    0.     0.     0.       0.     0.
       58.0   3.34  12.0  1.05   4400   180      4580    0.   ! right wing
       58.0   3.34 -12.0  1.05   4400   180      4580    0.   ! left wing

    *   1.    1.    1.    1.     1.     1.       1.     1.
    +   0.    0.    0.    0.     0.     0.       0.     0.
       16.0  -5.2   0.0   0.0        0    80        80    0.  ! fuselage pod
       18.0  13.25  0.0   0.0        0   700       700    0.  ! boom+rods
       22.0  -7.4   0.0   0.0        0     0         0    0.  ! battery


    Data lines 1-2 have all their masses scaled up by 1.2, and their locations
    shifted by delta(x) = 0.2.  Data lines 3-5 revert back to the defaults.
    """

    def __init__(self, plane) -> None:
        self.plane = plane

    def build_mass_of_components(self, mass_file, n_o_comp):
        """
        adds components to the mass table of the AVL mass file.
        """
        mass_file.write(
            f"\t{self.plane.n_o_comp.mass.mass}\t{self.plane.n_o_comp.mass.x_location}"
            f"\t{self.plane.n_o_comp.mass.y_location}\t{self.plane.n_o_comp.mass.z_location}"
            f"\t{self.plane.n_o_comp.mass.i_xx}\t{self.plane.n_o_comp.mass.i_yy}\t"
            f"{self.plane.n_o_comp.mass.i_zz}"
            f"\t{self.plane.n_o_comp.mass.i_xy}\t{self.plane.n_o_comp.mass.i_xz}\t"
            f"{self.plane.n_o_comp.i_yz}"
        )

    def build_mass_table(self, mass_file):
        """
        builds the mass table for the AVL mass file.

        #  Mass & Inertia breakdown.
        #  x y z  is location of item's own CG.
        #  Ixx... are item's inertias about item's own CG.
        #
        #  x,y,z system here must be exactly the same one used in the .avl input file
        #     (same orientation, same origin location, same length units)
        #
        #  mass   x     y     z    [ Ixx     Iyy    Izz     Ixy   Ixz   Iyz ]
        *   1.    1.    1.    1.     1.     1.      1.      1.    1.    1.
        +   0.    0.    0.    0.     0.     0.      0.      0.    0.    0.
           58.0   3.34  12.0  1.05   4400   180     4580        ! right wing
           58.0   3.34 -12.0  1.05   4400   180     4580        ! left wing
           16.0  -5.2   0.0   0.0       0    80       80        ! fuselage pod
           18.0  13.25  0.0   0.0       0   700      700        ! boom+rods
           22.0  -7.4   0.0   0.0       0     0        0        ! battery
            2.0  -2.5   0.0   0.0       0     0        0        ! jack
            9.0  -3.8   0.0   0.0       0     0        0        ! RX
            9.0  -5.1   0.0   0.0       0     0        0        ! rud servo
            6.0  -5.9   0.0   0.0       0     0        0        ! ele servo
            9.0   2.6   1.0   0.0       0     0        0        ! R wing servo
            9.0   2.6  -1.0   0.0       0     0        0        ! L wing servo
            2.0   1.0   0.0   0.5       0     0        0        ! wing connector
            1.0   3.0   0.0   0.0       0     0        0        ! wing pins
            6.0  29.0   0.0   1.0      70     2       72        ! stab
            6.0  33.0   0.0   2.0      35    39        4        ! rudder
            0.0  -8.3   0.0   0.0       0     0        0        ! nose wt.

        *****

        The moments of inertia and products of inertia components above are defined as

          Ixx  =  int (y^2 + z^2) dm
          Iyy  =  int (x^2 + z^2) dm
          Izz  =  int (x^2 + y^2) dm
          Ixy  =  int  x y  dm
          Ixz  =  int  x y  dm
          Iyz  =  int  x y  dm

        where the integral is over all the mass elements dm with locations x,y,z.
        The symmetric moment of inertia tensor is given in terms of these
        components as follows.

                                 2
                      | 0 -z  y |          | Ixx -Ixy -Ixz |
          =           |         |          |               |
          I  =  - int | z  0 -x | dm   =   |-Ixy  Iyy -Iyz |
                      |         |          |               |
                      |-y  x  0 |          |-Ixz -Iyz  Izz |

        *****

                Mass, Position, and Inertia Data
        - - - - - - - - - - - - - - - - -
        A line which begins with a "*" specifies multipliers to be applied
        to all subsequent data.  If such a line is absent, these default to 1.
        A line which begins with a "+" specifies added constants to be applied
        to all subsequent data.  If such a line is absent, these default to 0.

        Lines with only numbers are interpreted as mass, position, and inertia data.
        Each such line contains values for

          mass   x     y     z      Ixx    Iyy    Izz    Ixz    Ixy    Iyz

        as described in the file comments above.  Note that the inertias are
        taken about that item's own mass centroid given by x,y,z.  The finer
        the mass breakdown, the less important these self-inertias become.
        The inertia values on each line are optional, and any ones which
        are absent will be assumed to be zero.

        Additional multiplier or adder lines can be put anywhere in the data lines,
        and these then re-define these mulipliers and adders for all subsequent lines.
        For example:

        #  mass   x     y     z      Ixx     Iyy     Izz    Ixz

        *   1.2   1.    1.    1.     1.     1.       1.     1.
        +   0.    0.2   0.    0.     0.     0.       0.     0.
           58.0   3.34  12.0  1.05   4400   180      4580    0.   ! right wing
           58.0   3.34 -12.0  1.05   4400   180      4580    0.   ! left wing

        *   1.    1.    1.    1.     1.     1.       1.     1.
        +   0.    0.    0.    0.     0.     0.       0.     0.
           16.0  -5.2   0.0   0.0        0    80        80    0.  ! fuselage pod
           18.0  13.25  0.0   0.0        0   700       700    0.  ! boom+rods
           22.0  -7.4   0.0   0.0        0     0         0    0.  ! battery


        Data lines 1-2 have all their masses scaled up by 1.2, and their locations
        shifted by delta(x) = 0.2.  Data lines 3-5 revert back to the defaults.
        """
        mass_file.write(
            f"#  mass   x     y     z    [ Ixx     Iyy    Izz     Ixy   Ixz   Iyz ]\n"
        )
        mass_file.write(
            f"*   1.    1.    1.    1.     1.     1.      1.      1.    1.    1.\n"
        )
        mass_file.write(
            f"+   0.    0.    0.    0.     0.     0.      0.      0.    0.    0.\n"
        )
        # for component in self.plane:  # self.plane.components is list of components
        # print(hasattr(self.plane, "mass"))
        if hasattr(self.plane, "mass"):
            mass_file.write(
                f"\t{self.plane.mass}\t{self.plane.center_of_gravity[0]}"
                f"\t{self.plane.center_of_gravity[1]}\t{self.plane.center_of_gravity[2]}"
            )
        # print(self.plane.__dict__.items())
        else:  # noch nicht verwendbar
            for component in self.plane.__dict__.items():
                logging.debug(hasattr(component, "mass"))
                if hasattr(component, "mass"):
                    MassFile.build_mass_of_components(self, mass_file, component)

    def build_mass_file(self):
        """
        This method creates a mass file as input for AVL.

        #  Names and scalings for units to be used for trim and eigenmode calculations.
        #  The Lunit and Munit values scale the mass, xyz, and inertia table data below.
        #  Lunit value will also scale all lengths and areas in the AVL input file.
        Lunit = 0.0254 m
        Munit = 0.001  kg
        Tunit = 1.0    s

        #-------------------------
        #  Gravity and density to be used as default values in trim setup (saves runtime typing).
        #  Must be in the unit names given above (i.e. m,kg,s).
        g   = 9.81
        rho = 1.225

        *****

        Units
        - - -
        The first three lines

          Lunit = 0.0254 m
          Munit = 0.001  kg
          Tunit = 1.0    s

        give the magnitudes and names of the units to be used for run case setup
        and possibly for eigenmode calculations.  In this example, standard SI units
        (m,kg,s) are chosen.  But the data in xxx.avl and xxx.mass is given in units
        of Lunit = 1 inch, which is therefore declared here to be equal to "0.0254 m".
        If the data was given in centimeters, the statement would read

          Lunit = 0.01 m

        and if it was given directly in meters, it would read

          Lunit = 1.0 m

        Similarly, Munit used here in this file is the gram, but since the kilogram (kg)
        is to be used for run case calculations, the Munit declaration is

          Munit = 0.001 kg

        If the masses here were given in ounces, the declaration would be

          Munit = 0.02835 kg

        The third line gives the time unit name and magnitude.

        If any of the three unit lines is absent, that unit's magnitude will
        be set to 1.0, and the unit name will simply remain as "Lunit",
        "Munit", or "Tunit".

        *****

        Constants
        - - - - -
        The 4th and 5th lines give the default gravitational acceleration and
        air density, in the units given above.  If these statements are absent,
        these constants default to 1.0, and will need to be changed manually at runtime.
        """
        tool_path = Path(__file__).resolve().parents[5]
        file_path = Path(tool_path, "temporary", f"mass_file{get_pid()}.mass")
        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, "w") as mass_file:
            mass_file.write(f"Lunit = {Units.l_unit} m\n")
            mass_file.write(f"Munit = {Units.m_unit} kg\n")
            mass_file.write(f"Tunit = {Units.t_unit} s\n")
            mass_file.write(f"g = {Constants.g}\n")
            mass_file.write(f"rho = {Constants.rho}\n")
            MassFile.build_mass_table(self, mass_file)

        # self.plane.avl.inputs.mass_file = file_path


# ========== Test ===========

if __name__ == "__main__":
    pass
