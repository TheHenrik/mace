from mace import ProjectSetup, calculate_plane
from mace.test import getsize, performance_report, performance_time


def main():
    project = ProjectSetup(planes_location=["flugzeug.xml"])
    for plane in project.planes:
        plane = calculate_plane(plane)
        print(f"The weight of the plane is approx. {plane.mass} kg!")

    plane = project.planes[0]
    print(f"Size on Disk of Plane: {getsize(plane)}")
    performance_time(10_000, calculate_plane, plane)
    performance_report(performance_time, 1_000, calculate_plane, plane, output=None)


if __name__ == "__main__":
    main()
