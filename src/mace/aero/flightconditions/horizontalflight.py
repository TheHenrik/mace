import numpy as np
from scipy.interpolate import interp1d
from scipy.optimize import bisect
from mace.domain import params, Plane
from mace.aero.implementations.aero import Aerodynamics
from mace.aero.generalfunctions import GeneralFunctions


class HorizontalFlight:
    def __init__(self, plane: Plane):
        self.plane = plane
        self.mass = self.plane.mass[0]
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho
        self.CL_start = 0.05
        self.CL_end = 1.
        self.CL_step = 0.05

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
        CL_list = np.arange(self.CL_start, self.CL_end, self.CL_step)
        results = []
        Aero = Aerodynamics(self.plane)
        thrust = GeneralFunctions(self.plane).current_thrust

        # Evaluate required thrust in cl range
        for CL in CL_list:
            V = self.flight_velocity(CL)

            Aero.evaluate(CL=CL, V=V)
            
            # Calculate total drag force
            D = self.get_drag_force(V)
            
            # --- Evaluate Thrust ---
            T = thrust(V)

            results.append([V, D, T])

        self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation = np.array(results)

    def get_maximum_velocity(self):
        """
        Returns the maximum velocity in horizontal flight.
        """
        results = self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation
        if results is None:
            self.fv_diagramm()
            results = self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation

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
        results = self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation
        if results is None:
            self.fv_diagramm()
            results = self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation

        V = results[:, 0]
        D = results[:, 1]
        T = results[:, 2]

        plt.plot(V, D, label="Drag")
        plt.plot(V, T, label="Thrust")
        plt.xlabel("Velocity [m/s]")
        plt.ylabel("Force [N]")
        plt.legend()
        plt.grid()
        plt.title("Horizontal Flight")
        plt.show()