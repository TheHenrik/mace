import logging
import os  # operation system
from pathlib import Path

import numpy as np

from mace.aero.implementations import runsubprocess as runsub
from mace.aero.implementations.avl.geometry_and_mass_files import GeometryFile, MassFile

# from mace.domain.vehicle import Vehicle
from mace.domain.parser import PlaneParser
from mace.utils.mp import get_pid


class AVL:
    def __init__(self, plane):
        pid = get_pid()
        self.plane = plane
        tool_path = Path(__file__).resolve().parents[5]
        self.avl_path = Path(tool_path, "bin", "avl")
        self.total_forces_file_name = Path(
            tool_path, "temporary", f"total_forces{pid}.avl"
        )
        self.strip_forces_file_name = Path(
            tool_path, "temporary", f"strip_forces{pid}.avl"
        )
        self.input_file_name = Path(tool_path, "temporary", f"input_file_avl{pid}.in")
        self.geometry_file = Path(tool_path, "temporary", f"geometry_file{pid}.avl")
        self.stability_file_name = Path(
            tool_path, "temporary", f"stability_file{pid}.avl"
        )
        self.mass_file = Path(tool_path, "temporary", f"mass_file{pid}.mass")
        self.stability_input_file_name = Path(
            tool_path, "temporary", f"stability_input_file_avl{pid}.in"
        )

    def run_avl(
        self,
        avl_file=None,
        mass_file=None,
        angle_of_attack=None,
        lift_coefficient=None,
        flap_angle=None,
        run_case: int = 1,
        maschine_readable_file=True,
    ):
        """
        For run_case != 1 please check if runcase is available! At the time not possible! (maybe in future versions)
        """

        if os.path.exists(self.total_forces_file_name):
            os.remove(self.total_forces_file_name)
        if os.path.exists(self.strip_forces_file_name):
            os.remove(self.strip_forces_file_name)

        # --- Input file writer---
        with open(self.input_file_name, "w") as input_file:
            if avl_file:
                input_file.write(f"LOAD {avl_file}\n")
            else:
                input_file.write(f"LOAD {self.geometry_file}\n")
            if mass_file:
                input_file.write(f"MASS {mass_file}\n")
            else:
                input_file.write(f"MASS {self.mass_file}\n")
            # input_file.write(f'CASE {run_file}\n')
            input_file.write(f"OPER\n")
            if run_case != 1:  # select run_case
                input_file.write(f"{run_case}\n")
            if angle_of_attack is not None:  # set angle of attack in degrees
                input_file.write(f"A A {angle_of_attack}\n")
            if lift_coefficient is not None:  # set angle of attack with cl
                input_file.write(f"A C {lift_coefficient}\n")

            num_control_surfaces = 0
            if flap_angle is not None:  # set flap angle
                for wing in self.plane.wings.values():
                    for segment in wing.segments:
                        if segment.control:
                            num_control_surfaces += 1
                            input_file.write(
                                f"D{num_control_surfaces} D{num_control_surfaces} {flap_angle}\n"
                            )

            if num_control_surfaces != 0:
                num_control_surfaces += 1
                input_file.write(
                    f"D{num_control_surfaces} D{num_control_surfaces} {flap_angle}\n"
                )

            input_file.write(
                f"X\n"
            )  # execute runcase, XX executes all runcases but uses last runcase
            if maschine_readable_file:
                input_file.write(f"MRF\n")  # maschine readable file
            input_file.write(f"FT\n")  # write total forces
            input_file.write(f"{self.total_forces_file_name}\n")
            input_file.write(f"FS\n")  # write strip forces
            input_file.write(f"{self.strip_forces_file_name}\n")
            # input_file.write(f'ST\n')  # write strip forces
            # input_file.write(f'{self.stability_file_name}\n')
            input_file.write("\n")
            input_file.write("QUIT\n")

        # ---Run AVL---
        cmd = (
            str(self.avl_path) + " <" + str(self.input_file_name)
        )  # external command to run
        runsub._run_subprocess(cmd, timeout=15)
        # list_of_process_ids = runsub.find_process_id_by_name("avl")
        # runsub.kill_subprocesses(list_of_process_ids)

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
                values = np.fromstring(string[0], dtype=int, sep=" ")
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
                    if (
                        line.startswith("   {0}".format(strip_number + 1))
                        and "|" not in line
                    ):
                        values = np.fromstring(line, sep=" ")  # np.loadtxt(line)
                elif strip_number + 1 < 100:
                    if (
                        line.startswith("  {0}".format(strip_number + 1))
                        and "|" not in line
                    ):
                        values = np.fromstring(line, sep=" ")  # np.loadtxt(line)
                elif strip_number + 1 < 1000:
                    if (
                        line.startswith(" {0}".format(strip_number + 1))
                        and "|" not in line
                    ):
                        values = np.fromstring(line, sep=" ")  # np.loadtxt(line)
                elif strip_number + 1 < 10000:
                    if (
                        line.startswith("{0}".format(strip_number + 1))
                        and "|" not in line
                    ):
                        values = np.fromstring(line, sep=" ")  # np.loadtxt(line)
                else:
                    logging.error("No valid data format")
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

        for i in range(self.plane.avl.outputs.surface_data.shape[0]):
            first_strip = self.plane.avl.outputs.surface_data[i, -1]
            last_strip = first_strip + self.plane.avl.outputs.surface_data[i, -2] - 1
            strips = self.plane.avl.outputs.strip_forces[
                first_strip - 1 : last_strip, :
            ]
            first_and_last_strip = {
                "first_strip": first_strip,
                "last_strip": last_strip,
            }
            surface_dictionary_data = {
                "first_strip": first_strip,
                "last_strip": last_strip,
                "strips": strips,
            }
            self.plane.avl.outputs.first_and_last_strips[i + 1] = first_and_last_strip
            self.plane.avl.outputs.surface_dictionary[i + 1] = surface_dictionary_data

    def get_stability_data(
        self,
        design_lift_coefficient=0.6,
        design_flap_angle=0.0,
        machine_readable_file=True,
    ):
        if os.path.exists(self.stability_input_file_name):
            os.remove(self.stability_input_file_name)
        if os.path.exists(self.stability_file_name):
            os.remove(self.stability_file_name)

        with open(self.stability_input_file_name, "w") as input_file:
            input_file.write(f"LOAD {self.geometry_file}\n")
            input_file.write(f"MASS {self.mass_file}\n")
            input_file.write(f"OPER\n")
            input_file.write(f"A C {design_lift_coefficient}\n")
            num_control_surfaces = 0
            if design_flap_angle is not None:  # set flap angle
                for wing in self.plane.wings.values():
                    for segment in wing.segments:
                        if segment.control:
                            num_control_surfaces += 1
                            input_file.write(
                                f"D{num_control_surfaces} D{num_control_surfaces} {design_flap_angle}\n"
                            )
            if num_control_surfaces != 0:
                num_control_surfaces += 1
                input_file.write(
                    f"D{num_control_surfaces} D{num_control_surfaces} {design_flap_angle}\n"
                )
            input_file.write(
                f"X\n"
            )  # execute runcase, XX executes all runcases but uses last runcase
            if machine_readable_file:
                input_file.write(f"MRF\n")  # maschine readable file
            input_file.write(f"ST\n")
            input_file.write(f"{self.stability_file_name}\n")
            input_file.write("\n")
            input_file.write("QUIT\n")

        # ---Run AVL---
        cmd = (
            str(self.avl_path) + " <" + str(self.stability_input_file_name)
        )  # external command to run
        runsub._run_subprocess(cmd, timeout=15)
        # list_of_process_ids = runsub.find_process_id_by_name("avl")
        # runsub.kill_subprocesses(list_of_process_ids)

        with open(self.stability_file_name) as file:
            lines = file.readlines()

            CLa: float = 0
            Cma: float = 0
            Cnb: float = 0
            XNP: float = 0

            for line in lines:
                if line.endswith("| z' force CL  : CLa, CLb\n"):
                    string = line.split("|")
                    value_string = string[0]
                    values = value_string.split()
                    CLa = float(values[0])
                if line.endswith("| y  mom.  Cm  : Cma, Cmb\n"):
                    string = line.split("|")
                    value_string = string[0]
                    values = value_string.split()
                    Cma = float(values[0])
                if line.endswith("| z' mom.  Cn' : Cna, Cnb\n"):
                    string = line.split("|")
                    value_string = string[0]
                    values = value_string.split()
                    Cnb = float(values[1])
                if line.endswith("| Neutral point  Xnp\n"):
                    string = line.split("|")
                    value_string = string[0]
                    values = value_string.split()
                    XNP = float(values[0])

            SM = -Cma / CLa
            l_mu = self.plane.wings["main_wing"].mean_aerodynamic_chord
            ac = self.plane.wings["main_wing"].neutral_point[0]
            XCG = XNP - SM * self.plane.wings["main_wing"].mean_aerodynamic_chord
            percentMAC = (XCG - (ac - 0.25 * l_mu)) / l_mu

            logging.debug("\n")
            logging.debug("CLa: %.3f" % CLa)
            logging.debug("Cma: %.3f" % Cma)
            logging.debug("Cnb: %.3f" % Cnb)
            logging.debug("XNP: %.3f m" % XNP)
            logging.debug("SM: %.1f %%" % (100 * SM))
            logging.debug("l_mu: %.3f m" % l_mu)
            logging.debug("XCG: %.3f m" % XCG)
            logging.debug("percentMAC: %.1f %%" % (100 * percentMAC))
            logging.debug("\n")

            return CLa, Cma, Cnb, XNP, SM


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
    file.close()

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

    strip_forces = np.array([])
    for strip_number in range(number_of_strips):
        for line in lines:
            if strip_number + 1 < 10:
                if (
                    line.startswith("   {0}".format(strip_number + 1))
                    and "|" not in line
                ):
                    values = line.split()
            elif strip_number + 1 < 100:
                if (
                    line.startswith("  {0}".format(strip_number + 1))
                    and "|" not in line
                ):
                    values = line.split()
            elif strip_number + 1 < 1000:
                if line.startswith(" {0}".format(strip_number + 1)) and "|" not in line:
                    values = line.split()
            elif strip_number + 1 < 10000:
                if line.startswith("{0}".format(strip_number + 1)) and "|" not in line:
                    values = line.split()
            else:
                logging.error("No valid data format")
        if strip_number == 0:
            strip_forces = np.array(values)
        else:
            arr = np.array(values)
            strip_forces = np.vstack((strip_forces, arr))

    file.close()
    result = (
        clff,
        cdff,
        cyff,
        oswaldfactor,
        s_ref,
        c_ref,
        b_ref,
        x_ref,
        y_ref,
        z_ref,
        number_of_strips,
        number_of_surfaces,
        number_of_vortices,
        surface_data,
        strip_forces,
    )
    return result


# ---Test---


if __name__ == "__main__":
    plane = PlaneParser("testplane.toml").get("Plane")
    GeometryFile(plane).build_geometry_file(1)
    MassFile(plane).build_mass_file()
    AVL(plane).run_avl()

    AVL(plane).read_avl_output()
    logging.debug(plane.avl.outputs.surface_dictionary)
