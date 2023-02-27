import os


def build_geo_header(geometry_file, plane_name=None, cdp=0):

    if plane_name is not None:
        geometry_file.write("{0}\n".format(plane_name))
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
        geometry_file.write("{0}\n".format(profile_drag))


def build_geo_surface_section_control(geometry_file):

    geometry_file.write("#++++++++++++++++++++\n")
    geometry_file.write("#CONTROL\n")  # multiple different controls are possible on the same surface

    geometry_file.write("#Cname\tCgain\tXhinge\tHingeVec\t \t \tSgnDup\n")
    geometry_file.write(
        "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".format(
            c_name, c_gain, x_hinge, x_hinge_vec, y_hinge_vec, z_hinge_vec, sgn_dup))


def build_geo_surface_section(geometry_file):
    geometry_file.write("#SECTION\n")  # minimum of 2 sections required to build surface

    geometry_file.write("#Xle\tYle\tZle\tChord\tAinc\tNspanwise\tSspace\n")
    geometry_file.write(
        "{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\n".format(x_le, y_le, z_le, chord, a_inc, n_spanwise, s_space))
    # -Airfoil Data-
    if airfoil_data is not Naca:
        geometry_file.write("AFIL\t0.0\t1.0\n")  # uses complete chord length of airfoil
        geometry_file.write("{0}\n".format(airfoil_path))

    # build controls
    build_geo_surface_section_control(geometry_file)


def build_geo_surface(geometry_file):

    geometry_file.write("#SURFACE\n")
    geometry_file.write("{0}\n".format(surface_name))

    geometry_file.write("#Nchordwise\tCspace\tNspanwise\tSspace\n")
    geometry_file.write("{0}\t{1}\t{2}\t{3}\n".format(n_chordwise, c_space, n_spanwise, s_space))
    geometry_file.write("INDEX\n")
    geometry_file.write("{0}\n".format(index))
    geometry_file.write("ANGLE\n")
    geometry_file.write("{0}\n".format(twist_angle))  # twist angle bias for whole surface, Anstellwinkel ganze Surface
    geometry_file.write("SCALE\n")
    geometry_file.write("{0}\t{1}\t{2}\n".format(x_scale, y_scale, z_scale))
    geometry_file.write("TRANSLATE\n")
    geometry_file.write("{0}\t{1}\t{2}\n".format(x_translate, y_translate, z_translate))
    geometry_file.write("YDUPLICATE\n")
    geometry_file.write("0.0\n")  # duplicates about x-axis

    geometry_file.write("#--------------------\n")

    build_geo_surface_section()


def build_geometry_file(plane_name=None, cdp=0):
    if os.path.exists("geometry_file.avl"):
        os.remove("geometry_file.avl")

    geometry_file = open("geometry_file.avl", 'w')

    build_geo_header(geometry_file, plane_name, cdp)

    geometry_file.write("#======================\n")

    build_geo_surface(geometry_file)        # surface nr.1


