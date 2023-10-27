import logging
import time
import warnings

import numpy as np
from scipy.optimize import fsolve, root_scalar, minimize, differential_evolution
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
    def __init__(self, Aircraft: Vehicle) -> None:
        self.plane = Aircraft
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.get_thrust = GeneralFunctions(self.plane).current_thrust
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

        self.plot_surface = False

    def T(self, V, I):
        thrust_array = self.plane.propulsion.thrust
        thrust_force = I / 30 * np.interp(V, thrust_array[:, 0], thrust_array[:, 1])
        return thrust_force

    def get_drag_force(self, V):
        if V > self.v_min:
            CL = self.mass * g / (0.5 * rho * V**2 * self.s_ref)

            if self.optimize_flap_angle:
                c_length = self.plane.reference_values.c_ref
                re = functions.get_reynolds_number(V, c_length)
                airfoil = Airfoil(self.plane.wings["main_wing"].airfoil)
                airfoil.print_re_warnings = False
                self.flap_angle = airfoil.check_for_best_flap_setting(re, CL)

            self.Aero.evaluate(V=V, CL=CL, FLAP=self.flap_angle)
            drag_coefficient = self.plane.aero_coeffs.drag_coeff.cd_tot
            drag_force = rho / 2 * V**2 * self.s_ref * drag_coefficient
        else:
            drag_force = 100.0
            # print('V to low, returning default drag value')
        return drag_force

    def D(self, V):
        vmin = self.v_min
        vmax = self.v_max
        v_vec = np.linspace(vmin, vmax, 10)
        if self.is_drag_surrogate_build == False:
            self.drag_surrogate = np.array([self.get_drag_force(v) for v in v_vec])
            self.is_drag_surrogate_build = True
            drag_force = np.interp(V, v_vec, self.drag_surrogate)
        else:
            drag_force = np.interp(
                V, v_vec, self.drag_surrogate, right=100.0, left=100.0
            )
        return drag_force

    def equation_system(self, E0, v1, t1, I, print_results=False):
        T = self.T
        D = self.D
        m = self.mass
        h2 = self.h_end
        tges = self.t_ges

        def func(x):
            h1 = min(x[0], 100)
            v2 = max(x[1], 0)

            eq1 = E0 + (T(v1, I) - D(v1)) * v1 * t1 - 1 / 2 * m * v1**2 - m * g * h1
            eq2 = (
                1 / 2 * m * v1**2
                + m * g * h1
                - D(v2) * v2 * (tges - t1)
                - m * g * h2
                - 1 / 2 * m * v2**2
            )
            return [eq1, eq2]

        root = fsolve(func, [60, 13], xtol=1e-4, maxfev=1000)
        if np.all(np.isclose(func(root), [0.0, 0.0], atol=1e-1)):
            if print_results:
                logging.debug(
                    "->   h1:", round(min(root[0], 100), 1), "v2:", round(root[1], 1)
                )
            return root
        else:
            if print_results:
                logging.info("-> No solution found")
            return [0, 0]

    def optimizer(self, v0, h0, I=30):
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
                return 0
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
                self.equation_system(E0, v1, t1, I, print_results=True)
                logging.debug("points: ", round(points, 5))
                logging.debug("\n")

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
                tol=0.1,
                workers=1,
            )
            return -objective_function(result.x, print_results=True)
        else:
            import matplotlib.pyplot as plt

            v1_vec = np.linspace(0, 1, 100)
            t1_vec = np.linspace(0, 1, 100)
            points = np.zeros((len(v1_vec), len(t1_vec)))
            for i, v1 in enumerate(v1_vec):
                for j, t1 in enumerate(t1_vec):
                    points[i, j] = -1.0 * objective_function(
                        [v1, t1], print_results=True
                    )
            x, y = np.meshgrid(v1_vec, t1_vec)
            fig, ax = plt.subplots(subplot_kw={"projection": "3d"})
            ax.plot_surface(x, y, points)
            ax.set_proj_type("ortho")
            ax.set_xlabel("t1")
            ax.set_ylabel("v1")
            ax.set_zlabel("points")
            plt.show()
            np.save("points_+1600.npy", points)

    def get_v_max(self, I, v0=15.0):
        def func(v):
            return self.T(v, I) - self.get_drag_force(v)

        v_max = root_scalar(func, method="brentq", bracket=[v0 + 1, 40], xtol=0.5).root
        return v_max

    def get_v_min(self, v0=15.0):
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
        m = self.mass
        D = self.D
        T = self.T
        hend = self.h_end
        tend = self.t_ges
        t1_min = (tend * v2 * D(v2) + m * g * (hend - h0)) / (
            v1 * (T(v1, I) - D(v1) + v2 * D(v2))
        )
        return t1_min


if __name__ == "__main__":
    from mace.aero.implementations.avl import (
        geometry_and_mass_files_v2 as geometry_and_mass_files,
    )
    from mace.test.vehicle_setup_acc import vehicle_setup

    Aircraft = vehicle_setup()
    Aircraft.mass -= 0.0
    mass_file = geometry_and_mass_files.MassFile(Aircraft)
    mass_file.build_mass_file()
    geometry_file = geometry_and_mass_files.GeometryFile(Aircraft)
    geometry_file.z_sym = 0
    geometry_file.build_geometry_file()

    efficiency_flight = EfficiencyFlight(Aircraft)
    efficiency_flight.plot_surface = True
    v0 = 17.1
    h0 = 72
    efficiency_flight.optimizer(v0, h0)
    # print(result)
