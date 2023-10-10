import math
import time

import numpy as np
from scipy.optimize import fsolve, minimize_scalar

import mace.aero.generalfunctions as functions
from mace.aero.generalfunctions import GeneralFunctions
from mace.aero.implementations.aero import Aerodynamics
from mace.aero.implementations.airfoil_analyses import Airfoil
from mace.domain import params
from mace.domain.vehicle import Vehicle


class Climb:
    def __init__(self, plane: Vehicle):
        self.plane = plane
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho

        self.cl_start = 0.01
        self.cl_end = 0.5

        self.flap_angle = 0.0
        self.optimize_flap_angle = True

    def evaluate(self, CL, return_v=False):
        Aero = Aerodynamics(self.plane)
        T = GeneralFunctions(self.plane).current_thrust

        s = self.s_ref
        m = self.mass
        g = self.g
        V0 = ((2 * m * g) / (CL * self.rho * self.s_ref)) ** 0.5

        if self.optimize_flap_angle:
            c_length = self.plane.reference_values.c_ref
            re = functions.get_reynolds_number(V0, c_length)
            airfoil = Airfoil(self.plane.wings["main_wing"].airfoil)
            self.flap_angle = airfoil.check_for_best_flap_setting(re, CL)

        def func(x):
            v = x[0]
            alpha = x[1]
            q = self.rho / 2 * v**2
            Aero.evaluate(V=v, CL=CL, FLAP=self.flap_angle)

            CD = self.plane.aero_coeffs.drag_coeff.cd_tot
            eq1 = q * CD * s + np.sin(alpha) * m * g - T(v)
            eq2 = np.cos(alpha) * m * g - q * CL * s
            return [eq1, eq2]

        v, alpha = fsolve(func, [V0, 0], xtol=1e-3, factor=10)
        V_vertical = v * np.sin(alpha)
        if return_v:
            return v
        return -V_vertical

    def get_v_v_max(self):
        # V_v maximal
        res = minimize_scalar(
            self.evaluate,
            bounds=(self.cl_start, self.cl_end),
            method="bounded",
            options={"xatol": 0.01},
        )
        v = self.evaluate(res.x, return_v=True)
        return -res.fun, v

    def get_h_max(self, delta_t, h0=0):
        """
        Returns a gained height. Needs therefore a timespan and an additional value.
        """
        v_vertical_max, v = self.get_v_v_max()
        height = h0 + v_vertical_max * delta_t
        return height, v
