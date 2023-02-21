import os               # operation system
import signal
import subprocess
import time
import numpy as np
import psutil


# ---Inputs---


def get_xfoil_polar(airfoil_name, alfa_start, alfa_end, alfa_step, reynoldsnumber, n_iter):

    # ---Inputfile writer---

    if os.path.exists("polar_file.txt"):
        os.remove("polar_file.txt")

    input_file = open("input_file.in", 'w')
    input_file.write("LOAD {0}\n".format(airfoil_name))
    # input_file.write(airfoil_name + "\n")
    input_file.write("NORM\n")
    input_file.write("PANE\n")
    input_file.write("OPER\n")
    input_file.write("Visc {0}\n".format(reynoldsnumber))
    input_file.write("PACC\n")
    input_file.write("polar_file.txt\n\n")
    input_file.write("ITER {0}\n".format(n_iter))
    input_file.write("ASeq {0} {1} {2}\n".format(alfa_start, alfa_end, alfa_step))

    input_file.write("\n\n")
    input_file.write("quit \n")
    input_file.close()

    # ---Run XFOIL---

    # subprocess.run("C:/Users/Gregor/Documents/Modellflug/Software/XFOIL/xfoil.exe < input_file.in", shell=True)
    cmd = "C:/Users/Gregor/Documents/Modellflug/Software/XFOIL/xfoil.exe < input_file.in"   # external command to run

    try:
        p = subprocess.Popen(cmd, shell=True, start_new_session=True)
        p.wait(timeout=5)
    except subprocess.TimeoutExpired:
        # print(p.pid)
        pass

    polar_data = np.loadtxt("polar_file.txt", skiprows=12)

    def check_if_process_running(process_name):
        """
        Check if there is any running process that contains the given name processName.
        """
        # Iterate over all the running processes
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if process_name.lower() in proc.name().lower():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def find_process_id_by_name(process_name):
        """
        Get a list of all the PIDs of all the running processes whose name contains
        the given string processName.
        """

        list_of_process_objects = []

        # Iterate over all the running processes
        for proc in psutil.process_iter():
            try:
                pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time'])
                # Check if process name contains the given name string.
                if process_name.lower() in pinfo['name'].lower():
                    list_of_process_objects.append(pinfo)
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return list_of_process_objects

    # Find all PIDs of all the running instances of process that contains "xfoil" in it's name
    list_of_process_ids = find_process_id_by_name("xfoil")

    if len(list_of_process_ids) > 0:
        print("Process exists / PID and other details are:")
        for elem in list_of_process_ids:
            process_id = elem["pid"]
            process_name = elem["name"]
            process_creation_time = time.strftime("%Y-%m-%d-%H:%M:%S", time.localtime(elem["create_time"]))
            print((process_id, process_name, process_creation_time))
            os.kill(process_id, signal.SIGTERM)     # noch abwarten, bis berechnung fertig
    else:
        print("No running process found with given text")
    return polar_data


# ---Test---

if __name__ == "__main__":

    airfoil_name = "C:/Users/Gregor/Documents/GitHub/mace/data/airfoils/n0012.dat"
    alfa_start = 0
    alfa_end = 20
    alfa_step = 0.25
    re = 200000
    n_iter = 100            # wenn keine Konvergenz reduzieren

    polar_daten = get_xfoil_polar(airfoil_name, alfa_start, alfa_end, alfa_step, re, n_iter)
    print(polar_daten)