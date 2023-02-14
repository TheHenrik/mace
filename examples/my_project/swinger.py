from mace import PlaneParser, get_mass_plane, mace_setup
from mace.test import performance_report, performance_time, getsize
from mace.setup import populate_airfoils


def main():
    populate_airfoils()
    plane = calc()
    print(f"The weight of the plane is approx. {plane.mass} kg!")
    print(f"Size on Disk of Plane: {getsize(plane)}")
    performance_time(10_000, calc)
    performance_report(performance_time, 1_000, calc, output=None)
    

def calc():
    plane = PlaneParser("flugzeug.xml").build_plane()
    plane = get_mass_plane(plane)
    return plane


def _main():
    #read from files
    project = mace_setup()
    for plane in project:
        plane = calculate(plane)
        #eval
    #print best?

if __name__ == "__main__":
    main()
