from mace.domain.vector import Vector


class Cache_segments:
    def __init__(self) -> None:
        self.dictionary = dict()

    def __call__(self, *args: tuple, **kwds: tuple) -> int:
        input = (args, kwds)
        if input in self.dictionary:
            return self.dictionary[input]


@Cache_segments
def add_vector(a: Vector, b: Vector, name: str):
    return a + b


def main():
    one = Vector(1, 1, 1)
    two = Vector(0, 0, 0)

    for _ in range(100):
        two = add_vector(one, two, "test")


if __name__ == "__main__":
    main()
