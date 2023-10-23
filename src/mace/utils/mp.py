from multiprocessing import Pool, current_process
from typing import Iterable, Callable
from time import sleep

def mp(func: Callable, params: Iterable, processes: int | None = None):
    with Pool(processes=processes) as p:
         return p.map(func, params)
    

def fn(x: int) -> int:
    if current_process().name == "MainProcess":
        pid = ""
    else:
        pid = current_process().pid
    print(pid)
    sleep(1)
    return x * x


def main():
     print(fn(1))
     print(mp(fn, range(6)))


if __name__ == "__main__":
    main()
           