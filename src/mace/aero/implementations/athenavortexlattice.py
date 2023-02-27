import os  # operation system
import numpy as np
from mace.aero.implementations import runsubprocess as runsub


def avl_output(avl_file, mass_file, run_file, total_forces_file_name, strip_forces_file_name,
               angle_of_attack=None, lift_coefficient=None, run_case: int = 1, maschine_readable_file=True):
    """
    For run_case != 1 please check runcase is available!
    """
    # --- Input file writer---

    if os.path.exists("total_forces_avl"):
        os.remove("total_forces_avl")
    if os.path.exists("strip_forces_avl"):
        os.remove("strip_forces_avl")

    input_file = open("input_file_avl.in", 'w')
    input_file.write("LOAD {0}\n".format(avl_file))
    input_file.write("MASS {0}\n".format(mass_file))
    # input_file.write("CASE {0}\n".format(run_file))
    input_file.write("OPER\n")
    if run_case != 1:                                           # select run_case
        input_file.write("{0}\n".format(run_case))
    if angle_of_attack is not None:                             # set angle of attack in degrees
        input_file.write("A A {0}\n".format(angle_of_attack))
    if lift_coefficient is not None:                             # set angle of attack with cl
        input_file.write("A C {0}\n".format(lift_coefficient))
    input_file.write("X\n")                         # execute runcase, XX executes all runcases but uses last runcase
    if maschine_readable_file:
        input_file.write("MRF\n")                               # maschine readable file
    input_file.write("FT\n")                                    # write total forces
    input_file.write("{0}\n".format(total_forces_file_name))
    input_file.write("FS\n")                                    # write strip forces
    input_file.write("{0}\n".format(strip_forces_file_name))

    input_file.write("\n")

    input_file.write("QUIT\n")
    input_file.close()

    # ---Run AVL---

    cmd = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/avl.exe < input_file_avl.in"  # external command to run
    runsub.run_subprocess(cmd)


def read_avl_files():
    file = open("total_forces_avl")
    lines = file.readlines()

# ------total_forces_avl file------

    # ---Trefftz Plane---

    clff: float = 0
    cdff: float = 0
    cyff: float = 0
    oswaldfactor: float = 0

    for line in lines:
        if line.endswith("| Trefftz Plane: CLff, CDff, CYff, e\n"):
            string = line.split("|")
            value_string = string[0]
            values = value_string.split()
            clff = float(values[0])
            cdff = float(values[1])
            cyff = float(values[2])
            oswaldfactor = float(values[3])

    # ---Reference Data---

    s_ref: float = 0
    c_ref: float = 0
    b_ref: float = 0

    for line in lines:
        if line.endswith("| Sref, Cref, Bref\n"):
            string = line.split("|")
            value_string = string[0]
            values = value_string.split()
            s_ref = float(values[0])
            c_ref = float(values[1])
            b_ref = float(values[2])

    # ---Number of Strips---

    number_of_strips: int = 0
    for line in lines:
        if line.endswith("| # strips\n"):
            string = line.split("|")
            value_string = string[0]
            values = value_string.split()
            number_of_strips = int(values[0])

    # ---Number of Surfaces---

    number_of_surfaces: int = 0

    for line in lines:
        if line.endswith("| # surfaces\n"):
            string = line.split("|")
            value_string = string[0]
            values = value_string.split()
            number_of_surfaces = int(values[0])

    # ---Number of Vortices---
    number_of_vortices: int = 0

    for line in lines:
        if line.endswith("| # vortices\n"):
            string = line.split("|")
            value_string = string[0]
            values = value_string.split()
            number_of_vortices = int(values[0])

    # ---Close file and test---

    file.close()

    print("CLff = {:.4f}\n".format(clff))
    print("CDff = {:.4f}\n".format(cdff))
    print("CYff = {:.4f}\n".format(cyff))
    print("Oswaldfactor = {:.4f}\n".format(oswaldfactor))

    print("Reference Wing area = {:.4f}\n".format(s_ref))
    print("Reference chord depth = {:.4f}\n".format(c_ref))
    print("Reference Wingspan = {:.4f}\n".format(b_ref))

    print("number of strips = {0}\n".format(number_of_strips))
    print("number of surfaces = {0}\n".format(number_of_surfaces))
    print("number of vortices = {0}\n".format(number_of_vortices))

# ------strip_forces_avl file------

    file = open("strip_forces_avl")

    lines = file.readlines()
    values: list = []
    for strip_number in range(number_of_strips):
        for line in lines:
            if strip_number + 1 < 10:
                if line.startswith("   {0}".format(strip_number + 1)) and "|" not in line:
                    values = line.split()
            elif strip_number + 1 < 100:
                if line.startswith("  {0}".format(strip_number + 1)) and "|" not in line:
                    values = line.split()
            elif strip_number + 1 < 1000:
                if line.startswith(" {0}".format(strip_number + 1)) and "|" not in line:
                    values = line.split()
            elif strip_number + 1 < 10000:
                if line.startswith("{0}".format(strip_number + 1)) and "|" not in line:
                    values = line.split()
            else:
                print("No valid data format")
        # print(values)

        j = int(values[0])              # entspricht strip_number
        xle = float(values[1])          # Xle
        yle = float(values[2])          # Yle
        zle = float(values[3])          # Zle
        chord = float(values[4])        # Chord
        area = float(values[5])         # Area
        c_cl = float(values[6])         # c_cl
        ai = float(values[7])           # ai
        cl_norm = float(values[8])      # cl_norm
        cl = float(values[9])           # cl
        cd = float(values[10])          # cd
        cdv = float(values[11])         # cdv
        cm_c = float(values[12])        # cm_c / 4
        cm_le = float(values[13])       # cm_LE
        cpx = float(values[14])         # C.P.x / c     Center of Pressure in x-Axis over chord (Druckpunkt)

        print("strip number = {0}\n".format(j), "Xle = {:.4f}\n".format(xle), "Yle = {:.4f}\n".format(yle),
              "Zle = {:.4f}\n".format(zle), "Chord = {:.4f}\n".format(chord), "Area = {:.4f}\n".format(area),
              "c_cl = {:.4f}\n".format(c_cl), "ai = {:.4f}\n".format(ai), "cl_norm = {:.4f}\n".format(cl_norm),
              "cl = {:.4f}\n".format(cl), "cd = {:.4f}\n".format(cd), "cdv = {:.4f}\n".format(cdv),
              "cm_c / 4 = {:.4f}\n".format(cm_c), "cm_LE = {:.4f}\n".format(cm_le), "C.P.x / c = {:.4f}\n".format(cpx))
    file.close()


# ---Test---


if __name__ == "__main__":
    avl_file = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/runs/supra.avl"
    mass_file = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/runs/supra.mass"
    run_file = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/runs/supra.run"
    total_forces_file_name = "total_forces_avl"
    strip_forces_file_name = "strip_forces_avl"

    avl_output(avl_file, mass_file, run_file, total_forces_file_name, strip_forces_file_name,
               angle_of_attack=0, run_case=1, maschine_readable_file=True)
    read_avl_files()
