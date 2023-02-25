import os                       # operation system
import numpy as np
from mace.aero.implementations import runsubprocess as runsub


def avl_output(avl_file, mass_file, run_file, total_forces_file_name, strip_forces_file_name, maschine_readable_file=True):

    # --- Input file writer---

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
    if maschine_readable_file:
        input_file.write("MRF\n")                       # maschine readable file
    input_file.write("FT\n")                            # write total forces
    input_file.write("{0}\n".format(total_forces_file_name))
    input_file.write("FS\n")                            # write strip forces
    input_file.write("{0}\n".format(strip_forces_file_name))

    input_file.write("\n")

    input_file.write("QUIT\n")
    input_file.close()

    # ---Run AVL---

    cmd = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/avl.exe < input_file_avl.in"   # external command to run
    runsub.run_subprocess(cmd)

    # total_forces = np.loadtxt("forces_avl", skiprows=12)
    # total_forces = np.fromfile("total_forces_avl", sep=" ")
def read_avl_files():
    # string.split("/"," ")   # Bsp string splitten
    # data.strip() # String wird von Weißraumzeichen bereinigt, geht auch nur rechts oder links (lstrip, rstrip)
    file = open("total_forces_avl")
    lines = file.readlines()
    # print(file.read())
    # print(file.readline())
    # print(file.readlines())  # gibt Liste zurück
    for line in lines:
        if line.endswith("| Trefftz Plane: CLff, CDff, CYff, e\n"):
            print(line)
            string = line.split("|")
            # string.pop(1)
            # print(string)
            value_string = string[0]
            values = value_string.split()
            print(values)
            CLff = float(values[0])
            CDff = float(values[1])
            CYff = float(values[2])
            oswaldfactor = float(values[3])
            print("CLff = {:.4f}\n".format(CLff), "CDff = {:.4f}\n".format(CDff),
                  "CYff = {:.4f}\n".format(CYff), "Oswaldfactor = {:.4f}\n".format(oswaldfactor))
    for line in lines:
        if line.endswith("| Sref, Cref, Bref\n"):
            string = line.split("|")
            value_string = string[0]
            values = value_string.split()
            s_ref = float(values[0])
            c_ref = float(values[1])
            b_ref = float(values[2])
            print("Reference Wing area = {:.4f}\n".format(s_ref), "Reference chord depth = {:.4f}\n".format(c_ref),
                  "Reference Wingspan = {:.4f}\n".format(b_ref))
    number_of_strips: int = 0
    for line in lines:
        if line.endswith("| # strips\n"):
            string = line.split("|")
            value_string = string[0]
            values = value_string.split()
            number_of_strips = int(values[0])
            print("number of strips = {0}\n".format(number_of_strips))
    file.close()

    file = open("strip_forces_avl")
    lines = file.readlines()
    for strip_number in range(number_of_strips):
        print(strip_number+1)
        for line in lines:
            if strip_number+1 < 10:
                if line.startswith("   {0}".format(strip_number+1)):
                    print(line)
            elif strip_number+1 < 100:
                if line.startswith("  {0}".format(strip_number+1)):
                    print(line)
            elif strip_number+1 < 1000:
                if line.startswith(" {0}".format(strip_number+1)):
                    print(line)
            elif strip_number+1 < 10000:
                if line.startswith("{0}".format(strip_number+1)):
                    print(line)
            else:
                print("No valid data format")
    file.close()

# ---Test---


if __name__ == "__main__":
    avl_file = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/runs/supra.avl"
    mass_file = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/runs/supra.mass"
    run_file = "C:/Users/Gregor/Documents/Modellflug/Software/AVL/runs/supra.run"
    total_forces_file_name = "total_forces_avl"
    strip_forces_file_name = "strip_forces_avl"

    avl_output(avl_file, mass_file, run_file, total_forces_file_name, strip_forces_file_name,
               maschine_readable_file=True)
    read_avl_files()