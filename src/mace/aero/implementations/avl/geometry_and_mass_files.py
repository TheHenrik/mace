import os
from mace.domain import Plane, plane as pl
from mace.domain.parser import PlaneParser
from pathlib import Path

# ========== Geometry File ==========


class GeometryFile:
    """
    Vortex Lattice Spacing Distributions
    ------------------------------------

    Discretization of the geometry into vortex lattice panels
    is controlled by the spacing parameters described earlier:
    Sspace, Cspace, Bspace

    These must fall in the range  -3.0 ... +3.0 , and they
    determine the spanwise and lengthwise horseshoe vortex
    or body line node distributions as follows:

     parameter                              spacing
     ---------                              -------

        3.0        equal         |   |   |   |   |   |   |   |   |

        2.0        sine          || |  |   |    |    |     |     |

        1.0        cosine        ||  |    |      |      |    |  ||

        0.0        equal         |   |   |   |   |   |   |   |   |

       -1.0        cosine        ||  |    |      |      |    |  ||

       -2.0       -sine          |     |     |    |    |   |  | ||

       -3.0        equal         |   |   |   |   |   |   |   |   |

      Sspace (spanwise)  :    first section        ==>       last section
      Cspace (chordwise) :    leading edge         ==>       trailing edge
      Bspace (lengthwise):    frontmost point      ==>       rearmost point

    An intermediate parameter value will result in a blended distribution.

    The most efficient distribution (best accuracy for a given number of
    vortices) is usually the cosine (1.0) chordwise and spanwise.  If the
    wing does not have a significant chord slope discontinuity at the
    centerline, such as a straight, elliptical, or slightly tapered wing,
    then the -sine (-2.0) distribution from root to tip will be more
    efficient.  This is equivalent to a cosine distribution across the
    whole span.  The basic rule is that a tight chordwise distribution
    is needed at the leading and trailing edges, and a tight spanwise
    distribution is needed wherever the circulation is changing rapidly,
    such as taper breaks, and especially at flap breaks and wingtips.

    The tables below show the accuracy superiority of the cosine spacing
    over uniform spacing, at least for a simple wing planform.  With
    cosine spacing, a much smaller number of vortex elements is needed
    to reach the desired limiting answer to within a given tolerance.
    Note also that the uniform spacing always tends to overpredict
    the span efficiency, and its error decreases only linearly with
    the number of elements in each direction.


    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    Panel refinement study
    Rectangular wing


    # Cosine spacing in C and S
    #
    #1/Ni  Ni  Nj   CL       CDi        CLff     CDiff     e     e_error
    #
    1      1   4   4.18875  0.05807  4.19383  0.05829   0.9605   +0.09 %
    0.5    2   8   4.20951  0.05872  4.21465  0.05893   0.9595   -0.01 %
    0.25   4   16  4.21151  0.05876  4.21665  0.05898   0.9596   -0.00 %
    0.125  8   32  4.21184  0.05835  4.21695  0.05899   0.9596    0.00 %


    # Uniform spacing in C and S
    #
    #1/Ni  Ni  Nj   CL       CDi        CLff     CDiff     e     e_error
    #
    1      1   4   4.45637  0.05797  4.46144  0.05819   1.0887  +13.45 %
    0.5    2   8   4.35198  0.05894  4.35713  0.05917   1.0213   +6.43 %
    0.25   4   16  4.28694  0.05903  4.29211  0.05926   0.9896   +3.13 %
    0.125  8   32  4.25067  0.05895  4.25583  0.05917   0.9744   +1.54 %
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -




    A number of vortex-spacing rules must be followed to get good results
    from AVL, or any other vortex-lattice method:

    1) In a standard VL method, a trailing vortex leg must not pass
    close to a downstream control point, else the solution will be garbage.
    In practice, this means that surfaces which are lined up along
    the x direction (i.e. have the same or nearly the same y,z coordinates),
    MUST have the same spanwise vortex spacing.  AVL relaxes this requirement
    by employing a finite core size for each vortex on a surface which is
    influencing a control point in another aurface (unless the two surfaces
    share the same COMPONENT declaration).  This feature can be disabled
    by setting the core size to zero in the OPER sub-menu, Option
    sub-sub-menu, command C.  This reverts AVL to the standard VL method.

    2) Spanwise vortex spacings should be "smooth", with no sudden
    changes in spanwise strip width.  Adjust Nspan and Sspace parameters
    to get a smooth distribution.  Spacing should be bunched at
    dihedral and chord breaks, control surface ends, and especially
    at wing tips.  If a single spanwise spacing distribution is specified
    for a surface with multiple sections, the spanwise distribution
    will be fudged as needed to ensure that a point falls exactly
    on the section location.  Increase the number of spanwise points
    if the spanwise spacing looks ragged because of this fudging.

    3) If a surface has a control surface on it, an adequate number
    of chordwise vortices Nchord should be used to resolve the
    discontinuity in the camberline angle at the hingeline.  It is
    possible to define the control surface as a separate SURFACE
    entity.  Cosine chordwise spacings then produce bunched points
    exactly at the hinge line, giving the best accuracy.  The two
    surfaces must be given the same COMPONENT and the same spanwise point
    spacing for this to work properly. Such extreme measures are
    rarely necessary in practice, however.  Using a single surface
    with extra chordwise spacing is usually sufficient.

    4) When attempting to increase accuracy by using more vortices,
    it is in general necessary to refine the vortex spacings in both
    the spanwise AND in the chordwise direction.  Refining only
    along one direction may not converge to the correct result,
    especially locally wherever the bound vortex line makes a sudden bend,
    such as a dihedral break, or at the center of a swept wing.
    In some special configurations, such as an unswept planar wing,
    the chordwise spacing may not need to be refined at all to
    get good accuracy, but for most cases the chordwise spacing
    will be significant.
    """
    def __init__(self, plane: Plane) -> None:
        self.plane = plane

    def build_geo_header(self, geometry_file):
        """
        Mach  = default freestream Mach number for Prandtl-Glauert correction

        iYsym   =  1  case is symmetric about Y=0    , (X-Z plane is a solid wall)
                = -1  case is antisymmetric about Y=0, (X-Z plane is at const. Cp)
                =  0  no Y-symmetry is assumed

        iZsym   =  1  case is symmetric about Z=Zsym    , (X-Y plane is a solid wall)
                = -1  case is antisymmetric about Z=Zsym, (X-Y plane is at const. Cp)
                =  0  no Z-symmetry is assumed (Zsym ignored)

        Sref  = reference area  used to define all coefficients (CL, CD, Cm, etc)
        Cref  = reference chord used to define pitching moment (Cm)
        Bref  = reference span  used to define roll,yaw moments (Cl,Cn)

        X,Y,Zref  = default location about which moments and rotation rates are defined
                    (if doing trim calculations, XYZref must be the CG location,
                    which can be imposed with the MSET command described later)

        CDp = default profile drag coefficient added to geometry, applied at XYZref
                (assumed zero if this line is absent, for previous-version compatibility)
        """

        if self.plane.name is not None:
            geometry_file.write(f'{self.plane.name}\n')
        geometry_file.write(f'# Mach\n')
        geometry_file.write(f'{self.plane.reference_values.mach}\n')
        geometry_file.write(f'#IYsym\tIZsym\tZsym\n')
        geometry_file.write(f'{self.plane.reference_values.iy_sym:<10}'
                            f'{self.plane.reference_values.iz_sym:<10}'
                            f'{self.plane.reference_values.z_sym:<10}\n\n')  # iYsym has to be 0 for YDUPLICATE
        geometry_file.write(f'#Sref\tCref\tBref\n')
        geometry_file.write(f'{self.plane.reference_values.s_ref:<10}'
                            f'{self.plane.reference_values.c_ref:<10}'
                            f'{self.plane.reference_values.b_ref:<10}\n')
        geometry_file.write(f'#Xref\tYref\tZref\n')
        geometry_file.write(f'{self.plane.reference_values.x_ref:<10}'
                            f'{self.plane.reference_values.y_ref:<10}'
                            f'{self.plane.reference_values.z_ref:<10}\n')
        # if self.plane.aero_coeffs.cdp != 0:
        #     geometry_file.write(f'# CDp\n')
        #     geometry_file.write(f'{self.plane.aero_coeffs.cdp}\n')

        """if plane_name is not None:
            geometry_file.write("{0}\n".format(self.plane.name))
        geometry_file.write("# Mach\n")
        geometry_file.write("{0}\n".format(mach))
        geometry_file.write("#IYsym\tIZsym\tZsym\n")
        geometry_file.write("{0}\t{1}\t{2}\n".format(iy_sym, iz_sym, z_sym))
        geometry_file.write("#Sref\tCref\tBref\n")
        geometry_file.write("{0}\t{1}\t{2}\n".format(s_ref, c_ref, b_ref))
        geometry_file.write("#Xref\tYref\tZref\n")
        geometry_file.write("{0}\t{1}\t{2}\n".format(x_ref, y_ref, z_ref))
        if cdp != 0:
            geometry_file.write("# CDp\n")
            geometry_file.write("{0}\n".format(profile_drag))"""

    def build_geo_surface_section_control(self, geometry_file, element):
        """
        multiple different controls are possible on th same surface

        *****

        CONTROL                              | (keyword)
        elevator  1.0  0.6   0. 1. 0.   1.0  | name, gain,  Xhinge,  XYZhvec,  SgnDup


        The CONTROL keyword declares that a hinge deflection at this section
        is to be governed by one or more control variables.  An arbitrary number
        of control variables can be used, limited only by the array limit NDMAX.

        The data line quantities are...

         name     name of control variable
         gain     control deflection gain, units:  degrees deflection / control variable
         Xhinge   x/c location of hinge.
                   If positive, control surface extent is Xhinge..1  (TE surface)
                   If negative, control surface extent is 0..-Xhinge (LE surface)
         XYZhvec  vector giving hinge axis about which surface rotates
                   + deflection is + rotation about hinge vector by righthand rule
                   Specifying XYZhvec = 0. 0. 0. puts the hinge vector along the hinge
         SgnDup   sign of deflection for duplicated surface
                   An elevator would have SgnDup = +1
                   An aileron  would have SgnDup = -1

        Control derivatives will be generated for all control variables
        which are declared.


        More than one variable can contribute to the motion at a section.
        For example, for the successive declarations

        CONTROL
        aileron  1.0  0.7  0. 1. 0.  -1.0

        CONTROL
        flap     0.3  0.7  0. 1. 0.   1.0

        the overall deflection will be

         control_surface_deflection  =  1.0 * aileron  +  0.3 * flap


        The same control variable can be used on more than one surface.
        For example the wing sections might have

        CONTROL
        flap     0.3   0.7  0. 1. 0.   1.0

        and the horizontal tail sections might have

        CONTROL
        flap     0.03  0.5  0. 1. 0.   1.0

        with the latter simulating 10:1 flap -> elevator mixing.


        A partial-span control surface is specified by declaring
        CONTROL data only at the sections where the control surface
        exists, including the two end sections.  For example,
        the following wing defined with three sections (i.e. two panels)
        has a flap over the inner panel, and an aileron over the
        outer panel.

        SECTION
        0.0  0.0  0.0   2.0   0.0   | Xle Yle Zle   Chord Ainc
        CONTROL
        flap     1.0   0.80   0. 0. 0.   1   | name, gain,  Xhinge,  XYZhvec,  SgnDup

        SECTION
        0.0  8.0  0.0   2.0   0.0   | Xle Yle Zle   Chord Ainc
        CONTROL
        flap     1.0   0.80   0. 0. 0.   1   | name, gain,  Xhinge,  XYZhvec,  SgnDup
        CONTROL
        aileron  1.0   0.85   0. 0. 0.  -1   | name, gain,  Xhinge,  XYZhvec,  SgnDup

        SECTION
        0.2 12.0  0.0   1.5   0.0   | Xle Yle Zle   Chord Ainc
        CONTROL
        aileron  1.0   0.85   0. 0. 0.  -1   | name, gain,  Xhinge,  XYZhvec,  SgnDup


        The control gain for a control surface does not need to be equal
        at each section.  Spanwise stations between sections receive a gain
        which is linearly interpolated from the two bounding sections.
        This allows specification of flexible-surface control systems.
        For example, the following surface definition models wing warping
        which is linear from root to tip.  Note that the "hinge" is at x/c=0.0,
        so that the entire chord rotates in response to the aileron deflection.

        SECTION
        0.0  0.0  0.0   2.0   0.0   | Xle Yle Zle   Chord Ainc
        CONTROL
        aileron  0.0   0.     0. 0. 0.  -1   | name, gain,  Xhinge,  XYZhvec,  SgnDup

        SECTION
        0.2 12.0  0.0   1.5   0.0   | Xle Yle Zle   Chord Ainc
        CONTROL
        aileron  1.0   0.     0. 0. 0.  -1   | name, gain,  Xhinge,  XYZhvec,  SgnDup



        Non-symmetric control effects, such as Aileron Differential, can be specified
        by a non-unity SgnDup magnitude.  For example,

        SECTION
        0.0  6.0  0.0   2.0   0.0   | Xle Yle Zle   Chord Ainc
        CONTROL
        aileron  1.0   0.7    0. 0. 0.  -2.0   | name, gain,  Xhinge,  XYZhvec,  SgnDup

        SECTION
        0.0 10.0  0.0   2.0   0.0   | Xle Yle Zle   Chord Ainc
        CONTROL
        aileron  1.0   0.7    0. 0. 0.  -2.0   | name, gain,  Xhinge,  XYZhvec,  SgnDup

        will result in the duplicated aileron having a deflection opposite and
        2.0 times larger than the defined aileron.  Note that this will have
        the proper effect only in one direction.  In the example above, the
        two aileron surfaces deflect as follows:

          Right control surface:   1.0*aileron         =  1.0*aileron
          Left  control surface:   1.0*aileron*(-2.0)  = -2.0*aileron

        which is the usual way Aileron Differential is implemented if "aileron"
        is positive. To get the same effect with a negative "aileron" control change,
        the definitions would have to be as follows.

        SECTION
        0.0  6.0  0.0   2.0   0.0   | Xle Yle Zle   Chord Ainc
        CONTROL
        aileron  2.0   0.7    0. 0. 0.  -0.5   | name, gain,  Xhinge,  XYZhvec,  SgnDup

        SECTION
        0.0 10.0  0.0   2.0   0.0   | Xle Yle Zle   Chord Ainc
        CONTROL
        aileron  2.0   0.7    0. 0. 0.  -0.5   | name, gain,  Xhinge,  XYZhvec,  SgnDup

        This then gives:

          Right control surface:   2.0*aileron         = -2.0*(-aileron)
          Left  control surface:   2.0*aileron*(-0.5)  =  1.0*(-aileron)

        which is the correct mirror image of the previous case if "aileron" is negative.

        #############################################################
        not implemented/used yet:
        #############################################################

        CLAF        |  (keyword)
        CLaf        |  dCL/da scaling factor

        This scales the effective dcl/da of the section airfoil as follows:
         dcl/da  =  2 pi CLaf
        The implementation is simply a chordwise shift of the control point
        relative to the bound vortex on each vortex element.

        The intent is to better represent the lift characteristics
        of thick airfoils, which typically have greater dcl/da values
        than thin airfoils.  A good estimate for CLaf from 2D potential
        flow theory is

          CLaf  =  1 + 0.77 t/c

        where t/c is the airfoil's thickness/chord ratio.  In practice,
        viscous effects will reduce the 0.77 factor to something less.
        Wind tunnel airfoil data or viscous airfoil calculations should
        be consulted before choosing a suitable CLaf value.

        If the CLAF keyword is absent for a section, CLaf defaults to 1.0,
        giving the usual thin-airfoil lift slope  dcl/da = 2 pi.

        *****

        CDCL                         |  (keyword)
        CL1 CD1  CL2 CD2  CL3 CD3    |  CD(CL) function parameters

        The CDCL keyword specifies a simple profile-drag CD(CL) function
        for this section.  The function is parabolic between CL1..CL2 and
        CL2..CL3, with rapid increases in CD below CL1 and above CL3.
        See the SUBROUTINE CDCL header (in cdcl.f) for more details.

        The CD-CL polar is based on a simple interpolation with four CL regions:
         1) negative stall region
         2) parabolic CD(CL) region between negative stall and the drag minimum
         3) parabolic CD(CL) region between the drag minimum and positive stall
         4) positive stall region

                 CLpos,CDpos       <-  Region 4 (quadratic above CLpos)
        CL |   pt3--------
           |    /
           |   |                   <-  Region 3 (quadratic above CLcdmin)
           | pt2 CLcdmin,CDmin
           |   |
           |    \                  <-  Region 2 (quadratic below CLcdmin)
           |   pt1_________
           |     CLneg,CDneg       <-  Region 1 (quadratic below CLneg)
           |
           -------------------------
                           CD

        The CD(CL) function is interpolated for stations in between
        defining sections.  Hence, the CDCL declaration on any surface
        must be used either for all sections or for none (unless the SURFACE
        CDCL is specified).
        """

        geometry_file.write(f'\t\t#++++++++++++++++++++\n')
        geometry_file.write(f'\t\t\t#CONTROL\n')
        geometry_file.write(f'\t\t\t#Cname\tCgain\tXhinge\tHingeVec\t \t \tSgnDup\n')
        geometry_file.write(f'\t\t\t{element.c_name}\t{element.c_gain}\t{element.x_hinge}\t'
                            f'{element.hinge_vec[0]}\t{element.hinge_vec[1]}\t{element.hinge_vec[2]}\t'
                            f'{element.sgn_dup}\n')  # HingeVec most cases 0 0 0 -> along hinge

        """geometry_file.write("\t\t#++++++++++++++++++++\n")
        geometry_file.write("\t\t\t#CONTROL\n")  # multiple different controls are possible on the same surface
    
        geometry_file.write("\t\t\t#Cname\tCgain\tXhinge\tHingeVec\t \t \tSgnDup\n")
        geometry_file.write(
            "\t\t\t{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".format(
                c_name, c_gain, x_hinge, x_hinge_vec, y_hinge_vec, z_hinge_vec, sgn_dup))"""

    def get_chord(self, element):
        chord_inner = ((element.back_inner[0] - element.nose_inner[0]) ** 2 +
                       (element.back_inner[1] - element.nose_inner[1]) ** 2 + (
                        element.back_inner[2] - element.nose_inner[2]) ** 2) ** 0.5
        chord_outer = ((element.back_outer[0] - element.nose_outer[0]) ** 2 +
                       (element.back_outer[1] - element.nose_outer[1]) ** 2 + (
                        element.back_outer[2] - element.nose_outer[2]) ** 2) ** 0.5
        return chord_inner, chord_outer

    def build_geo_surface_section(self, geometry_file, element):
        """
        SECTION                             |  (keyword)
        0.0 5.0 0.2   0.50  1.50   5 -2.0   | Xle Yle Zle   Chord Ainc   [ Nspan Sspace ]

        The SECTION keyword defines an airfoil-section camber line at some
        spanwise location on the surface.

          Xle,Yle,Zle =  airfoil's leading edge location
          Chord       =  the airfoil's chord  (trailing edge is at Xle+Chord,Yle,Zle)
          Ainc        =  incidence angle, taken as a rotation (+ by RH rule) about
                         the surface's spanwise axis projected onto the Y-Z plane.
          Nspan       =  number of spanwise vortices until the next section [ optional ]
          Sspace      =  controls the spanwise spacing of the vortices      [ optional ]

        Note: Nspan and Sspace are explained in the docstring of the class GeometryFile.

        Nspan and Sspace are used here only if the overall Nspan and Sspace
        for the whole surface is not specified after the SURFACE keyword.
        The Nspan and Sspace for the last section in the surface are always ignored.

        Note that Ainc is used only to modify the flow tangency boundary
        condition on the airfoil camber line, and does not rotate the geometry
        of the airfoil section itself.  This approximation is consistent with
        linearized airfoil theory.

        The local chord and incidence angle are linearly interpolated between
        defining sections.  Obviously, at least two sections (root and tip)
        must be specified for each surface.

        The default airfoil camber line shape is a flat plate.  The NACA, AIRFOIL,
        and AFIL keywords, described below, are available to define non-flat
        camber lines.  If one of these is used, it must immediately follow
        the data line of the SECTION keyword.

        A positive surface-airfoil circulation and a corresponding positive local
        lift coefficient is defined by righthand rule in direction of successive
        sections. This also defines the tops of the section airfoils as the suction
        side for positive overall lift.  Therefore, to match conventional definitions,
        the order of the sections must be left to right across the span.

        NOTE!!
        If the sections are ordered right to left, then the overall airfoils will effectively
        be upside down.  The overall dCL/dalpha will still be positive as usual, but
        for positive CL the local cl values will be negative.  Needless to say,
        it's best to avoid these complications by ordering the sections left to right
        across the span (root to tip for the right wing).

        The section ordering of a vertical tail is somewhat more arbitrary.
        But a top to bottom ordering is most convenient, since positive local cl values
        then produce a positive yaw moment Cn.

        *****

        NACA      X1  X2          | (keyword)    [ optional x/c range ]
        4300                      | section NACA camberline

        The NACA keyword sets the camber line to the NACA 4-digit shape specified.

        If present, the optional X1 X2 numerical parameters indicate that only
        the x/c range X1..X2 from the coordinates is to be assigned to the surface.
        If the surface is a 20%-chord flap, for example, then X1 X2
        would be 0.80 1.00.  This allows the camber shape to be easily
        assigned to any number of surfaces in piecewise manner.

        If omitted,  X1, X2  default to  0.0, 1.0, which indicates that the
        entire airfoil is to be used to define the camber shape as usual.

        *****

        AIRFOIL   X1  X2          | (keyword)    [ optional x/c range ]
        1.0   0.0                 | x/c(1)  y/c(1)
        0.98  0.002               | x/c(2)  y/c(2)
         .     .                  |  .       .
         .     .                  |  .       .
         .     .                  |  .       .
        1.0  -0.01                | x/c(N)  y/c(N)


        The AIRFOIL keyword declares that the airfoil definition is input
        as a set of x/c, y/c pairs.

          x/c,y/c =  airfoil coordinates

        The x/c, y/c coordinates run from TE, to LE, back to the TE again
        in either direction.  These coordinates are splined, and the slope
        of the camber y(x) function is obtained from the middle y/c values
        between the top and bottom.  The number of points N is deterimined
        when a line without two readable numbers is encountered.

        If present, the optional X1 X2 parameters indicate that only the
        x/c range X1..X2 from the coordinates is to be assigned to the surface.
        If the surface is a 20%-chord flap, for example, then X1 X2
        would be 0.80 1.00.  This allows the camber shape to be easily
        assigned to any number of surfaces in piecewise manner.

        *****

        AFILE      X1  X2         | (keyword)   [ optional x/c range ]
        filename                  | filename string

        The AFILE keyword is essentially the same as AIRFOIL, except
        that the x/c,y/c pairs are generated from a standard (XFOIL-type)
        set of airfoil coordinates contained in the file "filename".
        The first line of this file is assumed to contain a string
        with the name of the airfoil (as written out with XFOIL's SAVE
        command).   If the path/filename has embedded blanks,
        double quotes should be used to delimit the string.

        If present, the optional X1 X2 numerical parameters indicate that only
        the x/c range X1..X2 from the coordinates is to be assigned to the surface.
        If the surface is a 20%-chord flap, for example, then X1 X2
        would be 0.80 1.00.  This allows the camber shape to be easily
        assigned to any number of surfaces in piecewise manner.

        If omitted,  X1, X2  default to  0.0, 1.0, which indicates that the
        entire airfoil is to be used to define the camber shape as usual.

        #############################################################
        not implemented/used yet:
        #############################################################

        DESIGN                  | (keyword)
        DName  Wdes             | design parameter name,  local weight

        This declares that the section angle Ainc is to be virtually perturbed
        by a design parameter, with name DName and local weight Wdes.

        For example, declarations for design variables "twist1" and "bias1"

        DESIGN
        twist1  -0.5

        DESIGN
        bias1   1.0

        Give an effective (virtual) section incidence that is set using the "twist1"
        and "bias1" design variables as:

          Ainc_total = Ainc  - 0.5*twist1_value + 1.0*bias_value

        where twist1_value and bias1_value are design parameters specified at runtime.

        The sensitivities of the flow solution to design variable changes
        can be displayed at any time during program execution.  Hence,
        design variables can be used to quickly investigate the effects
        of twist changes on lift, moments, induced drag, etc.

        Declaring the same design parameter with varying weights for multiple
        sections in a surface allows the design parameter to represent a convenient
        "design mode", such as linear washout, which influences all sections.
        """

        chord_outer = 0
        for index in range(len(element.segments)):
            geometry_file.write(f'SECTION\n')
            geometry_file.write(f'#Xle\tYle\tZle\tChord\tAinc\tNspanwise\tSspace\n')
            chord_inner = self.get_chord(element.segments[index])[0]
            chord_outer = self.get_chord(element.segments[index])[1]
            geometry_file.write(f'{element.segments[index].nose_inner[0]}  '
                                f'{element.segments[index].nose_inner[1]}  '
                                f'{element.segments[index].nose_inner[2]}  '
                                f'{chord_inner}  '
                                f'{element.segments[index].a_inc}')
            if element.segments[index].n_spanwise is not None:
                geometry_file.write(f'{  element.segments[index].n_spanwise}')
            if element.segments[index].s_space is not None:
                geometry_file.write(f'{  element.segments[index].s_space}')
            geometry_file.write(f'\n\n')

            if isinstance(element.segments[index].inner_airfoil.type, type(pl.Naca())):
                # geometry_file.write(f'NACA\n')
                # geometry_file.write(f'{element.segments[index].inner_airfoil.type.number_of_naca:0>4}\n\n')
                geometry_file.write(f'AFIL  0.0  1.0\n')
                geometry_file.write(f'{element.segments[index].inner_airfoil.type.filepath}\n\n')
            if isinstance(element.segments[index].inner_airfoil.type, type(pl.AirfoilFile())):
                geometry_file.write(f'AFIL  0.0  1.0\n')
                geometry_file.write(f'{element.segments[index].inner_airfoil.type.filepath}\n\n')

            if element.segments[index].control is not None:
                GeometryFile.build_geo_surface_section_control(self, geometry_file, element.segments[index])

        index = len(element.segments)-1
        geometry_file.write(f'SECTION\n')
        geometry_file.write(f'#Xle\tYle\tZle\tChord\tAinc\tNspanwise\tSspace\n')
        geometry_file.write(f'{element.segments[index].nose_outer[0]}  '
                            f'{element.segments[index].nose_outer[1]}  '
                            f'{element.segments[index].nose_outer[2]}  '
                            f'{chord_outer}  '
                            f'{element.segments[index].a_inc_outer}\n\n')

        if isinstance(element.segments[index].inner_airfoil.type, type(pl.Naca())):
            # geometry_file.write(f'NACA\n')
            # geometry_file.write(f'{element.segments[index].outer_airfoil.type.number_of_naca:0>4}\n\n')
            geometry_file.write(f'AFIL  0.0  1.0\n')
            geometry_file.write(f'{element.segments[index].inner_airfoil.type.filepath}\n\n')
        if isinstance(element.segments[index].inner_airfoil.type, type(pl.AirfoilFile())):
            geometry_file.write(f'AFIL  0.0  1.0\n')
            geometry_file.write(f'{element.segments[index].outer_airfoil.type.filepath}\n\n')

        if element.segments[index].control is not None:
            GeometryFile.build_geo_surface_section_control(self, geometry_file, element.segments[index])

    def build_geo_surface(self, geometry_file):
        """
        SURFACE              | (keyword)
        Main Wing            | surface name string
        12   1.0  20  -1.5   | Nchord  Cspace   [ Nspan Sspace ]

        The SURFACE keyword declares that a surface is being defined until
        the next SURFACE or BODY keyword, or the end of file is reached.
        A surface does not really have any significance to the underlying
        AVL vortex lattice solver, which only recognizes the overall
        collection of all the individual horseshoe vortices.  SURFACE
        is provided only as a configuration-defining device, and also
        as a means of defining individual surface forces.  This is
        necessary for structural load calculations, for example.

          Nchord =  number of chordwise horseshoe vortices placed on the surface
          Cspace =  chordwise vortex spacing parameter (described later)

          Nspan  =  number of spanwise horseshoe vortices placed on the surface [optional]
          Sspace =  spanwise vortex spacing parameter (described later)         [optional]

        If Nspan and Sspace are omitted (i.e. only Nchord and Cspace are present on line),
        then the Nspan and Sspace parameters will be expected for each section interval,
        as described later.

        Note: Nchord, Cspace, Nspan and Sspace are explained in the docstring of the class GeometryFile.



        *****

        COMPONENT       | (keyword) or INDEX
        3               | Lcomp

        This optional keywords COMPONENT (or INDEX for backward compatibility)
        allows multiple input SURFACEs to be grouped together into a composite
        virtual surface, by assigning each of the constituent surfaces the same
        Lcomp value.  Application examples are:
        - A wing component made up of a wing SURFACE and a winglet SURFACE
        - A T-tail component made up of horizontal and vertical tail SURFACEs.

        A common Lcomp value instructs AVL to _not_ use a finite-core model
        for the influence of a horseshoe vortex and a control point which lies
        on the same component, as this would seriously corrupt the calculation.

        If each COMPONENT is specified via only a single SURFACE block,
        then the COMPONENT (or INDEX) declaration is unnecessary.

        *****

        YDUPLICATE      | (keyword)
        0.0             | Ydupl

        The YDUPLICATE keyword is a convenient shorthand device for creating
        another surface which is a geometric mirror image of the one
        being defined.  The duplicated surface is _not_ assumed to be
        an aerodynamic image or anti-image, but is truly independent.
        A typical application would be for cases which have geometric
        symmetry, but not aerodynamic symmetry, such as a wing in yaw.
        Defining the right wing together with YDUPLICATE will conveniently
        create the entire wing.

        The YDUPLICATE keyword can _only_ be used if iYsym = 0 is specified.
        Otherwise, the duplicated real surface will be identical to the
        implied aerodynamic image surface, and velocities will be computed
        directly on the line-vortex segments of the images. This will
        almost certainly produce an arithmetic fault.

        The duplicated surface gets the same Lcomp value as the parent surface,
        so they are considered to be the same COMPONENT.  There is no significant
        effect on the results if they are in reality two physically-separate surfaces.


        Ydupl =  Y position of X-Z plane about which the current surface is
                    reflected to make the duplicate geometric-image surface.

        *****

        SCALE            |  (keyword)
        1.0  1.0  0.8    | Xscale  Yscale  Zscale

        The SCALE allows convenient rescaling for the entire surface.
        The scaling is applied before the TRANSLATE operation described below.

        Xscale,Yscale,Zscale  =  scaling factors applied to all x,y,z coordinates
                           (chords are also scaled by Xscale)

        *****

        TRANSLATE         |  (keyword)
        10.0  0.0  0.5    | dX  dY  dZ

        The TRANSLATE keyword allows convenient relocation of the entire
        surface without the need to change the Xle,Yle,Zle locations
        for all the defining sections.  A body can be translated without
        the need to modify the body shape coordinates.

        dX,dY,dZ =  offset added on to all X,Y,Z values in this surface.

        *****

        ANGLE       |  (keyword)
        2.0         | dAinc

        or

        AINC        |  (keyword)
        2.0         | dAinc

        The ANGLE keyword allows convenient changing of the incidence angle
        of the entire surface without the need to change the Ainc values
        for all the defining sections.  The rotation is performed about
        the spanwise axis projected onto the y-z plane.

          dAinc =  offset added on to the Ainc values for all the defining sections
                   in this surface

        #############################################################
        not implemented/used yet:
        #############################################################

        NOWAKE     |  (keyword)

        The NOWAKE keyword specifies that this surface is to NOT shed a wake,
        so that its strips will not have their Kutta conditions imposed.
        Such a surface will have a near-zero net lift, but it will still
        generate a nonzero moment.

        *****

        NOALBE    |  (keyword)

        The NOALBE keyword specifies that this surface is unaffected by
        freestream direction changes specified by the alpha,beta angles
        and p,q,r rotation rates.  This surface then reacts to only to
        the perturbation velocities of all the horseshoe vortices and
        sources and doublets in the flow.
        This allows the SURFACE/NOALBE object to model fixed surfaces such
        as a ground plane, wind tunnel walls, or a nearby other aircraft
        which is at a fixed flight condition.

        *****

        NOLOAD    |  (keyword)

        The NOLOAD keyword specifies that the force and moment on this surface
        is to NOT be included in the overall forces and moments of the configuration.
        This is typically used together with NOALBE, since the force on a ground
        plane or wind tunnel walls certainly is not to be considered as part
        of the aircraft force of interest.

        *****
        The following keyword declarations would be used in envisioned applications.

        1) Non-lifting fuselage modeled by its side-view and top-view profiles.
        This will capture the moment of the fuselage reasonably well.
        NOWAKE

        2) Another nearby aircraft, with both aircraft maneuvering together.
        This would be for trim calculation in formation flight.
        NOALBE
        NOLOAD

        3) Another nearby aircraft, with only the primary aircraft maneuvering.
        This would be for a flight-dynamics analysis in formation flight.
        NOLOAD

        4) Nearby wind tunnel walls or ground plane.
        NOALBE
        NOLOAD

        *****

        CDCL                         |  (keyword)
        CL1 CD1  CL2 CD2  CL3 CD3    |  CD(CL) function parameters


        The CDCL keyword placed in the SURFACE options specifies a simple
        profile-drag CD(CL) function for all sections in this SURFACE.
        The function is parabolic between CL1..CL2 and
        CL2..CL3, with rapid increases in CD below CL1 and above CL3.

        The CD-CL polar is based on a simple interpolation with four CL regions:
         1) negative stall region
         2) parabolic CD(CL) region between negative stall and the drag minimum
         3) parabolic CD(CL) region between the drag minimum and positive stall
         4) positive stall region

                 CLpos,CDpos       <-  Region 4 (quadratic above CLpos)
        CL |   pt3--------
           |    /
           |   |                   <-  Region 3 (quadratic above CLcdmin)
           | pt2 CLcdmin,CDmin
           |   |
           |    \                  <-  Region 2 (quadratic below CLcdmin)
           |   pt1_________
           |     CLneg,CDneg       <-  Region 1 (quadratic below CLneg)
           |
           -------------------------
                           CD

        See the SUBROUTINE CDCL header (in cdcl.f) for more details.

        The CD(CL) function is interpolated for stations in between
        defining sections.
        """
        # surface_name e.g wing or empennage
        for element in [self.plane.wing]:                       # [... , self.plane.empennage]
            if element.isactive:
                geometry_file.write(f'SURFACE\n')
                geometry_file.write(f'{element.name}\n')          # for example "Main Wing"
                # geometry_file.write(f'#Nchordwise\tCspace\tNspanwise\tSspace\n')
                geometry_file.write(f'{element.n_chordwise}  {element.c_space}  '
                                    f'{element.n_spanwise}  {element.s_space}\n\n')
                geometry_file.write(f'Component\n')
                geometry_file.write(f'{element.l_comp}\n\n')             # component value/index
                geometry_file.write(f'YDUPLICATE\n')
                geometry_file.write(f'0.0\n\n')
                # geometry_file.write(f'SCALE\n') # macht Probleme
                # geometry_file.write(f'{element.x_scale}\t{element.y_scale}\t{element.z_scale}\n\n')
                geometry_file.write(f'TRANSLATE\n')
                geometry_file.write(f'{element.x_translate}\t{element.y_translate}\t{element.z_translate}\n\n')
                geometry_file.write(f'ANGLE\n')
                geometry_file.write(f'{element.twist_angle:.5f}\n\n')
                geometry_file.write(f'#--------------------\n')

                GeometryFile.build_geo_surface_section(self, geometry_file, element)

    def build_geometry_file(self, number_of_surfaces, plane_name=None, cdp=0, mach=0):
        """
        This method creates a geometry file as input for AVL.

        Coordinate system: X downstream, Y out the right wing, Z up
        """
        tool_path = Path(__file__).resolve().parents[5]
        file_path = os.path.join(tool_path, "temporary/geometry_file.avl")
        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, "w") as geometry_file:
            GeometryFile.build_geo_header(self, geometry_file)
            geometry_file.write(f'\n#======================\n')
            for surface in range(number_of_surfaces):
                GeometryFile.build_geo_surface(self, geometry_file)

        self.plane.avl.inputs.avl_file = file_path
        print('AVL Geometry File built successfully')


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

    def __init__(self, plane: Plane) -> None:
        self.plane = plane

    def build_mass_of_components(self, mass_file, n_o_comp):
        """
        adds components to the mass table of the AVL mass file.
        """
        mass_file.write(f'\t{self.plane.n_o_comp.mass.mass}\t{self.plane.n_o_comp.mass.x_location}'
                        f'\t{self.plane.n_o_comp.mass.y_location}\t{self.plane.n_o_comp.mass.z_location}'
                        f'\t{self.plane.n_o_comp.mass.i_xx}\t{self.plane.n_o_comp.mass.i_yy}\t'
                        f'{self.plane.n_o_comp.mass.i_zz}'
                        f'\t{self.plane.n_o_comp.mass.i_xy}\t{self.plane.n_o_comp.mass.i_xz}\t'
                        f'{self.plane.n_o_comp.i_yz}')

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
        mass_file.write(f'#  mass   x     y     z    [ Ixx     Iyy    Izz     Ixy   Ixz   Iyz ]\n')
        mass_file.write(f'*   1.    1.    1.    1.     1.     1.      1.      1.    1.    1.\n')
        mass_file.write(f'+   0.    0.    0.    0.     0.     0.      0.      0.    0.    0.\n')
        # for component in self.plane:  # self.plane.components is list of components
        # print(hasattr(self.plane, "mass"))
        if hasattr(self.plane, "mass"):
            mass_file.write(f'\t{self.plane.mass[0]}\t{self.plane.mass[1]}'
                            f'\t{self.plane.mass[2]}\t{self.plane.mass[3]}')
        # print(self.plane.__dict__.items())
        else:       # noch nicht verwendbar
            for component in self.plane.__dict__.items():
                print(hasattr(component, "mass"))
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
        file_path = os.path.join(tool_path, "temporary/mass_file.mass")
        if os.path.exists(file_path):
            os.remove(file_path)

        with open(file_path, "w") as mass_file:
            mass_file.write(f'Lunit = {self.plane.parameters.units.l_unit} m\n')
            mass_file.write(f'Munit = {self.plane.parameters.units.m_unit} kg\n')
            mass_file.write(f'Tunit = {self.plane.parameters.units.t_unit} s\n')

            mass_file.write(f'g = {self.plane.parameters.constants.g}\n')
            mass_file.write(f'rho = {self.plane.parameters.constants.rho}\n')
            MassFile.build_mass_table(self, mass_file)

        self.plane.avl.inputs.mass_file = file_path
        print('AVL Mass File built successfully')


# ========== Test ===========

if __name__ == "__main__":
    plane = PlaneParser("testplane.toml").get("Plane")
    GeometryFile(plane).build_geometry_file(1)
    MassFile(plane).build_mass_file()
