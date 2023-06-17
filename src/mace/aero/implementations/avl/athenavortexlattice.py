import os  # operation system
import numpy as np
from mace.aero.implementations import runsubprocess as runsub
from mace.domain import plane, Plane
from mace.domain.parser import PlaneParser
from mace.aero.implementations.avl.geometry_and_mass_files import GeometryFile, MassFile
from pathlib import Path


class AVL:
    def __init__(self, plane: Plane):
        self.plane = plane
        tool_path = Path(__file__).resolve().parents[5]
        self.avl_path = os.path.join(tool_path, "avl")
        self.total_forces_file_name = os.path.join(tool_path, "temporary/total_forces.avl")
        self.strip_forces_file_name = os.path.join(tool_path, "temporary/strip_forces.avl")
        self.input_file_name = os.path.join(tool_path, "temporary/input_file_avl.in")

    def run_avl(self, avl_file=None, mass_file=None,
                angle_of_attack=None, lift_coefficient=None, run_case: int = 1, maschine_readable_file=True):
        """
        For run_case != 1 please check if runcase is available! At the time not possible! (maybe in future versions)
        """

        if os.path.exists(self.total_forces_file_name):
            os.remove(self.total_forces_file_name)
        if os.path.exists(self.strip_forces_file_name):
            os.remove(self.strip_forces_file_name)

        # --- Input file writer---
        with open(self.input_file_name, 'w') as input_file:
            if avl_file:
                input_file.write(f'LOAD {avl_file}\n')
            else:
                input_file.write(f'LOAD {self.plane.avl.inputs.avl_file}\n')
            if mass_file:
                input_file.write(f'MASS {mass_file}\n')
            else:
                input_file.write(f'MASS {self.plane.avl.inputs.mass_file}\n')
            # input_file.write(f'CASE {run_file}\n')
            input_file.write(f'OPER\n')
            if run_case != 1:  # select run_case
                input_file.write(f'{run_case}\n')
            if angle_of_attack is not None:  # set angle of attack in degrees
                input_file.write(f'A A {angle_of_attack}\n')
            if lift_coefficient is not None:  # set angle of attack with cl
                input_file.write(f'A C {lift_coefficient}\n')
            input_file.write(f'X\n')  # execute runcase, XX executes all runcases but uses last runcase
            if maschine_readable_file:
                input_file.write(f'MRF\n')  # maschine readable file
            input_file.write(f'FT\n')  # write total forces
            input_file.write(f'{self.total_forces_file_name}\n')
            input_file.write(f'FS\n')  # write strip forces
            input_file.write(f'{self.strip_forces_file_name}\n')
            input_file.write("\n")
            input_file.write("QUIT\n")

        # ---Run AVL---
        cmd = self.avl_path + " <" + \
              self.input_file_name  # external command to run
        runsub.run_subprocess(cmd,timeout=15)
        list_of_process_ids = runsub.find_process_id_by_name("avl")
        runsub.kill_subprocesses(list_of_process_ids)

    def read_total_forces_avl_file(self, lines):

        # ---Trefftz Plane---
        for line in lines:
            if line.endswith("| Trefftz Plane: CLff, CDff, CYff, e\n"):
                string = line.split("|")
                value_string = string[0]
                values = value_string.split()
                self.plane.avl.outputs.clff = float(values[0])
                self.plane.avl.outputs.cdff = float(values[1])
                self.plane.avl.outputs.cyff = float(values[2])
                self.plane.avl.outputs.oswaldfactor = float(values[3])

        # ---Reference Data---
        for line in lines:
            if line.endswith("| Sref, Cref, Bref\n"):
                string = line.split("|")
                value_string = string[0]
                values = value_string.split()
                self.plane.avl.outputs.s_ref = float(values[0])
                self.plane.avl.outputs.c_ref = float(values[1])
                self.plane.avl.outputs.b_ref = float(values[2])

        for line in lines:
            if line.endswith("| Xref, Yref, Zref\n"):
                string = line.split("|")
                value_string = string[0]
                values = value_string.split()
                self.plane.avl.outputs.x_ref = float(values[0])
                self.plane.avl.outputs.y_ref = float(values[1])
                self.plane.avl.outputs.z_ref = float(values[2])

        # ---Number of Strips---
        for line in lines:
            if line.endswith("| # strips\n"):
                string = line.split("|")
                value_string = string[0]
                values = value_string.split()
                self.plane.avl.outputs.number_of_strips = int(values[0])

        # ---Number of Surfaces---
        for line in lines:
            if line.endswith("| # surfaces\n"):
                string = line.split("|")
                value_string = string[0]
                values = value_string.split()
                self.plane.avl.outputs.number_of_surfaces = int(values[0])

        # ---Number of Vortices---
        for line in lines:
            if line.endswith("| # vortices\n"):
                string = line.split("|")
                value_string = string[0]
                values = value_string.split()
                self.plane.avl.outputs.number_of_vortices = int(values[0])

        # ---Aerodynamic Coefficients---

        for line in lines:
            if line.endswith("| CLtot\n"):
                string = line.split("|")
                value_string = string[0]
                values = value_string.split()
                self.plane.aero_coeffs.lift_coeff.cl_tot = float(values[0])

        for line in lines:
            if line.endswith("| CDtot\n"):
                string = line.split("|")
                value_string = string[0]
                values = value_string.split()
                self.plane.aero_coeffs.drag_coeff.cd_tot = float(values[0])

        for line in lines:
            if line.endswith("| CDvis, CDind\n"):
                string = line.split("|")
                value_string = string[0]
                values = value_string.split()
                self.plane.aero_coeffs.drag_coeff.cd_vis = float(values[0])
                self.plane.aero_coeffs.drag_coeff.cd_ind = float(values[1])

    def read_strip_forces_avl_file(self, lines):
        # ---Surface Data---
        surface_data = np.array([])
        hits = 0
        for line in lines:
            if line.endswith("| Surface #, # Chordwise, # Spanwise, First strip\n"):
                hits += 1
                string = line.split("|")
                values = np.fromstring(string[0], dtype=int, sep=' ')
                if hits == 1:
                    surface_data = values
                else:
                    surface_data = np.vstack((surface_data, values))
        self.plane.avl.outputs.surface_data = surface_data

        strip_forces = np.array([])
        for strip_number in range(self.plane.avl.outputs.number_of_strips):
            values = np.array([])
            for line in lines:
                if strip_number + 1 < 10:
                    if line.startswith("   {0}".format(strip_number + 1)) and "|" not in line:
                        values = np.fromstring(line, sep=' ')  # np.loadtxt(line)
                elif strip_number + 1 < 100:
                    if line.startswith("  {0}".format(strip_number + 1)) and "|" not in line:
                        values = np.fromstring(line, sep=' ')  # np.loadtxt(line)
                elif strip_number + 1 < 1000:
                    if line.startswith(" {0}".format(strip_number + 1)) and "|" not in line:
                        values = np.fromstring(line, sep=' ')  # np.loadtxt(line)
                elif strip_number + 1 < 10000:
                    if line.startswith("{0}".format(strip_number + 1)) and "|" not in line:
                        values = np.fromstring(line, sep=' ')  # np.loadtxt(line)
                else:
                    print("No valid data format")
            if strip_number == 0:
                strip_forces = values
            else:
                strip_forces = np.vstack((strip_forces, values))
        self.plane.avl.outputs.strip_forces = strip_forces

    def read_avl_output(self):
        with open(self.total_forces_file_name) as file:
            lines = file.readlines()
            self.read_total_forces_avl_file(lines)
        with open(self.strip_forces_file_name) as file:
            lines = file.readlines()
            self.read_strip_forces_avl_file(lines)

        # print(self.plane.avl.outputs.surface_data.shape[0])
        # print(self.plane.avl.outputs.surface_data)
        for i in range(self.plane.avl.outputs.surface_data.shape[0]):
            first_strip = self.plane.avl.outputs.surface_data[i, -1]
            last_strip = first_strip + self.plane.avl.outputs.surface_data[i, -2] - 1
            # print(f'Surface{i} has first strip {first_strip} and last strip {last_strip} with {self.plane.avl.outputs.surface_data[i, -2]} strips\n ')
            strips = self.plane.avl.outputs.strip_forces[first_strip - 1: last_strip, :]
            first_and_last_strip = {'first_strip': first_strip, 'last_strip': last_strip}
            surface_dictionary_data = {'first_strip': first_strip, 'last_strip': last_strip, 'strips': strips}
            self.plane.avl.outputs.first_and_last_strips[i + 1] = first_and_last_strip
            self.plane.avl.outputs.surface_dictionary[i + 1] = surface_dictionary_data


