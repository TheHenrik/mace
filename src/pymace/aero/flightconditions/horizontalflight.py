
import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import bisect

import pymace.aero.generalfunctions as functions
from pymace.aero.generalfunctions import GeneralFunctions
from pymace.aero.implementations.aero import Aerodynamics
from pymace.aero.implementations.airfoil_analyses import Airfoil
from pymace.domain import params
from pymace.domain.vehicle import Vehicle


class HorizontalFlight:
    def __init__(self, plane: Vehicle):
        self.plane = plane
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho
        self.cl_start = 0.01
        self.cl_end = 1.0
        self.cl_step = 0.05

        self.flap_angle = 0.0
        self.optimize_flap_angle = True

        self.Aero = Aerodynamics(self.plane)
        self.Aero.XFOIL.print_re_warnings = False

        self.batt_time_at_start = 40.0
        self.cruise_time = 90.0

        self.xtol = 0.1

    def get_drag_force(self, V):
        plane = self.plane
        S_ref = self.s_ref
        CD = plane.aero_coeffs.drag_coeff.cd_tot
        D = CD * 0.5 * self.rho * V**2 * S_ref
        return D

    def flight_velocity(self, CL):
        V = ((2 * self.mass * self.g) / (CL * self.rho * self.s_ref)) ** 0.5
        return V

    def lift_coefficient(self, V):
        CL = (self.mass * self.g) / (0.5 * self.rho * V**2 * self.s_ref)
        return CL

    def fv_diagramm(self):
        """
        cl_start has to be above 0. If not, no horizontal flight is possible.
        Returns an array with the correlation between velocity and needed thrust supply in horizontal flight.
        [[v1, d1, t1], [v2, d2, t2], [...], ...]
        """
        # Initialize vectors
        cl_list = np.arange(self.cl_start, self.cl_end, self.cl_step)
        results = []
        thrust = GeneralFunctions(self.plane).current_thrust

        # Evaluate required thrust in cl range
        for CL in cl_list:
            V = self.flight_velocity(CL)

            self.Aero.evaluate(CL=CL, V=V, FLAP=self.flap_angle)

            # Calculate total drag force
            D = self.get_drag_force(V)

            # --- Evaluate Thrust ---
            T = thrust(V)

            results.append([V, D, T])

        self.plane.flight_conditions.horizontal_flight.results.thrust_velocity_correlation = np.array(
            results
        )

    def get_maximum_velocity(self):
        """
        Returns the maximum velocity in horizontal flight.
        """
        results = self.plane.flight_conditions.horizontal_flight.results.thrust_velocity_correlation
        if results is None:
            self.fv_diagramm()
            results = self.plane.flight_conditions.horizontal_flight.results.thrust_velocity_correlation

        V = results[:, 0]
        D = results[:, 1]
        T = results[:, 2]

        # Get maximum velocity
        f_drag = interp1d(
            V, D, kind="quadratic", fill_value="extrapolate", bounds_error=False
        )
        f_thrust = interp1d(V, T, kind="quadratic", fill_value=0, bounds_error=False)

        def objective(V):
            return f_drag(V) - f_thrust(V)

        V_max = bisect(objective, min(V), max(V))
        return V_max

    def get_maximum_velocity_scipy(self):
        Aero = Aerodynamics(self.plane)
        batt_mid_time = self.batt_time_at_start + self.cruise_time / 2

        def func(V, return_values=False):
            CL = self.lift_coefficient(V)
            if self.optimize_flap_angle is True:
                c_length = self.plane.reference_values.c_ref
                re = functions.get_reynolds_number(V, c_length)
                x_hinge = 1 - self.plane.wings["main_wing"].segments[0].flap_chord_ratio
                airfoil = Airfoil(
                    self.plane.wings["main_wing"].airfoil, x_hinge=x_hinge
                )
                self.flap_angle = airfoil.check_for_best_flap_setting(re, CL)
            self.Aero.evaluate(CL=CL, V=V, FLAP=self.flap_angle)
            D = self.get_drag_force(V)
            # T = GeneralFunctions(self.plane).current_thrust(V)
            T = self.plane.evaluate_thrust(V, batt_mid_time)

            if return_values:
                results = self.plane.results
                results.cruise_air_speed = V
                results.cruise_flap_angle = self.flap_angle
                results.cruise_cl = CL
                results.cruise_drag_force = D
                results.cruise_reynolds = re
                (
                    results.cruise_battery_voltage,
                    results.cruise_battery_soc,
                ) = self.plane.battery.get_voltage(i=30.0, t=batt_mid_time)
            return D - T

        from scipy.optimize import root_scalar

        v_min = self.flight_velocity(self.cl_start)
        v_max = self.flight_velocity(self.cl_end)
        res = root_scalar(func, bracket=(v_min, v_max), method="brentq", xtol=self.xtol)
        func(res.root, return_values=True)
        return res.root

    def plot_fv_diagramm(self):
        """
        Plots the thrust-velocity correlation.
        """
        import matplotlib.pyplot as plt

        results = self.plane.flight_conditions.horizontal_flight.results.thrust_velocity_correlation
        if results is None:
            self.fv_diagramm()
            results = self.plane.flight_conditions.horizontal_flight.results.thrust_velocity_correlation

        V = results[:, 0]
        D = results[:, 1]
        T = results[:, 2]

        fig = plt.figure(dpi=400)
        ax = fig.add_subplot(111)
        ax.plot(V, D, label="Drag")
        ax.plot(V, T, label="Thrust")
        ax.set_xlabel("Velocity [m/s]")
        ax.set_ylabel("Force [N]")
        plt.legend()
        plt.grid()
        plt.tick_params(which="major", labelsize=6)

        plt.title("Horizontal Flight", fontsize=10)
        plt.show()
