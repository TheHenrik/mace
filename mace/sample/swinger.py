from mace.domain.plane import FlugzeugParser
from mace.mass.calc import get_mass


def main():
    flugzeug = FlugzeugParser('flugzeug.xml').build_plane()
    print(flugzeug)
    flugzeug.weight = get_mass(flugzeug)
    print(f'The weight of the plane is approx. {flugzeug.weight} kg!')


if __name__ == "__main__":
    main()
