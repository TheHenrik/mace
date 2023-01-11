from mace import FlugzeugParser, get_mass_aircraft
from mace.test import performance_time, performance_report


def main():
    flugzeug = FlugzeugParser("flugzeug.xml").build_plane()
    flugzeug.weight = get_mass_aircraft(flugzeug)
    #print(f"The weight of the plane is approx. {flugzeug.weight} kg!")


if __name__ == "__main__":
    print(performance_time(1_000, main))
    performance_report(performance_time,1_000, main)
