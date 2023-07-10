import numpy as np
import math
from mace.domain import params
from mace.domain.vehicle import Vehicle
from mace.aero.generalfunctions import GeneralFunctions
from mace.aero.generalfunctions import get_reynolds_number
from mace.aero.implementations.aero import Aerodynamics
from mace.aero.implementations.airfoil_analyses import Airfoil
from mace.aero.implementations.avl import geometry_and_mass_files_v2 as geometry_and_mass_files


class TakeOff:
    def __init__(self, plane: Vehicle):
        self.plane = plane
        self.mu = 0.125
        self.aero = Aerodynamics(self.plane)
        self.aero.XFOIL.print_re_warnings = False
        self.get_force = GeneralFunctions(self.plane).coefficient_to_lift_or_drag
        self.get_thrust = GeneralFunctions(self.plane).current_thrust
        self.flap_angle = 0.
        self.t_step = 0.2
        self.cl_safety_factor = 1.
        

    def get_friction(self, lift):
        return (self.plane.mass * params.Constants.g - lift) * self.mu
    def evaluate(self):
        S_REF = self.plane.reference_values.s_ref
        MASS = self.plane.mass
        DELTA_T = self.t_step
        G = params.Constants.g
        RHO = params.Constants.rho
        WingAirfoil = Airfoil(self.plane.wings["main_wing"].airfoil, 
                              flap_angle=self.flap_angle, 
                              x_hinge=(1-self.plane.wings["main_wing"].segments[0].flap_chord_ratio))
        WingAirfoil.print_re_warnings = False
        MAC = self.plane.wings["main_wing"].mean_aerodynamic_chord
        
        T = 0.
        S = 0.
        V = 0.
        while True:
            self.aero.evaluate(CL=None, V=V, FLAP=self.flap_angle, ALPHA=0.)
            
            CL = self.plane.aero_coeffs.lift_coeff.cl_tot
            CD = self.plane.aero_coeffs.drag_coeff.cd_tot
            
            LIFT = self.get_force(V, CL)
            DRAG = self.get_force(V, CD)
            FRICTION = self.get_friction(LIFT)
            THRUST = self.get_thrust(V)
            
            ACCELL = (THRUST - DRAG - FRICTION) / MASS
            T += DELTA_T
            V += ACCELL * DELTA_T
            S += 1/2 * ACCELL * DELTA_T ** 2 + V * DELTA_T
            
            REQ_CL = (MASS * G) / (1/2 * RHO * V ** 2 * S_REF)
            RE_AT_MAC = get_reynolds_number(V, MAC)

            CL_MAX = WingAirfoil.get_cl_max(RE_AT_MAC)

            if CL_MAX > self.cl_safety_factor * REQ_CL:
                break

        print("S: %.3f" % S)
        print("CL: %.3f" % REQ_CL)
        print("T_TO: %.3f" % T)

            
            
            
            
            
        
        
        
        