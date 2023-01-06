from mace.domain.vector import Vector


class Cache_segments:
    def __init__(self, fun) -> None:
        self.fun = fun
        self.dictionary = dict()

    def __call__(self, *args) -> None:
        if args in self.dictionary:
            return self.dictionary[args]
        output = self.fun(*args)
        self.dictionary[args] = output
        return output