def read_avl_output():
    """
    returns a tuple of:
    (clff , cdff, cyff, oswaldfactor, s_ref, c_ref, b_ref, x_ref, y_ref, z_ref,
    number_of_strips, number_of_surfaces, number_of_vortices, surface_data, strip_forces)
    """

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

    x_ref: float = 0
    y_ref: float = 0
    z_ref: float = 0

    for line in lines:
        if line.endswith("| Xref, Yref, Zref\n"):
            string = line.split("|")
            value_string = string[0]
            values = value_string.split()
            x_ref = float(values[0])
            y_ref = float(values[1])
            z_ref = float(values[2])

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

    """print("CLff = {:.4f}\n".format(clff))
    print("CDff = {:.4f}\n".format(cdff))
    print("CYff = {:.4f}\n".format(cyff))
    print("Oswaldfactor = {:.4f}\n".format(oswaldfactor))

    print("Reference Wing area = {:.4f}\n".format(s_ref))
    print("Reference chord depth = {:.4f}\n".format(c_ref))
    print("Reference Wingspan = {:.4f}\n".format(b_ref))

    print("Reference x value = {:.4f}\n".format(x_ref))
    print("Reference y value = {:.4f}\n".format(y_ref))
    print("Reference z value = {:.4f}\n".format(z_ref))

    print("number of strips = {0}\n".format(number_of_strips))
    print("number of surfaces = {0}\n".format(number_of_surfaces))
    print("number of vortices = {0}\n".format(number_of_vortices))"""

    # ------strip_forces_avl file------

    file = open("strip_forces_avl")

    lines = file.readlines()

    # ---Surface Data---
    surface_data = np.array([])
    values: list = []
    hits = 0
    for line in lines:
        if line.endswith("| Surface #, # Chordwise, # Spanwise, First strip\n"):
            hits += 1
            string = line.split("|")
            value_string = string[0]
            values = value_string.split()
            if hits == 1:
                surface_data = np.array(values)
            else:
                arr = np.array(values)
                surface_data = np.vstack((surface_data, arr))

    """print(surface_data)
    print("Number of surface = {0}\n".format(surface_data[:, 0]))
    print("number of strips in chordwise direction = {0}\n".format(surface_data[:, 1]))
    print("number of strips in spanwise direction (important) = {0}\n".format(surface_data[:, 2]))
    print("surface begins with strip number = {0}\n".format(surface_data[:, 3]))"""

    strip_forces = np.array([])
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
        if strip_number == 0:
            strip_forces = np.array(values)
        else:
            arr = np.array(values)
            strip_forces = np.vstack((strip_forces, arr))

        """j = int(values[0])              # entspricht strip_number
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
"""
    file.close()

    result = (clff, cdff, cyff, oswaldfactor, s_ref, c_ref, b_ref, x_ref, y_ref, z_ref,
              number_of_strips, number_of_surfaces, number_of_vortices, surface_data, strip_forces)
    return result


# ---Test---


if __name__ == "__main__":
    plane = PlaneParser("testplane.toml").get("Plane")
    GeometryFile(plane).build_geometry_file(1)
    MassFile(plane).build_mass_file()
    AVL(plane).run_avl()

    AVL(plane).read_avl_output()
    print(plane.avl.outputs.surface_dictionary)




    # avl_file_path = plane.avl.inputs.avl_file
    # mass_file_path = plane.avl.inputs.mass_file

    # avl_file_path = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/runs/supra.avl"
    # mass_file_path = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/runs/supra.mass"
    # run_file_path = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/runs/supra.run"
    # total_forces_file = "total_forces_avl"
    # strip_forces_file = "strip_forces_avl"



# load C:/Users/Gregor/Documents/GitHub/mace/src/mace/aero/implementations/avl/geometry_file.avl

