def avlxfoil():
    pass


def ml():
    pass


class Aero:
    def __init__(self, avlxfoil: callable = avlxfoil, ml: callable=ml, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        self.avlxfoil = avlxfoil
        self.ml = ml