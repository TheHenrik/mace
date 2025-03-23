import cProfile
import logging
import pstats
import time


def performance_time(repetitions: int, func: callable, *args, output: str = None, **kwargs) -> float|None:
    """
    Measures the performance time of a given function by executing it a specified number of times.

    Args:
        repetitions (int): The number of times to execute the function.
        func (callable): The function to be executed.
        *args: Variable length argument list to pass to the function.
        output (str, optional): If set to "toConsole", the performance results will be logged to the console. Defaults to None.
        **kwargs: Arbitrary keyword arguments to pass to the function.

    Returns:
        float: The average time per execution in seconds if output is not "toConsole".
    """
    start = time.perf_counter()
    for _ in range(repetitions):
        func(*args, **kwargs)
    end = time.perf_counter()
    if output == "toConsole":
        took = end - start
        logging.debug(f"took {took:.3f} s, ")
        logging.debug(f"{repetitions/took:.3f} it/s, ")
        logging.debug(f"{took/repetitions*1e3:.3f} ms/it")
        return
    return (end - start) / repetitions


def performance_report(func, *args, save_path = "need_profiling.prof", **kwargs):
    """
    Profiles the performance of a given function and saves the profiling report to a file.

    Args:
        func (callable): The function to be profiled.
        *args: Variable length argument list to be passed to the function.
        **kwargs: Arbitrary keyword arguments to be passed to the function.

    Returns:
        None

    Side Effects:
        Creates a profiling report file named 'need_profiling.prof' in the current directory.
    """
    with cProfile.Profile() as pr:
        func(*args, **kwargs)
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats(filename=save_path)
