from ..domain.plane import FlugzeugBuilder
from ..mass.calc import estimate_weight

def main():
    flugzeug = FlugzeugBuilder()
    flugzeug.weight = estimate_weight(flugzeug)
    print(f'The weight of the plane is approx. {flugzeug.weight} kg!')


if __name__ == "__main__":
    main()
