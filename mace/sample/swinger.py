from ..mass.calc import estimate_weight
from ..domain.plane import FlugzeugParser

def main():
    flugzeug = FlugzeugParser('flugzeug.xml').build_plane()
    print(flugzeug)
    flugzeug.weight = estimate_weight(flugzeug)
    print(f'The weight of the plane is approx. {flugzeug.weight} kg!')


if __name__ == "__main__":
    main()
