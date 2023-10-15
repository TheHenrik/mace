from mace import Project


def main():
    project = Project(planes_location=["plane.toml"])
    project.calculate(verbose=True)
    project.evaluate()
    project.benchmark()


if __name__ == "__main__":
    main()
