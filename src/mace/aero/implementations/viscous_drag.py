import numpy.ma

from mace.aero.implementations.avl import athenavortexlattice
from mace.aero import generalfunctions
from mace.aero.implementations.xfoil import xfoilpolars
from mace.domain import params, Plane
from mace.aero.implementations.avl.athenavortexlattice import AVL
import numpy as np
import math
from mace.domain.parser import PlaneParser
from mace.aero.implementations.avl.geometry_and_mass_files import GeometryFile, MassFile
from pathlib import Path
import os


class ViscousDrag:
    def __init__(self, plane: Plane):
        self.plane = plane
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho
        AVL(self.plane).read_avl_output()
        
    def mach_strip_to_surface(self, strip):
        """
        returns surface_index, equals (number_of_surface - 1)
        """
        first_strip_of_surface = self.plane.avl.outputs.surface_data[:, 3]
        for surface_index in range(self.plane.avl.outputs.number_of_surfaces):
            if first_strip_of_surface[surface_index] < strip:
                continue
            else:
                return surface_index

    def evaluate(self, V):
        for surface in range(1, self.plane.avl.outputs.number_of_surfaces + 1):
            print("Surface: ", surface)
            strips = self.plane.avl.outputs.surface_dictionary[surface]["strips"][:, 0]
            print(strips)
        
if __name__ == "__main__":
    # Initialize aircraft
    plane = PlaneParser("aachen.toml").get("Plane")
    GeometryFile(plane).build_geometry_file(1)
    MassFile(plane).build_mass_file()

    # Define Analysis
    CL = 0.8
    V = 10

    # Run AVL
    inviscid_analysis = AVL(plane)
    inviscid_analysis.run_avl()
    inviscid_analysis.read_avl_output()

    # Run Xfoil
    viscous_analysis = ViscousDrag(plane)
    viscous_analysis.evaluate(V)