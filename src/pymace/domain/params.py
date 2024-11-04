from dataclasses import dataclass


@dataclass
class Constants:
    g: float = 9.812640
    rho: float = 1.14473
    ny: float = 1.64275e-5  # kinematische Viskosität Luft (18)


@dataclass()
class Units:
    l_unit: float = 1  # m (-> mm)   LengthUnit
    m_unit: float = 1  # kg        MassUnit
    t_unit: float = 1  # s         TimeUnit


@dataclass
class Material:
    name: str
    use: str
    count: int


class Parameters:
    constants = Constants
    units = Units
