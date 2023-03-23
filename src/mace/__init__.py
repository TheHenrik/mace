"""
MACE is a project to evaluate model aircraft.
For Help view the Domcumentation.
"""


from mace.algo.calculate_plane import calculate_plane
from mace.domain.parser import XMLParser, TOMLParser
from mace.gui.gui import hello_world
from mace.mass.mass import get_mass_plane
from mace.mass.mass_estimation import estimate_mass_plane
from mace.setup.mace_setup import Project
