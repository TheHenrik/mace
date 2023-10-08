from mace.domain.vehicle import Vehicle
from mace.domain import params
from mace.aero.implementations.aero import Aerodynamics
from mace.aero.generalfunctions import GeneralFunctions
from mace.aero.implementations.airfoil_analyses import Airfoil
import mace.aero.generalfunctions as functions
from scipy.optimize import fsolve
from scipy.optimize import root_scalar
from scipy.optimize import minimize_scalar
from scipy.optimize import minimize
from skopt import dummy_minimize
from skopt import gp_minimize, BayesSearchCV
import matplotlib.pyplot as plt
import numpy as np


class EfficiencyFlight:
    def __init__(self, Aircraft: Vehicle) -> None:
        self.plane = Aircraft
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho
        self.optimize_flap_angle = True
        self.flap_angle = 0.0
        self.v_tolerance = 0.1
        self.it_max = 20
        self.minimum_V_vertical = None
        self.v_at_minimum_V_vertical = None
        self.plots = True

    def v_climb(self, current_thrust, cl, cd):
        a = (self.rho / 2) * self.s_ref * (cd**2 + cl**2)
        b = -2 * current_thrust * cd
        c = (current_thrust**2 - (self.mass * self.g) ** 2) / (
            (self.rho / 2) * self.s_ref
        )
        v_square = (-b + (b**2 - 4 * a * c) ** 0.5) / (2 * a)
        v = v_square**0.5
        return v

    def sin_gamma(self, current_thrust, v_square, cd):
        sin = (current_thrust - (self.rho / 2) * v_square * self.s_ref * cd) / (
            self.mass * self.g
        )
        return sin

    def cos_gamma(self, v_square, cl):
        cos = ((self.rho / 2) * v_square * self.s_ref * cl) / (self.mass * self.g)
        return cos

    def func(self, V, I):
        CL = self.mass * self.g / (0.5 * self.rho * V**2 * self.s_ref)
        # Check if CL is within the limits of the airfoil
        c_length = self.plane.reference_values.c_ref
        re = functions.get_reynolds_number(V, c_length)
        airfoil = Airfoil(self.plane.wings["main_wing"].airfoil)
        airfoil.print_re_warnings = False
        if CL > airfoil.get_cl_max(re):
            return -10, 0

        v_tolerance = self.v_tolerance
        it_max = self.it_max
        Aero = Aerodynamics(self.plane)
        Aero.XFOIL.print_re_warnings = False
        thrust = GeneralFunctions(self.plane).current_thrust
        not_in_tolerance = True
        it = 0
        V2 = V

        while not_in_tolerance and it < it_max:
            if self.optimize_flap_angle:
                c_length = self.plane.reference_values.c_ref
                re = functions.get_reynolds_number(V2, c_length)
                airfoil = Airfoil(self.plane.wings["main_wing"].airfoil)
                airfoil.print_re_warnings = False
                self.flap_angle = airfoil.check_for_best_flap_setting(re, CL)

            Aero.evaluate(V=V, CL=CL, FLAP=self.flap_angle)
            CD = self.plane.aero_coeffs.drag_coeff.cd_tot
            T = thrust(V) * I / 30.0
            V2 = self.v_climb(T, CL, CD)
            it += 1
            not_in_tolerance = abs(V - V2) >= v_tolerance
            CL = CL * (V2 / V) ** 2

        sin = self.sin_gamma(T, V**2, CD)
        cos = self.cos_gamma(V**2, CL)

        V_vertical = V * sin
        V_horizontal = V * cos

        return V_vertical, V_horizontal

    def motor_on(self, V, I, t, h1):
        V_vertical, V_horizontal = self.func(V, I)
        deltaH = V_vertical * t
        deltaS = V_horizontal * t
        deltaE = I * t * 11.5
        if h1 + deltaH < 10:
            deltaH = -1 * (h1 - 10)
            deltaS = 0.1
            deltaE = 1e3
        return deltaS, deltaH, deltaE

    def motor_off(self, deltaH, t):
        target_V_vertical = deltaH / t

        def minimize_func(V):
            V_vertical, V_horizontal = self.func(V, 0)
            return -V_vertical

        def root_func(V):
            V_vertical, V_horizontal = self.func(V, 0)
            return -V_vertical - target_V_vertical

        if self.minimum_V_vertical == None:
            res = minimize_scalar(minimize_func, bounds=(5, 50), options={"xatol": 0.1})
            self.v_at_minimum_V_vertical = res.x
            self.minimum_V_vertical = res.fun

        if self.minimum_V_vertical < target_V_vertical:
            V = root_scalar(
                root_func,
                bracket=(
                    self.v_at_minimum_V_vertical,
                    5 * self.v_at_minimum_V_vertical,
                ),
                method="brentq",
                xtol=0.1,
            )
            V_vertical, V_horizontal = self.func(V.root, 0)
            deltaS = V_horizontal * t
            deltaH = V_vertical * t
            deltaE = 0
            return deltaS, deltaH, deltaE
        else:
            return 0, 0, 0

    def evaluate(self, V_motor_on, I, t_motor_on, h0, v0):
        s1 = 0.0
        h1 = h0 + (1 / 2 * v0**2 - 1 / 2 * V_motor_on**2) / 9.81
        e1 = 0.0
        if I > 0 and t_motor_on > 0:
            deltaS1, deltaH1, deltaE1 = self.motor_on(V_motor_on, I, t_motor_on, h1)
            s2 = s1 + deltaS1
            h2 = h1 + deltaH1
            e2 = e1 + deltaE1
        else:
            s2 = s1
            h2 = h1
            e2 = e1
        h2 = min(h2, 100)

        if t_motor_on < 90:
            deltaS2, deltaH2, deltaE2 = self.motor_off(h2 - 10, 90 - t_motor_on)
            s3 = s2 + deltaS2
            h3 = h2 + deltaH2
            e3 = e2 + deltaE2
        else:
            s3 = s2
            h3 = h2
            e3 = e2
        s = s3 / 1000.0
        e = e3 / 3600.0

        points = (s) ** 2 / (2 * s + e)
        if I > 30:
            penalty_points = 0.5 * (I - 30) * t_motor_on
            points_factor = (333.33 - penalty_points) / 333.33
            points *= points_factor

        if points != 0 and self.plots == True:
            plt.plot((0, s1), (h0, h1), "k")
            plt.plot((s1, s2), (h1, h2), "k")
            plt.plot((s2, s3), (h2, h3), "k")
            plt.grid()
            plt.title("E_TEAM: %.3f" % points)
            plt.show()

        return points

    def optimize_for_competition_points(self, h0, v0):
        def objective_function(x):
            V_motor_on = x[0]
            I = x[1]
            t_motor_on = x[2]
            print(
                "V_motor_on: %.3f, I: %.3f, t_motor_on: %.3f"
                % (V_motor_on, I, t_motor_on)
            )
            points = self.evaluate(V_motor_on, I, t_motor_on, h0, v0)
            print("points: %.3f" % points)
            return -points

        param_space = [(10.0, 25.0), (5.0, 40.0), (1.0, 80.0)]
        # res = minimize(objective_function, x0=[20., 15., 70.], method='Nelder-Mead', bounds=((10., 50.), (5., 40.), (0., 90.)))
        # res = dummy_minimize(objective_function, param_space, n_calls=10)
        # optimizer = BayesSearchCV(
        #     estimator=None,
        #     # Hier kann ein Modell angegeben werden, das optimiert werden soll (None in diesem Beispiel)
        #     search_spaces=dict(zip(['param1', 'param2', 'param3'], param_space)),
        #     n_iter=100  # Anzahl der Optimierungsiterationen
        # )

        # Führe die Optimierung durch
        result = gp_minimize(
            func=objective_function,
            dimensions=param_space,
            n_calls=100,
            acq_optimizer="auto",
            x0=[20.0, 30.0, 40.0],
        )
        print(result)


if __name__ == "__main__":
    from mace.test.vehicle_setup import vehicle_setup
    from mace.aero.implementations.avl import (
        geometry_and_mass_files_v2 as geometry_and_mass_files,
    )

    Aircraft = vehicle_setup()

    mass_file = geometry_and_mass_files.MassFile(Aircraft)
    mass_file.build_mass_file()
    geometry_file = geometry_and_mass_files.GeometryFile(Aircraft)
    geometry_file.z_sym = 0
    geometry_file.build_geometry_file()

    efficiency_flight = EfficiencyFlight(Aircraft)
    points = efficiency_flight.evaluate(
        V_motor_on=18.0, I=30, t_motor_on=34, h0=50, v0=13.0
    )
    print(points)

    # efficiency_flight.optimize_for_competition_points(h0=50, v0=13.)
