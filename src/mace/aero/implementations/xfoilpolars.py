import os                       # operation system
import numpy as np
from mace.aero.implementations import runsubprocess as runsub


# ---Inputs---


def get_xfoil_polar(airfoil_name, alfa_start, alfa_end, alfa_step, reynoldsnumber, n_iter,
                    mach: float=0, n_crit: float=9, x_transition_top=100, x_transition_bottom=100):
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

    if os.path.exists("polar_file.txt"):
        os.remove("polar_file.txt")

    input_file = open("input_file.in", 'w')
    input_file.write("LOAD {0}\n".format(airfoil_name))
    input_file.write("NORM\n")
    input_file.write("PANE\n")
    input_file.write("OPER\n")
    input_file.write("Visc {0}\n".format(reynoldsnumber))
    if mach != 0:
        input_file.write("Mach {0}\n".format(mach))
    if n_crit != 9 or x_transition_top != 100 or x_transition_bottom != 100:
        input_file.write("VPAR\n")
        if n_crit != 9:
            input_file.write("N {0}\n".format(n_crit))
        if x_transition_top != 100 or x_transition_bottom != 100:
            input_file.write("XTR {0} {1}\n".format(x_transition_top/100, x_transition_bottom/100))
        input_file.write("\n")
    input_file.write("PACC\n")
    input_file.write("polar_file.txt\n\n")
    input_file.write("ITER {0}\n".format(n_iter))
    input_file.write("ASeq {0} {1} {2}\n".format(alfa_start, alfa_end, alfa_step))

    input_file.write("\n\n")
    input_file.write("quit \n")
    input_file.close()              # mit context manager nicht notwendig

    # ---Run XFOIL---

    cmd = "C:/Users/Gregor/Documents/Modellflug/Software/XFOIL/xfoil.exe < input_file.in"   # external command to run
    runsub.run_subprocess(cmd)

    polar_data = np.loadtxt("polar_file.txt", skiprows=12)      # max_rows ist Parameter für Anzahl Zeilen

    # Find all PIDs of all the running instances of process that contains "xfoil" in its name
    list_of_process_ids = runsub.find_process_id_by_name("xfoil")

    runsub.kill_subprocesses(list_of_process_ids)
    return polar_data


# ---Test---

if __name__ == "__main__":

    airfoil_name = "C:/Users/Gregor/Documents/GitHub/mace/data/airfoils/n0012.dat"
    alfa_start = 0
    alfa_end = 20
    alfa_step = 0.25
    re = 200000
    n_iter = 80            # wenn keine Konvergenz reduzieren, Ergebnisse scheinen annähernd gleich zu bleiben

    polar_daten = get_xfoil_polar(airfoil_name, alfa_start, alfa_end, alfa_step, re, n_iter,
                                  n_crit=5.794, x_transition_top=54, mach=0.6)
    print(polar_daten)
