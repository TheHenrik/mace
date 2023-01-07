import mace.domain
from mace.domain.plane import FlugzeugParser, Rumpf
from mace.domain.vector import Vector, Vectorcalc
from mace.gui.gui import hello_world
from mace.mass.calc import get_mass_aircraft


def gui():
    """Entry point for 'mace-gui'"""
    hello_world()
