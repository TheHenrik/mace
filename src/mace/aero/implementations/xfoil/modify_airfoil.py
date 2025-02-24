from mace.utils.file_path import root
from mace.aero.implementations import runsubprocess as runsub
from pathlib import Path
from mace.utils.mp import get_pid
import sys
import os
import numpy as np

def modify_airfoil(airfoil_name,
                   thick_new = None,
                   x_thick_max_new = None,
                   camb_new = None,
                   x_camb_max_new = None,
                   LE_rad_new = None,
                   LE_bending_x = None,
                   TE_gap_new = None,
                   alpha_start = 0,
                   alpha_end = 10,
                   reynoldsnumber = 1e6,
                   mach = 0,
                   n_crit = 9,
                   x_transition_top = 100,
                   x_transition_bottom = 100,
                   n_iter = 100,
                   alfa = None,
                   alfa_start = None,
                   cl = None,
                   cl_start = None,
                   cl_end = None,
                   ):
    """
    This Method modifies the airfoil shape using the XFOIL geometry commands.
    """

    tool_path = root()
    input_file_path = Path(tool_path, "temporary", f"input_file_xfoil{get_pid()}.in")
    polar_file_path = Path(tool_path, "temporary", "polar_file.txt")
    xfoil_path = Path(tool_path, "bin", sys.platform, "xfoil")

    airfoil_path = os.path.join(
        tool_path, "data", "airfoils", airfoil_name + ".dat"
    )
    airfoil_path_out = os.path.join(
        tool_path, "data", "airfoils", airfoil_name + "_out.dat"
    )

    with open(input_file_path, "w") as input_file:
        input_file.write(f"LOAD {airfoil_path}\n")
        input_file.write(f"NORM\n")
        input_file.write(f"GDES\n")
        input_file.write(f"TSET\n")
        input_file.write(f"{round(thick_new, 3)}\n")
        input_file.write(f"{round(camb_new, 3)}\n")
        input_file.write(f"HIGH\n")
        input_file.write(f"{round(x_thick_max_new, 3)}\n")
        input_file.write(f"{round(x_camb_max_new, 3)}\n")
        input_file.write(f"LERA\n")
        input_file.write(f"{round(LE_rad_new, 3)}\n")
        input_file.write(f"{round(x_camb_max_new, 3)}\n")
        input_file.write(f"X\n")
        input_file.write(f"INPL\n")
        input_file.write(f"\n")
        input_file.write(f"SAVE {airfoil_path_out}\n")
        input_file.write(f"OPER\n")
        input_file.write(f"Visc {reynoldsnumber}\n")
        if mach != 0:
            input_file.write(f"Mach {mach}\n")
        if n_crit != 9 or x_transition_top != 100 or x_transition_bottom != 100:
            input_file.write(f"VPAR\n")
            if n_crit != 9:
                input_file.write(f"N {n_crit}\n")
            if x_transition_top != 100 or x_transition_bottom != 100:
                input_file.write(
                    f"XTR {x_transition_top / 100} {x_transition_bottom / 100}\n"
                )
            input_file.write(f"\n")
        input_file.write(f"PACC\n")
        input_file.write(str(polar_file_path) + "\n\n")
        # input_file.write(f'polar_file.txt\n\n')
        input_file.write(f"ITER {n_iter}\n")
        if alfa is not None:
            input_file.write(f"Alfa {alfa}\n")
        elif alfa_start is not None and alfa_end is not None:
            input_file.write(f"ASeq {alfa_start} {alfa_end} {alfa_step}\n")
        elif cl:
            input_file.write(f"Cl {cl}\n")
        elif cl_start is not None and cl_end is not None:
            input_file.write(f"CSeq {cl_start} {cl_end} {cl_step}\n")

        input_file.write(f"\n\n")
        input_file.write(f"quit \n")

    # ---Run XFOIL---
    cmd = str(xfoil_path) + " <" + str(input_file_path)  # external command to run
    runsub.run_subprocess(cmd)

    #polar_data = np.loadtxt(polar_file_path, skiprows=12)

    # list_of_process_ids = runsub.find_process_id_by_name("xfoil")
    # runsub.kill_subprocesses(list_of_process_ids)


if __name__ == '__main__':
    modify_airfoil("ag40", thick_new=0.08, camb_new=0.03, x_thick_max_new=0.3, x_camb_max_new=0.3, LE_rad_new=1.5)


