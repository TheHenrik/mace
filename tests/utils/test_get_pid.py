import re
from multiprocessing import Pool
from pymace.utils.mp import get_pid

def test_get_pid_main_process():
    # In the main process, get_pid() should return an empty string.
    assert get_pid() == ""

def _call_get_pid(_):
    return get_pid()

def test_get_pid_subprocess():
    # In a subprocess, get_pid() should return a string starting with an underscore
    # followed by digits.
    with Pool(1) as pool:
        results = pool.map(_call_get_pid, [0])
    pid = results[0]
    assert isinstance(pid, str)
    assert pid.startswith("_")
    assert re.fullmatch(r"_\d+", pid)