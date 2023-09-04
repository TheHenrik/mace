import math

import numpy as np
from mace.domain import params
from mace.domain.vehicle import Vehicle
from mace.aero.implementations.aero import Aerodynamics
from mace.aero.implementations.airfoil_analyses import Airfoil
from mace.aero.generalfunctions import GeneralFunctions
import mace.aero.generalfunctions as functions
from scipy.optimize import minimize_scalar
import time

class Climb:
    def __init__(self, plane: Vehicle):
        self.plane = plane
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho

        self.cl_start = 0.1
        self.cl_end = 1.1
        self.cl_step = 0.05
        self.v_tolerance = 0.1
        self.it_max = 20
        
        self.flap_angle = 0.
        self.optimize_flap_angle = True

    def v_climb(self, current_thrust, cl, cd) -> (float, float):
        """
        Returns the velocity (on the flightpath) of a plane.
        (It is a bit more complex compared to horizontal flight.)
        It is !not! the vertical velocity. It is the velocity during climb/descent.
        It depends on the current thrust and aerodynamic coefficients.

        It returns as a tupel (v, v^2).
        """

        a = (self.rho/2) * self.s_ref * (cd**2 + cl**2)
        b = -2 * current_thrust * cd
        c = (current_thrust**2 - (self.mass * self.g)**2) / ((self.rho/2) * self.s_ref)

        v_square = (-b + (b**2 - 4 * a * c)**0.5) / (2 * a)
        v = v_square**0.5

        return v 

    def sin_gamma(self, current_thrust, v_square, cd):         # v_square = V^2
        """
        Returns the sinus of the climbing/descent angle gamma.
        It depends on the current thrust, v_square and the aerodynamic drag coefficient.
        """
        sin = (current_thrust - (self.rho/2) * v_square * self.s_ref * cd) / (self.mass * self.g)
        return sin

    def cos_gamma(self, v_square, cl):         # v_square = V^2
        """
        Returns the cosinus of the climbing/descent angle gamma.
        It depends on v_square and the aerodynamic lift coefficient.
        """
        cos = ((self.rho/2) * v_square * self.s_ref * cl) / (self.mass * self.g)
        return cos

    def gamma(self, sin, cos):                # zu Vergleichszwecken doppelte Berechnung
        """
        Returns the climbing/descent angle gamma in degrees if sin and cos are given.
        """
        gamma = math.degrees(np.arcsin(sin))
        # if cos >= 1:
        #     gamma = 0
        # else:
        #     gamma2 = math.degrees(np.arccos(cos))
        return gamma      # wird als Tupel übergeben

    def v_vertical(self, velocity, sin_gam):                # sin_gamma bereits vorher berechnen, ist übersichtlicher
        """
        Returns vertical velocity if velocity on flightpath and sinus(gamma) is given.
        """
        v_vert = velocity * sin_gam
        return v_vert


    def evaluate(self, CL):
        v_tolerance = self.v_tolerance
        it_max = self.it_max
        Aero = Aerodynamics(self.plane)
        thrust = GeneralFunctions(self.plane).current_thrust
        V = ((2 * self.mass * self.g) / (CL * self.rho * self.s_ref)) ** 0.5
        not_in_tolerance = True
        it = 0

        while not_in_tolerance and it < it_max:
            if self.optimize_flap_angle:
                c_length = self.plane.reference_values.c_ref
                re = functions.get_reynolds_number(V, c_length)
                airfoil = Airfoil(self.plane.wings['main_wing'].airfoil)
                self.flap_angle = airfoil.check_for_best_flap_setting(re, CL)

            Aero.evaluate(V=V, CL=CL, FLAP=self.flap_angle)
            CD = self.plane.aero_coeffs.drag_coeff.cd_tot
            T = thrust(V)
            V2 = self.v_climb(T, CL, CD)
            it += 1
            not_in_tolerance = abs(V - V2) >= v_tolerance
            V = V2

        sin = self.sin_gamma(T, V**2, CD)
        V_vertical = self.v_vertical(V, sin)
        return - V_vertical
        
    def get_gamma_max(self):
        # gamma maximal
        climb_data = self.plane.flight_conditions.climb.results.climb_data
        if climb_data is None:
            self.evaluate()
            climb_data = self.plane.flight_conditions.climb.results.climb_data
        
        gamma_max = np.max(self.plane.flight_conditions.climb.results.climb_data[:, 3])  # alle Zeilen, Element
        self.plane.flight_conditions.climb.results.gamma_max = gamma_max
        return gamma_max

    def get_v_v_max(self):
        # V_v maximal
        res = minimize_scalar(self.evaluate, bounds=(self.cl_start, self.cl_end), method='bounded',
                              options={'xatol': 0.01})
        return -res.fun

    def get_h_max(self, delta_t, h0=0):
        """
        Returns a gained height. Needs therefore a timespan and an additional value.
        """
        v_vertical_max = self.get_v_v_max()
        height = h0 + v_vertical_max * delta_t
        return height