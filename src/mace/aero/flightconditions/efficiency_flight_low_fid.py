import logging
import time
import warnings

import numpy as np
from scipy.optimize import differential_evolution, fsolve, minimize, root_scalar
from skopt import BayesSearchCV, gp_minimize

import mace.aero.generalfunctions as functions
from mace.aero.generalfunctions import GeneralFunctions
from mace.aero.implementations.aero import Aerodynamics
from mace.aero.implementations.airfoil_analyses import Airfoil
from mace.domain import params
from mace.domain.vehicle import Vehicle

g = params.Constants.g
rho = params.Constants.rho

warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)


class EfficiencyFlight:
    """
    This method is used to estimate the scoring for the efficiency task in the Air Cargo Challenge 2024.
    Hereby, the scoring is calculated based on the distance and energy consumption of the aircraft.

    Score = distance^2 / (2 * distance + energy) [Distance in km, Energy in Wh]
    ... evaluated during in 90 seconds of flight, after a 30 seconds runtime (approx. 25 seconds climb after takeoff)

    The efficiency flight analysis is based on the following assumptions:
    1. The aircraft flies in 2 stationary conditions: motor on, with velocity v1, full throttle and a duration t1,
         and motor off, with velocity v2, and a duration t2 = t_ges - t1
    2. The efficiency flights begins with the initial climb height and speed and ends in the minimum height of 10 m and v2
    3. A small climb/descent angle is assumed to lower the complexity of the problem
    4. The calculation is based on an energy method, with initial energy, energy gain and loss and final energy after t1, tges
    5. An optimization algorithm is used to find the optimal v1 and t1, which maximizes the score
    """
    def __init__(self, Aircraft: Vehicle) -> None:
        """
        :param Aircraft: Vehicle object

        This initializes the efficiency flight analysis by setting up default values
        """
        self.plane = Aircraft
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.optimize_flap_angle = True
        self.flap_angle = 0.0
        self.Aero = Aerodynamics(self.plane)
        self.Aero.XFOIL.print_re_warnings = False
        self.h_end = 10.0
        self.t_ges = 90.0
        self.v_min = 10.0
        self.v_max = 100.0
        self.is_drag_surrogate_build = False
        self.drag_surrogate: np.ndarray = None
        self.is_drag_surrogate_build2 = False
        self.drag_surrogate2: np.ndarray = None
        self.plot_surface = False
        self.batt_time_at_start = 30.0
        self.tolerance = 0.1


    def T(self, V, t_avg, I):
        """
        :param V: Velocity [m/s]
        :param t_avg: Average total time (from begin of battery discharge) of operating point [s]
        :param I: Current [A]

        This funtion returns the thrust, under consideration of velocity dependency, throttle condition and battery discharge
        """
        return self.plane.evaluate_thrust(V, t_avg, I=I)

    def get_drag_force(self, V):
        """
        :param V: Velocity [m/s]

        This function returns the drag force, while the flap angle is optimized for the current operating point
        """
        if V > self.v_min:
            CL = self.mass * g / (0.5 * rho * V**2 * self.s_ref)

            if self.optimize_flap_angle:
                c_length = self.plane.reference_values.c_ref
                re = functions.get_reynolds_number(V, c_length)
                x_hinge = 1 - self.plane.wings["main_wing"].segments[0].flap_chord_ratio
                airfoil = Airfoil(self.plane.wings["main_wing"].airfoil, x_hinge=x_hinge)
                airfoil.print_re_warnings = False
                self.flap_angle = airfoil.check_for_best_flap_setting(re, CL)

            self.Aero.XFOIL.sensitivity_study_drag_factor = 1.
            self.Aero.evaluate(V=V, CL=CL, FLAP=self.flap_angle)
            drag_coefficient = self.plane.aero_coeffs.drag_coeff.cd_tot
            drag_force = rho / 2 * V**2 * self.s_ref * drag_coefficient
        else:
            drag_force = 100.0
            # print('V to low, returning default drag value')
        return drag_force

    def get_drag_force2(self, V):
        """
        :param V: Velocity [m/s]

        This function returns the drag force, while the flap angle is optimized for the current operating point
        """
        if V > self.v_min:
            CL = self.mass * g / (0.5 * rho * V**2 * self.s_ref)

            if self.optimize_flap_angle:
                c_length = self.plane.reference_values.c_ref
                re = functions.get_reynolds_number(V, c_length)
                x_hinge = 1 - self.plane.wings["main_wing"].segments[0].flap_chord_ratio
                airfoil = Airfoil(self.plane.wings["main_wing"].airfoil, x_hinge=x_hinge)
                airfoil.print_re_warnings = False
                self.flap_angle = airfoil.check_for_best_flap_setting(re, CL)

            self.Aero.XFOIL.sensitivity_study_drag_factor = 1.
            self.Aero.evaluate(V=V, CL=CL, FLAP=self.flap_angle)
            drag_coefficient = self.plane.aero_coeffs.drag_coeff.cd_tot
            drag_force = rho / 2 * V**2 * self.s_ref * drag_coefficient
        else:
            drag_force = 100.0
            # print('V to low, returning default drag value')
        return drag_force

    def D(self, V):
        """
        :param V: Velocity [m/s]

        This function returns the drag force from a built surrogate model, to save computation time.
        If the surrogate model is not built yet, it is built and saved for future use.
        """
        vmin = self.v_min
        vmax = self.v_max
        v_vec = np.linspace(vmin, vmax, 20)
        if self.is_drag_surrogate_build == False:
            self.drag_surrogate = np.array([self.get_drag_force(v) for v in v_vec])
            self.is_drag_surrogate_build = True
            drag_force = np.interp(V, v_vec, self.drag_surrogate)
        else:
            drag_force = np.interp(
                V, v_vec, self.drag_surrogate, right=100.0, left=100.0
            )
        return drag_force

    def D2(self, V):
        """
        :param V: Velocity [m/s]

        This function returns the drag force from a built surrogate model, to save computation time.
        If the surrogate model is not built yet, it is built and saved for future use.
        """
        vmin = self.v_min
        vmax = self.v_max
        v_vec = np.linspace(vmin, vmax, 20)
        if self.is_drag_surrogate_build2 == False:
            self.drag_surrogate2 = np.array([self.get_drag_force2(v) for v in v_vec])
            self.is_drag_surrogate_build2 = True
            drag_force = np.interp(V, v_vec, self.drag_surrogate)
        else:
            drag_force = np.interp(
                V, v_vec, self.drag_surrogate2, right=100.0, left=100.0
            )
        return drag_force

    def equation_system(self, E0, v1, t1, I, print_results=False):
        """
        :param E0: Initial energy [J]
        :param v1: Velocity [m/s]
        :param t1: Duration of motor on [s]
        :param I: Current [A]
        :param print_results: If True, the results are printed

        This function solves the equation system for the efficiency flight analysis
        """
        T = self.T
        D = self.D
        D2 = self.D2
        m = self.mass
        h2 = self.h_end
        tges = self.t_ges

        t_avg = self.batt_time_at_start + t1 / 2

        def func(x):
            h1 = x[0]
            # h1 = min(x[0], 100)
            v2 = max(x[1], 0)

            eq1 = (
                E0
                + (T(v1, t_avg, I) - D(v1)) * v1 * t1
                - 1 / 2 * m * v1**2
                - m * g * h1
            )
            eq2 = (
                1 / 2 * m * v1**2
                + m * g * h1
                - D2(v2) * v2 * (tges - t1)
                - m * g * h2
                - 1 / 2 * m * v2**2
            )
            return [eq1, eq2]

        root = fsolve(func, [60, 13], xtol=1e-4, maxfev=1000)
        if np.all(np.isclose(func(root), [0.0, 0.0], atol=1e-1)):
            if print_results:
                print(
                    "->   h1:", round(root[0], 1), "v2:", round(root[1], 1)
                )
            return root
        else:
            if print_results:
                logging.info("-> No solution found")
            return [0, 0]

    def optimizer(self, v0, h0, I=30):
        """
        :param v0: Initial velocity [m/s]
        :param h0: Initial height [m]
        :param I: Current [A]

        This function optimizes the efficiency flight analysis for the given aircraft and initial conditions
        """
        self.v_min = self.get_v_min(v0=v0)
        self.v_max = self.get_v_max(I, v0=self.v_min)
        E0 = 1 / 2 * self.mass * v0**2 + self.mass * g * h0

        def objective_function(x, print_results=False):
            v1_scale = x[0]
            t_scale = x[1]
            # I = x[2]

            vmin = self.v_min
            vmax = self.v_max
            v1 = vmin + v1_scale * (vmax - vmin)

            tmin = self.get_t1_min(v1, v0, I, h0)
            if tmin < 0:
                tmin = 0
            tmax = self.t_ges
            t1 = tmin + t_scale * (tmax - tmin)

            root = self.equation_system(E0, v1, t1, I)
            v2 = root[1]

            distance = (v1 * t1 + v2 * (self.t_ges - t1)) / 1000
            energy = I * 11.5 * t1 / 3600
            # print('distance: ', round(distance,3), 'energy: ', round(energy,3))
            points = distance**2 / (2 * distance + energy)
            # print('points: ', round(points,5))

            if print_results:
                logging.debug("\n")
                logging.debug("v1: ", round(v1, 2), "t1: ", round(t1, 2), "I: ", I)
                self.equation_system(E0, v1, t1, I, print_results=False)
                logging.debug("points: ", round(points, 5))
                logging.debug("\n")

                c_length = self.plane.reference_values.c_ref
                airfoil = Airfoil(self.plane.wings["main_wing"].airfoil)
                airfoil.print_re_warnings = False

                cl_1 = self.mass * g / (0.5 * rho * v1**2 * self.s_ref)
                re_1 = functions.get_reynolds_number(v1, c_length)
                flap_angle_1 = airfoil.check_for_best_flap_setting(re_1, cl_1)

                cl_2 = self.mass * g / (0.5 * rho * v2**2 * self.s_ref)
                re_2 = functions.get_reynolds_number(v2, c_length)
                flap_angle_2 = airfoil.check_for_best_flap_setting(re_2, cl_2)

                res = self.plane.results

                res.efficiency_motor_on_air_speed = v1
                res.efficiency_motor_on_cl = cl_1
                res.efficiency_motor_on_reynolds = re_1
                res.efficiency_motor_on_flap_angle = flap_angle_1
                res.efficiency_motor_on_time = t1

                res.efficiency_motor_off_air_speed = v2
                res.efficiency_motor_off_cl = cl_2
                res.efficiency_motor_off_reynolds = re_2
                res.efficiency_motor_off_flap_angle = flap_angle_2
                res.efficiency_motor_off_time = self.t_ges - t1

                t_avg = self.batt_time_at_start + t1 / 2
                (
                    res.efficiency_battery_voltage,
                    res.efficiency_battery_soc,
                ) = self.plane.battery.get_voltage(i=30.0, t=t_avg)

            if self.plot_surface:
                h1 = root[0]
                return points, v2, h1
            return -points

        if self.plot_surface == False:
            param_space = [(0.0, 1.0), (0.0, 1.0)]
            time0 = time.time()
            # result = gp_minimize(
            #     func=objective_function,
            #     dimensions=param_space,
            #     n_calls=100,
            #     n_initial_points=25,
            #     initial_point_generator="hammersly",
            #     acq_optimizer="sampling",
            #     n_jobs=1,
            #     x0=[0.5, 0.5],
            # )
            result = differential_evolution(
                func=objective_function,
                bounds=[(0, 1), (0, 1)],
                strategy="best1bin",
                tol=self.tolerance,
                workers=1,
            )
            v1_scale = result.x[0]
            t_scale = result.x[1]

            vmin = self.v_min
            vmax = self.v_max
            v1 = vmin + v1_scale * (vmax - vmin)

            tmin = self.get_t1_min(v1, v0, I, h0)
            if tmin < 0:
                tmin = 0
            tmax = self.t_ges
            t1 = tmin + t_scale * (tmax - tmin)

            root = self.equation_system(E0, v1, t1, I)
            v2 = root[1]

            return -objective_function(result.x, print_results=True), v1, t1, v2
        else:
            import matplotlib.pyplot as plt

            v1_vec = np.linspace(0, 1, 100)
            t1_vec = np.linspace(0, 1, 100)

            v1_actual = self.v_min + v1_vec * (self.v_max - self.v_min)
            tmin = 0

            tmax = self.t_ges

            t1_actual = tmin + t1_vec * (tmax - tmin)

            points = np.zeros((len(v1_vec), len(t1_vec)))
            v2 = np.zeros((len(v1_vec), len(t1_vec)))
            h1 = np.zeros((len(v1_vec), len(t1_vec)))
            for i, v1 in enumerate(v1_vec):
                for j, t1 in enumerate(t1_vec):
                    points[i, j], v2[i, j], h1[i, j]  = objective_function(
                        [v1, t1], print_results=False
                    )

            points = points.T
            v2 = v2.T
            h1 = h1.T

            v1matrix, t1matrix = np.meshgrid(v1_actual, t1_actual)
            fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
            ax.plot_surface(v1matrix, t1matrix, points)
            ax.set_proj_type("ortho")
            ax.set_xlabel("v1")
            ax.set_ylabel("t1")
            ax.set_zlabel("points")
            plt.show()

            import pandas as pd

            # Erstelle ein DataFrame aus den Arrays
            df = pd.DataFrame({
                'v_1': v1matrix.ravel(),
                't_1': t1matrix.ravel(),
                'points': points.ravel(),
                'v_2': v2.ravel(),
                'h_1': h1.ravel()
            })

            # Exportiere das DataFrame in eine CSV-Datei
            df.to_csv('efficiency_plot.csv', index_label='v1')

    def get_v_max(self, I, v0=15.0):
        """
        :param I: Current [A]
        :param v0: Initial velocity (optional, for initial guess) [m/s]

        This function returns the maximum velocity for the given aircraft and current
        """
        def func(v):
            return self.T(v, self.batt_time_at_start, I) - self.get_drag_force(v)

        v_max = root_scalar(func, method="brentq", bracket=[v0 + 1, 40], xtol=0.5).root
        return v_max

    def get_v_min(self, v0=15.0):
        """
        :param v0: Initial velocity (optional, for initial guess) [m/s]

        This function returns the minimum velocity (stall speed) for the given aircraft
        """
        c_length = self.plane.reference_values.c_ref
        airfoil = Airfoil(self.plane.wings["main_wing"].airfoil)
        v_min = v0 - 1
        v = v0
        while abs(v - v_min) > 0.01:
            re = functions.get_reynolds_number(v, c_length)
            v = v_min
            cl_max = airfoil.get_cl_max(re)
            v_min = (self.mass * g / (0.5 * rho * cl_max * self.s_ref)) ** 0.5
        return v_min

    def get_t1_min(self, v1, v2, I, h0):
        """
        :param v1: Velocity with motor on [m/s]
        :param v2: Velocity with motor off [m/s]
        :param I: Current [A]
        :param h0: Initial height [m]

        This function returns the minimum duration of motor on for the given aircraft and initial conditions.
        It is used to avoid a high number of meaningless combinations in the optimization process, where the aircraft
        is not able to glide the required time without going below the minimum height.
        """
        m = self.mass
        D = self.D
        T = self.T
        hend = self.h_end
        tend = self.t_ges
        t1_min = (tend * v2 * D(v2) + m * g * (hend - h0)) / (
            v1 * (T(v1, self.batt_time_at_start, I) - D(v1) + v2 * D(v2))
        )
        return t1_min


if __name__ == "__main__":
    from mace.aero.implementations.avl import (
        geometry_and_mass_files_v2 as geometry_and_mass_files,
    )
    from mace.test.vehicle_setup_acc_v4 import vehicle_setup
    from mace.aero.flightconditions.climb_scipy import Climb

    Aircraft = vehicle_setup(payload=4.75)
    print(Aircraft.mass)
    Aircraft.mass -= 0.0
    mass_file = geometry_and_mass_files.MassFile(Aircraft)
    mass_file.build_mass_file()
    geometry_file = geometry_and_mass_files.GeometryFile(Aircraft)
    geometry_file.z_sym = 0
    geometry_file.build_geometry_file()

    climb_analysis = Climb(Aircraft)
    climb_analysis.optimize_flap_angle = True
    climb_analysis.mid_time = 15
    climb_height, climb_ias = climb_analysis.get_h_max(
        delta_t=20
    )
    climb_height = min(climb_height, 100.0)
    print("H Climb: %.1f m, V IAS %.1f m/s" % (climb_height, climb_ias))

    efficiency_flight = EfficiencyFlight(Aircraft)
    efficiency_flight.plot_surface = True
    v0 = climb_ias
    h0 = climb_height
    efficiency_flight.optimizer(v0, h0)
