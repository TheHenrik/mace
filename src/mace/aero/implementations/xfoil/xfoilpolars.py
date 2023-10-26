import os  # operation system
from pathlib import Path

import numpy as np

from mace.aero.implementations import runsubprocess as runsub

# ---Inputs---


def get_xfoil_polar(
    airfoil_name,
    reynoldsnumber,
    *,
    alfa=None,
    alfa_start=None,
    alfa_end=None,
    cl=None,
    cl_start=None,
    cl_end=None,
    alfa_step: float = 0.5,
    cl_step: float = 0.05,
    n_iter=100,
    mach: float = 0,
    n_crit: float = 11,
    x_transition_top=100,
    x_transition_bottom=100,
    flap_angle: float = 0,
    x_hinge: float = 0.75,
    z_hinge: float = 0.0,
):
    """
    returns a numpy array with all polar data:
        each row contains:
        alpha, CL, CD, CDp, CM, Top_Xtr, Bot_Xtr

    inputs:
    airfoil_name, alfa_start, alfa_end, alfa_step, reynoldsnumber, n_iter

    it is recommended to have alfa_start = 0 for better convergence.

    ----------------
    Mach: float between 0 and Mach_crit (<<1), only use for Mach > 0.3
    ----------------

          situation            Ncrit
      -----------------        -----
      sailplane                12-14
      motorglider              11-13
      clean wind tunnel        10-12
      average wind tunnel        9     <=  standard "e^9 method"
      dirty wind tunnel         4-8

    ------------------
    Forced transition:

    x_transition_top: int between 0 and 100%        (from leading edge to trailing edge)
    x_transition_bottom: int between 0 and 100%     (from leading edge to trailing edge)
    """
    # ---Inputfile writer---

    tool_path = Path(__file__).resolve().parents[5]
    polar_file_path = os.path.join(tool_path, "temporary/polar_file.txt")
    input_file_path = os.path.join(tool_path, "temporary/input_file_xfoil.in")
    xfoil_path = os.path.join(tool_path, "Xfoil/bin/xfoil")

    if os.path.exists(polar_file_path):
        os.remove(polar_file_path)

    with open(input_file_path, "w") as input_file:
        input_file.write(f"LOAD {airfoil_name}\n")

        # Set flaps
        if flap_angle != 0:
            input_file.write(f"NORM\n")
            input_file.write(f"GDES\n")
            input_file.write(f"FLAP\n")
            input_file.write(f"{round(x_hinge, 3)}\n")
            input_file.write(f"{round(z_hinge, 3)}\n")
            input_file.write(f"{round(flap_angle, 3)}\n")
            input_file.write(f"X\n")
            input_file.write(f"\n")

        #        input_file.write(f'PANE\n')
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
                    f"XTR {x_transition_top/100} {x_transition_bottom/100}\n"
                )
            input_file.write(f"\n")
        input_file.write(f"PACC\n")
        input_file.write(polar_file_path + "\n\n")
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
        else:
            print(f"wrong XFOIL inputs")  # Error

        input_file.write(f"\n\n")
        input_file.write(f"quit \n")

    # ---Run XFOIL---
    cmd = xfoil_path + " <" + input_file_path  # external command to run
    runsub.run_subprocess(cmd)

    polar_data = np.loadtxt(polar_file_path, skiprows=12)

    list_of_process_ids = runsub.find_process_id_by_name("xfoil")
    runsub.kill_subprocesses(list_of_process_ids)

    return polar_data  #   alpha    CL        CD       CDp       CM     Top_Xtr  Bot_Xtr


# ---Test---

if __name__ == "__main__":
    tool_path = Path(__file__).resolve().parents[5]
    airfoil_name = os.path.join(tool_path, "data/airfoils/ag19.dat")
    alfa_start = 0
    alfa_end = 20
    alfa_step = 0.25
    reynolds = 200000
    n_iter = 80  # wenn keine Konvergenz reduzieren, Ergebnisse scheinen annähernd gleich zu bleiben

    polar_daten = get_xfoil_polar(airfoil_name, reynolds, cl=0.5)
    print(polar_daten)
