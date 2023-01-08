from mace import FlugzeugParser, get_mass_aircraft


def main():
    flugzeug = FlugzeugParser("flugzeug.xml").build_plane()
    flugzeug.weight = get_mass_aircraft(flugzeug)
    print(f"The weight of the plane is approx. {flugzeug.weight} kg!")


if __name__ == "__main__":
    main()
