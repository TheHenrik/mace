import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import bisect

from mace.aero.generalfunctions import GeneralFunctions
from mace.aero.implementations.aero import Aerodynamics
from mace.domain import params
from mace.domain.vehicle import Vehicle


class HorizontalFlight:
    def __init__(self, plane: Vehicle):
        self.plane = plane
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho
        self.cl_start = 0.05
        self.cl_end = 1.
        self.cl_step = 0.05
        
        self.flap_angle = 0.

    def get_drag_force(self, V):
        plane = self.plane
        S_ref = self.s_ref
        CD = plane.aero_coeffs.drag_coeff.cd_tot
        D = CD * 0.5 * self.rho * V**2 * S_ref
        return D

    def flight_velocity(self, CL):
        V = ((2 * self.mass * self.g)/(CL * self.rho * self.s_ref))**0.5
        return V

    def fv_diagramm(self):
        """
        cl_start has to be above 0. If not, no horizontal flight is possible.
        Returns an array with the correlation between velocity and needed thrust supply in horizontal flight.
        [[v1, d1, t1], [v2, d2, t2], [...], ...]
        """
        # Initialize vectors
        cl_list = np.arange(self.cl_start, self.cl_end, self.cl_step)
        results = []
        Aero = Aerodynamics(self.plane)
        thrust = GeneralFunctions(self.plane).current_thrust

        # Evaluate required thrust in cl range
        for CL in cl_list:
            V = self.flight_velocity(CL)

            Aero.evaluate(CL=CL, V=V, FLAP=self.flap_angle)
            
            # Calculate total drag force
            D = self.get_drag_force(V)
            
            # --- Evaluate Thrust ---
            T = thrust(V)

            results.append([V, D, T])

        self.plane.flight_conditions.horizontal_flight.results.thrust_velocity_correlation = np.array(results)

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
        f_drag = interp1d(V, D, kind="quadratic", fill_value="extrapolate", bounds_error=False)
        f_thrust = interp1d(V, T, kind="quadratic", fill_value=0, bounds_error=False)
        
        def objective(V):
            return f_drag(V) - f_thrust(V)
        
        V_max = bisect(objective, min(V), max(V))
        return V_max
    
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
        plt.tick_params(which='major', labelsize=6)

        plt.title("Horizontal Flight", fontsize=10)
        plt.show()