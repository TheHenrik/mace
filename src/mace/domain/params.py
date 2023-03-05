from dataclasses import dataclass


@dataclass
class Constants:
    g: float = 9.81
    rho: float = 1.225
    ny: float = 18*10**(-6)   # kinematische Viskosität Luft


@dataclass()
class Units():
    l_unit: float = 0.001   # m -> mm   LengthUnit
    m_unit: float = 1       # kg        MassUnit
    t_unit: float = 1       # s         TimeUnit


@dataclass
class Material:
    name: str
    use: str
    count: int


class Parameters:
    constants = Constants
    units = Units
