import cProfile
import pstats
import time


def performance_time(repetitions, func, *args, **kwargs):
    start = time.perf_counter()
    for _ in range(repetitions):
        func(*args, **kwargs)
    end = time.perf_counter()
    return (end - start) / repetitions


def performance_report(func, *args, **kwargs):
    with cProfile.Profile() as pr:
        func(*args, **kwargs)
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats(filename="need_profiling.prof")
