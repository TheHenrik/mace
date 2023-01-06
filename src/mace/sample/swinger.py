import cProfile
import pstats
import time

from mace.domain.plane import FlugzeugParser
from mace.mass.calc import get_mass_aircraft


def main():
    flugzeug = FlugzeugParser("flugzeug.xml").build_plane()
    flugzeug.weight = get_mass_aircraft(flugzeug)
    print(f"The weight of the plane is approx. {flugzeug.weight} kg!")


def performance():
    repetitions = 1
    start = time.perf_counter()
    for _ in range(repetitions):
        main()
    end = time.perf_counter()
    return (end - start) / repetitions


def perf_report():
    with cProfile.Profile() as pr:
        main()
    stats = pstats.Stats(pr)
    stats.sort_stats(pstats.SortKey.TIME)
    stats.dump_stats(filename="need_profiling.prof")


if __name__ == "__main__":
    perf_report()
