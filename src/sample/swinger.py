from ..domain.plane import *
from ..mass.calc import estimate_weight


def plane_setup():  # Edit to emulate swinger
    return FlugzeugBuilder() 


def main():
    flugzeug = plane_setup()
    flugzeug.weight = estimate_weight(flugzeug)
    print(f'The weight of the plane is approx. {flugzeug.weight} kg!')


if __name__ == "__main__":
    main()
