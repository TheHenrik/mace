import logging
from multiprocessing import Pool, current_process
from time import sleep
from typing import Callable, Iterable


def get_pid():
    """
    Returns the process ID (PID) of the current process if it is not the main process.

    If the current process is the main process, an empty string is returned.
    Otherwise, the PID of the current process is returned as a string prefixed with an underscore.

    Returns:
        str: An empty string if the current process is the main process, otherwise the PID of the current process prefixed with an underscore.
    """
    if current_process().name == "MainProcess":
        return ""
    else:
        return "_" + str(current_process().pid)


def mp(func: Callable, params: Iterable, processes: int | None = None):
    with Pool(processes=processes) as p:
        return p.map(func, params)


# Just for testing purposes

def _fn(x: int) -> int:
    if current_process().name == "MainProcess":
        pid = ""
    else:
        pid = current_process().pid
    logging.debug(pid)
    sleep(1)
    return x * x


def _main():
    logging.debug(_fn(1))
    logging.debug(mp(_fn, range(6)))


if __name__ == "__main__":
    _main()
