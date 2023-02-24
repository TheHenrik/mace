import os                       # operation system
import numpy as np
from mace.aero.implementations import runsubprocess as runsub


# def avl_output(maschine_readable_file=True):

# --- Input file writer---

avl_file = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/runs/supra.avl"
mass_file = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/runs/supra.mass"
run_file = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/runs/supra.run"
total_forces_file_name = "total_forces_avl"
strip_forces_file_name = "strip_forces_avl"

# "C:\Users\Gregor\Documents\GitHub\mace\src\mace\aero\implementations\forces_avl"

if os.path.exists("total_forces_avl"):
    os.remove("total_forces_avl")
if os.path.exists("strip_forces_avl"):
    os.remove("strip_forces_avl")

input_file = open("input_file_avl.in", 'w')
input_file.write("LOAD {0}\n".format(avl_file))
input_file.write("MASS {0}\n".format(mass_file))
input_file.write("CASE {0}\n".format(run_file))
input_file.write("OPER\n")
input_file.write("XX\n")                            # execute all runcases
# input_file.write("MRF\n")                           # maschine readable file
input_file.write("FT\n")                            # write total forces
input_file.write("{0}\n".format(total_forces_file_name))
input_file.write("FS\n")                            # write strip forces
input_file.write("{0}\n".format(strip_forces_file_name))

input_file.write("\n")

input_file.write("QUIT\n")
input_file.close()

cmd = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/avl.exe < input_file_avl.in"   # external command to run
runsub.run_subprocess(cmd)

#total_forces = np.loadtxt("forces_avl", skiprows=12)
