import os
import signal
import subprocess
import time

import psutil
import logging


def _run_subprocess(cmd, timeout=10):
    try:
        subprocess.run(cmd, capture_output=True, timeout=timeout, shell=True, check=True)
    except subprocess.TimeoutExpired as err:
        logging.critical(f"Process timed out: {err}")
    except subprocess.CalledProcessError as err:
        logging.error(f"Process returned: {err}")


def run_subprocess(cmd, timeout=5):
    """
    runs a subprocess with an external command cmd.
    """
    # cmd = "C:/Users/Gregor/Documents/Modellflug/Software/XFOIL/xfoil.exe < input_file.in"
    try:
        with open(os.devnull, "w") as devnull:
            p = subprocess.Popen(
                cmd, shell=True, start_new_session=True, stdout=devnull
            )
            p.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        # print(p.pid)
        pass


def check_if_process_running(process_name):  # wird derzeit nicht benötigt.
    """
    Checks if there is any running process that contains the given name processName.
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


def find_process_id_by_name(process_name) -> list:
    """
    Get a list of all the PIDs of all the running processes whose name contains
    the given string processName.
    """

    list_of_process_objects = []

    # Iterate over all the running processes
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=["pid", "name", "create_time"])
            # Check if process name contains the given name string.
            if process_name.lower() in pinfo["name"].lower():
                list_of_process_objects.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return list_of_process_objects


def kill_subprocesses(list_of_process_ids):
    """
    kills all subprocesses with a mentioned PID in the list_of_process_ids.
    """
    if len(list_of_process_ids) > 0:
        print("Process exists / PID and other details are:")
        for elem in list_of_process_ids:
            process_id = elem["pid"]
            process_name = elem["name"]
            process_creation_time = time.strftime(
                "%Y-%m-%d-%H:%M:%S", time.localtime(elem["create_time"])
            )
            print((process_id, process_name, process_creation_time))
            os.kill(process_id, signal.SIGTERM)
    else:
        pass
        # print("No running process found with given text")


if __name__ == "__main__":
    _run_subprocess(["echo", "Hello"])
    _run_subprocess(["sleep", "6"])   
    _run_subprocess(["ech", "Hello"])    

