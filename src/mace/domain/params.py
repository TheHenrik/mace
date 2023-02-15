from dataclasses import dataclass


@dataclass
class Constants:
    g: float = 9.81
    rho: float = 1.225


@dataclass
class Material:
    name: str
    use: str
    count: int


class Parameter:
    constants = Constants
