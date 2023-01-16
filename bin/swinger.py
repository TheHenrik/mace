from mace import FlugzeugParser, get_mass_plane
from mace.test import performance_report, performance_time


def main():
    flugzeug = FlugzeugParser("flugzeug.xml").build_plane()
    flugzeug = get_mass_plane(flugzeug)
    return flugzeug.mass


if __name__ == "__main__":
    print(f"The weight of the plane is approx. {main()} kg!")
    performance_time(10_000, main)
    performance_report(performance_time, 1_000, main, output=None)
