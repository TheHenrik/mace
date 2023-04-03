import math

import numpy as np
from mace.domain import params, Plane
from mace.aero.implementations.avl import athenavortexlattice, geometry_and_mass_files
from mace.aero.implementations.viscousdrag import ViscousDrag
from mace.aero.generalfunctions import GeneralFunctions



class Climb:
    def __init__(self, plane: Plane):
        self.plane = plane
        self.mass = self.plane.mass[0]
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho

    def v_climb(self, current_thrust, cl, cd) -> (float, float):
        """
        Returns the velocity (on the flightpath) of a plane.
        (It is a bit more complex compared to horizontal flight.)
        It is !not! the vertical velocity. It is the velocity during climb/descent.
        It depends on the current thrust and aerodynamic coefficients.

        It returns as a tupel (v, v^2).
        """
        """a = ((self.mass * self.g)**2 - current_thrust**2) / ((self.rho/2) * self.s_ref)
        b = (current_thrust * cd)**2 / ((self.rho/2) * self.s_ref * (cd**2 + cl**2))
        c = (self.rho/2) * self.s_ref * (cd**2 + cl**2)
        d = (current_thrust * cd) / ((self.rho/2) * self.s_ref * (cd**2 + cl**2))

        v = (((a + b) / c)**0.5 + d)**0.5
        v_square = ((a + b) / c)**0.5 + d"""

        a = (self.rho/2) * self.s_ref * (cd**2 + cl**2)
        b = -2 * current_thrust * cd
        c = (current_thrust**2 - (self.mass * self.g)**2) / ((self.rho/2) * self.s_ref)

        v_square = (-b + (b**2 - 4 * a * c)**0.5) / (2 * a)
        v = v_square**0.5

        # Annahme cd^2 = 0
        """v_square = (2 / (self.rho * self.s_ref * cl)) * ((self.mass * self.g)**2 - current_thrust**2)**0.5
        v = v_square ** 0.5"""

        print(f'rho = {self.rho}, s_ref = {self.s_ref}, g = {self.g}, cl = {cl},\n'
              f'v_square = {v_square}, velocity = {v}')

        return v, v_square                        # gibt als Tupel V und V^2 zurück

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
        gamma1 = math.degrees(np.arcsin(sin))
        if cos >= 1:
            gamma2 = 0
        else:
            gamma2 = math.degrees(np.arccos(cos))
        return gamma1, gamma2           # wird als Tupel übergeben

    def v_vertical(self, velocity, sin_gam):                # sin_gamma bereits vorher berechnen, ist übersichtlicher
        """
        Returns vertical velocity if velocity on flightpath and sinus(gamma) is given.
        """
        v_vert = velocity * sin_gam
        return v_vert

    # ---Iteration über Ca---

    def climb(self, cl_start, cl_end, cl_step: float = 0.1, v_tolerance: float = 1, it_max: int = 20):
        """
        cl_init should start around 0, so AVL can easily converge.
        Returns a numpy matrix with [cl, velocity, v_vertical, sin, cos, gamma (in degrees), current_thrust]
        in each row.
        """
        cl = cl_start
        climb_data = np.ndarray
        first_iteration = True
        velocity = (0, 0)
        while cl <= cl_end:
            print(f'##########################################################################')
            # AVL mit cl ausführen. -> cd_induced.
            geometry_and_mass_files.GeometryFile(self.plane).build_geometry_file(1)
            geometry_and_mass_files.MassFile(self.plane).build_mass_file()
            athenavortexlattice.AVL(self.plane).run_avl(lift_coefficient=cl)
            athenavortexlattice.AVL(self.plane).read_avl_output()

            # v_iteration_start aus Horizontalflug bestimmen
            if first_iteration:
                v_iteration = ((2 * self.mass * self.g) / (cl * self.rho * self.s_ref)) ** 0.5
                first_iteration = False
            # else:
            #     v_iteration = velocity[0]

            # Iteration über v -> über Re-Zahl cd_viscous ermitteln.
            current_thrust = float()
            cd = float()
            i = 0
            print(f'v_iteration = {v_iteration}, velocity = {velocity}')
            print(f'abs(v_it - velocity) = {abs(v_iteration - velocity[0])},'
                  f' v_tolerance = {v_tolerance}, iteration = {i}')
            not_in_tolerance = True
            print(f'not_in_tolerance: {not_in_tolerance}')

            while not_in_tolerance and i < it_max:
                print(f'---------------------------------------------------------------------')
                # ViscousDrag(self.plane).create_avl_viscous_drag_from_xfoil(velocity=v_iteration, alfa_step=1)
                cd = self.plane.aero_coeffs.drag_coeff.cd_viscous + self.plane.aero_coeffs.drag_coeff.cd_ind
                print(f'cd = {cd}, cd_viscous = {self.plane.aero_coeffs.drag_coeff.cd_viscous},'
                      f' cd_ind = {self.plane.aero_coeffs.drag_coeff.cd_ind}')
                current_thrust = GeneralFunctions(self.plane).current_thrust(v_iteration)
                print(f'current_thrust = {current_thrust}')
                velocity = self.v_climb(current_thrust, cl, cd)
                i += 1
                not_in_tolerance = abs(v_iteration - velocity[0]) >= v_tolerance
                print(f'v_iteration = {v_iteration}, velocity = {velocity}')
                print(f'abs(v_it - velocity) = {abs(v_iteration - velocity[0])},'
                      f' v_tolerance = {v_tolerance}, iteration = {i}')
                print(f'not_in_tolerance: {not_in_tolerance}')
                v_iteration = velocity[0]

            sin = self.sin_gamma(current_thrust, velocity[1], cd)
            print(f'sin = {sin}')
            cos = self.cos_gamma(velocity[1], cl)
            print(f'cos = {cos}')
            gamma = self.gamma(sin, cos)
            print(f'gamma = {gamma}')
            v_vertical = self.v_vertical(velocity[0], sin)
            print(f'v_vertical = {v_vertical}')

            results = np.array([cl, velocity[0], v_vertical, sin, cos, gamma[0], gamma[1], current_thrust])
            if cl == cl_start:
                climb_data = results
            else:
                climb_data = np.vstack((climb_data, results))
            print(f'climb_data = {climb_data}')
            cl += cl_step

        self.plane.flightconditions.climb.results.climb_data = climb_data
        self.steepest_climb()
        self.fastest_climb()
        return climb_data

    # ---Auswertung---

    def steepest_climb(self):
        # gamma maximal
        gamma_max = np.max(self.plane.flightconditions.climb.results.climb_data[:, 5])  # alle Zeilen, Element
        self.plane.flightconditions.climb.results.gamma_max = gamma_max
        return gamma_max

    def fastest_climb(self):
        # V_v maximal
        v_vertical_max = np.max(self.plane.flightconditions.climb.results.climb_data[:, 2])  # alle Zeilen, Element
        self.plane.flightconditions.climb.results.v_vertical_max = v_vertical_max
        return v_vertical_max

    def gained_heigth(self, time, *, v_vertical=None, cl=None, velocity=None, gamma=None):
        """
        Returns a gained height. Needs therefore a timespan and an additional value.
        """
        if v_vertical:
            v_v = v_vertical
        else:
            v_vertical_array = self.plane.flightconditions.climb.results.climb_data[:, 2]
            if cl:
                new_value = cl
                value_arr = self.plane.flightconditions.climb.results.climb_data[:, 0]
            elif velocity:
                new_value = velocity
                value_arr = self.plane.flightconditions.climb.results.climb_data[:, 1]
            elif gamma:
                new_value = gamma
                value_arr = self.plane.flightconditions.climb.results.climb_data[:, 5]
            else:
                return print("Please chose an argument and try again.")
            v_v = np.interp(new_value, value_arr, v_vertical_array)

        heigth = v_v * time
        return heigth

    def gained_distance(self, time, *, v_vertical=None, cl=None, velocity=None, gamma=None):
        """
        Returns a reached distance. Needs therefore a timespan and an additional value.
        """
        new_value = float()
        value_arr = np.array([])
        if velocity:
            v = velocity
        else:
            v_array = self.plane.flightconditions.climb.results.climb_data[:, 1]
            if cl:
                new_value = cl
                value_arr = self.plane.flightconditions.climb.results.climb_data[:, 0]
            elif v_vertical:
                new_value = v_vertical
                value_arr = self.plane.flightconditions.climb.results.climb_data[:, 2]
            elif gamma:
                new_value = gamma
                value_arr = self.plane.flightconditions.climb.results.climb_data[:, 5]
            else:
                return print("Please chose an argument and try again.")
            v = np.interp(new_value, value_arr, v_array)

        cos_gam_array = self.plane.flightconditions.climb.results.climb_data[:, 4]
        cos_gam = np.interp(new_value, value_arr, cos_gam_array)

        distance = v * cos_gam * time
        return distance


# --------------------------------
# ---Test---
# --------------------------------


"""if __name__ == "__main__":
    x = gamma(0.4, 0.2)
    print(x)"""
