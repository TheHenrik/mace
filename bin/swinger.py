from mace import FlugzeugParser, get_mass_aircraft
from mace.test import performance_report, performance_time


def main():
    flugzeug = FlugzeugParser("flugzeug.xml").build_plane()
    flugzeug.weight = get_mass_aircraft(flugzeug)
    return flugzeug.weight


if __name__ == "__main__":
    print(f"The weight of the plane is approx. {main()} kg!")
    performance_time(10_000, main)
    performance_report(performance_time,1_000, main, output = None)
