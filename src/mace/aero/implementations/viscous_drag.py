
from mace.domain.parser import PlaneParser
from mace.aero.implementations.avl.geometry_and_mass_files import GeometryFile, MassFile
from mace.domain import params, Plane
from mace.aero.implementations.avl.athenavortexlattice import AVL
from pathlib import Path
import os
import numpy as np
from mace.aero.implementations.airfoil_analyses import Airfoil
from mace.aero.generalfunctions import get_reynolds_number


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

        S_ref = self.plane.avl.outputs.s_ref
        S_sum = 0.
        CD = 0.

        for surface in range(1, self.plane.avl.outputs.number_of_surfaces + 1, 2):
            strips = self.plane.avl.outputs.surface_dictionary[surface]["strips"][:, 0]
            for element in strips:
                # initialize strip values
                strip_values = self.plane.avl.outputs.surface_dictionary[surface]["strips"][int(element - 1), :]

                # get local reynolds
                c   = strip_values[4]
                cl  = strip_values[9]  # 9 und nicht 6 (cl_norm)
                re = get_reynolds_number(V, c)
                
                airfoil = Airfoil("ag19") # TODO: get airfoil from plane
                cd = airfoil.get_cd(re, cl)

                S = strip_values[5]

                CD += 2 * cd * S / S_ref
                S_sum += 2 * S

        plane.aero_coeffs.drag_coeff.cd_visc = CD
        plane.aero_coeffs.drag_coeff.cd_tot = CD + plane.aero_coeffs.drag_coeff.cd_ind

        return CD




        
if __name__ == "__main__":
    # Initialize aircraft
    plane = PlaneParser("aachen.toml").get("Plane")
    GeometryFile(plane).build_geometry_file(1)
    MassFile(plane).build_mass_file()

    # Define Analysis
    V = 10.
    W = plane.mass[0]
    CL = 0.5

    # Run AVL
    inviscid_analysis = AVL(plane)
    inviscid_analysis.run_avl(lift_coefficient=CL)
    inviscid_analysis.read_avl_output()

    # Run Xfoil
    viscous_analysis = ViscousDrag(plane)

    CDv = viscous_analysis.evaluate(V)
    CDi = plane.aero_coeffs.drag_coeff.cd_ind
    CD = CDv + CDi
    L_D = CL / CD

    print("V:  ", V)
    print("CL:  %.4f" % CL)
    print("CDv: %.4f" % CDv)
    print("CDi: %.4f" % CDi)
    print("L/D: %.4f" % L_D)