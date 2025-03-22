from pymace.new.domain import Plane

def avlxfoil(plane: Plane) -> None:

    pass


def ml(plane: Plane) -> None:
    pass


class Aero:
    def __init__(self, avlxfoil: callable = avlxfoil, ml: callable=ml, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.avlxfoil = avlxfoil
        self.ml = ml

    def __call__(self, plane: Plane, *args, methode="ml", **kwargs):
        ret_val = self.__dict__[methode](plane, *args, **kwargs)
        return ret_val