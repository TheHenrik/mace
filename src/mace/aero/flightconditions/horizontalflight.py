import numpy as np

from mace.domain import params, Plane
from mace.aero.implementations.avl import athenavortexlattice, geometry_and_mass_files
from mace.aero import generalfunctions
from mace.aero.implementations.viscousdrag import ViscousDrag


class HorizontalFlight:
    def __init__(self, plane: Plane):
        self.plane = plane
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho

    def flight_velocity(self, cl):
        velocity = ((2 * self.mass * self.g)/(cl * self.rho * self.s_ref))**0.5
        return velocity

    def lift_coefficient(self, velocity):
        cl = (2 * self.mass * self.g)/(velocity**2 * self.rho * self.s_ref)
        return cl

    def min_flight_velocity(self, cl_max):      # nicht wirklich nötig / identisch zu flight_velocity
        v_min = self.flight_velocity(cl_max)
        return v_min

    def thrust_supply(self, cd, cl):            # Schubbedarf
        thrust = cd / cl * self.mass * self.g
        return thrust

    def fv_diagramm(self, cl_start, cl_end, step=0.1):
        """
        cl_start has to be above 0. If not, no horizontal flight is possible.
        Returns an array with the correlation between velocity and needed thrust supply in horizontal flight.
        [[v1, t1], [v2, t2], [...], ...]
        """
        cl = cl_start

        results = np.array([])
        error = False

        while cl <= cl_end and error is False:

            # ---Widerstand ermitteln---
            # AVL mit cl ausführen. -> cd_induced.
            geometry_and_mass_files.GeometryFile(self.plane).build_geometry_file(
                self.plane.reference_values.number_of_surfaces)
            geometry_and_mass_files.MassFile(self.plane).build_mass_file()
            athenavortexlattice.AVL(self.plane).run_avl(lift_coefficient=cl)
            athenavortexlattice.AVL(self.plane).read_avl_output()
            # if Fehler:
            #     error = False

            # Fluggeschwindigkeit ermitteln
            velocity = self.flight_velocity(cl)

            # cd_viscous mit XFOIL ermitteln
            ViscousDrag(self.plane).create_avl_viscous_drag_from_xfoil()
            cd = self.plane.aero_coeffs.drag_coeff.cd_viscous + self.plane.aero_coeffs.drag_coeff.cd_ind
            # if Fehler:
            #     error = False

            # Calculate needed thrust for cl
            needed_thrust = self.thrust_supply(cd, cl)

            res = velocity, needed_thrust

            if cl == cl_start:
                results = res
            else:
                results = np.vstack((results, res))

            cl += step
        self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation = results
        self.plane.flightconditions.horizontalflight.results.minimum_thrust = self.min_thrust()
        if self.plane.propulsion.thrust is not None and not np.array([]):
            self.plane.flightconditions.horizontalflight.results.maximum_flight_velocity = self.max_flight_velocity()
        return results

    # ---Auswertung---

    def min_thrust(self):
        """
        Returns a tuple with (minimum thrust, corresponding velocity, row_index in thrust_velocity_correlation).
        """
        min_index = np.argmin(self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation[:, 1])
        minimum_thrust = self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation[min_index, 1]
        min_thrust_velocity = \
            self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation[min_index, 0]
        return minimum_thrust, min_thrust_velocity, min_index

    def max_flight_velocity(self):
        """
        Returns the point of max_flight_velocity as a tupel:
        (max_flight_velocity, thrust)
        """
        # von vorne nach hinten (schnell nach langsam) iterieren in thrust velocity correlation
        # propulsion.thrust nach v interpolieren
        # needed_thrust(v) mit propulsion.thrust vergleichen.
        # wenn kleiner (erst ab Element 2 ([1])), dann Schnittpunkt zwischen needed_thrust und propulsion.thrust
        length_of_array = len(self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation[:, 0])
        i = 0
        for row_index in range(length_of_array):
            velocity = self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation[row_index, 0]
            needed_thrust = \
                self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation[row_index, 1]
            thrust = generalfunctions.GeneralFunctions(self.plane).current_thrust(velocity)
            if needed_thrust <= thrust and i != 0:
                v_a1 = \
                    self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation[row_index - 1, 0]
                t_a1 = \
                    self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation[row_index - 1, 1]
                a1 = [v_a1, t_a1]
                v_a2 = velocity
                t_a2 = needed_thrust
                a2 = [v_a2, t_a2]
                # b1 und b2 in propulsion.thrust finden. Punkt1 velocity kleiner, Punkt2 velocity größer
                row_index_thrust = 0
                for row_index_thrust in range(len(self.plane.propulsion.thrust[:, 0])):    # v ansteigend
                    if self.plane.propulsion.thrust[row_index, 0] >= velocity and row_index_thrust != 0:
                        break
                    else:
                        continue
                v_b1 = self.plane.propulsion.thrust[row_index_thrust - 1, 0]
                t_b1 = self.plane.propulsion.thrust[row_index_thrust - 1, 1]
                b1 = [v_b1, t_b1]
                v_b2 = self.plane.propulsion.thrust[row_index_thrust, 0]
                t_b2 = self.plane.propulsion.thrust[row_index_thrust, 1]
                b2 = [v_b2, t_b2]
                point_of_intersection = generalfunctions.get_intersect(a1, a2, b1, b2)
                # max_velocity = np.array([point_of_intersection(0), point_of_intersection(1)])
                return point_of_intersection
            else:
                i += 0

    def flight_distance(self, velocity, time):
        distance = velocity * time
        return distance

    # ---Beschleunigung---

    def excess_power(self, cd, cl, thrust):
        excess_power = thrust - self.thrust_supply(cd, cl)
        return excess_power

    def delta_t(self, v2, v1, excess_power):
        del_t = self.mass / excess_power * (v2 - v1)
        return del_t

    def zwischenschritt(self, cl, thrust):
        # ---Widerstand ermitteln---
        # AVL mit cl ausführen. -> cd_induced.
        geometry_and_mass_files.GeometryFile(self.plane).build_geometry_file(
            self.plane.reference_values.number_of_surfaces)
        geometry_and_mass_files.MassFile(self.plane).build_mass_file()
        athenavortexlattice.AVL(self.plane).run_avl(lift_coefficient=cl)
        athenavortexlattice.AVL(self.plane).read_avl_output()
        # if Fehler:
        #     error = False

        # cd_viscous mit XFOIL ermitteln
        ViscousDrag(self.plane).create_avl_viscous_drag_from_xfoil()
        cd = self.plane.aero_coeffs.drag_coeff.cd_viscous + self.plane.aero_coeffs.drag_coeff.cd_ind
        # if Fehler:
        #     error = False

        # ---Calculating excess power---
        excess = self.excess_power(cd, cl, thrust)

        return cd, excess

    def beschleunigung(self, v_begin, v_end, v_step):
        time = 0
        distance = 0
        distance1 = 0
        distance2 = 0

        if v_begin < v_end:
            velocity = v_begin
            cl = self.lift_coefficient(velocity)
            thrust = generalfunctions.GeneralFunctions(self.plane).current_thrust(velocity)
            res = self.zwischenschritt(cl, thrust)
            excess = res[1]

            if excess < 0:
                print("error")
            else:
                while velocity <= v_end:
                    delta_t = self.delta_t(velocity + v_step, velocity, excess)
                    distance1 += delta_t * velocity
                    distance2 += delta_t * (velocity + v_step)
                    time += delta_t
                    velocity += v_step
                distance = (distance1 + distance2) / 2
                return time, distance
        elif v_end < v_begin:
            velocity = v_begin
            cl = self.lift_coefficient(velocity)
            thrust = generalfunctions.GeneralFunctions(self.plane).current_thrust(velocity)
            res = self.zwischenschritt(cl, thrust)
            excess = res[1]
            if excess > 0:
                print("error")
            else:
                while velocity <= v_end:
                    delta_t = self.delta_t(velocity + v_step, velocity, excess)
                    distance1 += delta_t * velocity
                    distance2 += delta_t * (velocity + v_step)
                    time += delta_t
                    velocity -= v_step
                distance = (distance1 + distance2) / 2
                return time, distance
        else:
            return time, distance
