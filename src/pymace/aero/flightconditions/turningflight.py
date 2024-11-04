import logging
import math

import numpy as np

from pymace.aero import generalfunctions

# from mace.aero.implementations.avl import athenavortexlattice, geometry_and_mass_files
# from mace.aero.implementations.viscousdrag import ViscousDrag
from pymace.domain import Plane, params


class TurningFlight:
    def __init__(self, plane: Plane):
        self.plane = plane
        self.mass = self.plane.mass[0]
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho

    # ---Kurvengeschwindigkeit---

    def velocity_turning_flight(self, cl, phi):
        """
        Returns the velocity of the plane during a horizontal turning flight
        phi in degrees.
        """
        v_k = (
            (2 * self.mass * self.g)
            / (self.rho * self.s_ref * cl * math.cos(math.radians(phi)))
        ) ** 0.5
        return v_k

    def cl_turning_flight(self, velocity, phi):
        """
        Returns the lift_coefficient of the plane during a horizontal turning flight.
        phi in degrees.
        """
        cl = (2 * self.mass * self.g) / (
            self.rho * self.s_ref * velocity**2 * math.cos(math.radians(phi))
        )
        return cl

    def min_velocity_turning_flight(self, cl_max, phi):
        """
        Returns the minimum velocity of the plane during a horizontal turning flight.
        phi in degrees
        """
        v_k_min = self.velocity_turning_flight(cl_max, phi)
        return v_k_min

    # ---Kurvenradius---

    def turn_radius(
        self, *, v=None, r_k=None, cl=None, n=None, phi=None
    ) -> (float, float, float, float, float):
        """This fucntion recieves 2 input parameters (not n and phi, either or) and returns a tupel with all 5 turning
        flight defining parameters.
        (velocity, radius of turning flight, lift coefficient, load faktor, rolling angle, turning_velocity chi_dot)

        phi in degrees
        phi dot in degrees/s
        """
        # umschreiben zu z.B. if v is not None and r_k is not none:
        m = self.mass

        if v and r_k:  # v, r_k
            n = ((v**2) / (self.g * r_k)) ** 2 + 1
            phi = math.degrees(math.acos(1 / n))
            cl = (2 * m) / (self.rho * self.s_ref * r_k * (1 / n) * (n**2 - 1) ** 0.5)
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif v and cl:  # v, ca
            n = (cl * self.rho / 2 * v**2 * self.s_ref) / (self.mass * self.g)
            logging.debug(f"n = {n}")
            phi = math.degrees(math.acos(1 / n))
            r_k = (v**2) / (self.g * (n**2 - 1) ** 0.5)
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif v and n:  # v, n
            r_k = (v**2) / (self.g * (n**2 - 1) ** 0.5)
            phi = math.degrees(math.acos(1 / n))
            cl = (2 * m) / (self.rho * self.s_ref * r_k * (1 / n) * (n**2 - 1) ** 0.5)
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif v and phi:  # v, phi
            n = 1 / math.cos(math.radians(phi))
            r_k = (v**2) / (self.g * (n**2 - 1) ** 0.5)
            cl = (2 * m) / (self.rho * self.s_ref * r_k * (1 / n) * (n**2 - 1) ** 0.5)
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif r_k and cl:  # r_k, cl
            cos_phi = (1 - (2 * m) / (self.rho * self.s_ref * cl * r_k)) ** 0.5
            phi = math.degrees(
                math.acos((1 - (2 * m) / (self.rho * self.s_ref * cl * r_k)) ** 0.5)
            )
            n = 1 / cos_phi
            v = (r_k / (self.g * ((1 / cos_phi) ** 2 - 1) ** 0.5)) ** 0.5
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif r_k and n:  # r_k, n
            v = (r_k / (self.g * (n**2 - 1) ** 0.5)) ** 0.5
            phi = math.degrees(math.acos(1 / n))
            cl = (2 * m) / (self.rho * self.s_ref * r_k * (1 / n) * (n**2 - 1) ** 0.5)
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif r_k and phi:  # r_k, phi
            n = 1 / math.cos(math.radians(phi))
            v = (r_k / (self.g * (n**2 - 1) ** 0.5)) ** 0.5
            cl = (2 * m) / (self.rho * self.s_ref * r_k * (1 / n) * (n**2 - 1) ** 0.5)
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif cl and n:  # cl, n
            phi = math.degrees(math.acos(1 / n))
            r_k = (2 * m) / (
                self.rho
                * self.s_ref
                * cl
                * (1 - (math.cos(math.radians(phi))) ** 2) ** 0.5
            )
            v = (r_k / (self.g * (n**2 - 1) ** 0.5)) ** 0.5
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif cl and phi:  # cl, phi
            n = 1 / math.cos(math.radians(phi))
            r_k = (2 * m) / (
                self.rho
                * self.s_ref
                * cl
                * (1 - (math.cos(math.radians(phi))) ** 2) ** 0.5
            )
            v = (r_k / (self.g * (n**2 - 1) ** 0.5)) ** 0.5
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif n and phi:  # n, phi
            logging.error("error: n and phi are too less arguments")

        else:
            logging.error("error: wrong arguments")

    # ---Wendegeschwindigkeit und Wendedauer---

    def turning_velocity(self, velocity, turn_radius):
        """
        Returns the turning velocity chi dot in degrees/s
        Needs the velocity of the plane and the turn radius.
        """
        chi_punkt = math.degrees(velocity / turn_radius)
        return chi_punkt

    def turning_time(self, angle, turning_velocity):
        """
        angle in degrees
        turning velocity in degrees/s
        """
        time = angle / turning_velocity
        return time

    # def wendegeschwindigkeit2(v, g, rho, m, s_ref, ca):
    # chi_punkt = (g * (((ca * rho/2 * v**2 *s_ref) / (m * g))**2 - 1)**0.5) / (v)
    # return chi_punkt

    # ---Schubbedarf für stationäre Kurve___

    def needed_thrust_for_turn(self, cd, cl, *, n=None, phi=None):
        """
        Returns needed thrust for a specified turning flight.
        Input cd, cl and n or phi (in degrees).
        phi in degrees
        """
        if n is None and phi is None:
            logging.warning("Bitte Parameter n oder phi ausfüllen.")
        elif n:
            phi = math.degrees(math.acos(1 / n))
        needed_thrust = cd / cl * (self.mass * self.g) / (math.cos(math.radians(phi)))
        return needed_thrust

    # ---beschleunigte/abgebremste Kurve---

    def delta_chi(self, excess_power, r_k, time, v_0):
        delta = excess_power / (2 * r_k * self.mass) * time**2 + v_0 / r_k * time
        v_0_neu = excess_power / self.mass * time + v_0
        return delta, v_0_neu

    def delta_t(self, r_k, excess_power, v_0, chi_inkrement):
        """
        chi_increment in degrees
        """
        delta = (r_k * self.mass / excess_power) * (
            (
                (v_0 / r_k) ** 2
                + 2 * math.radians(chi_inkrement) * excess_power / (r_k * self.mass)
            )
            ** 0.5
            - v_0 / r_k
        )
        logging.debug(f"delta = {delta},")
        v_0_neu = excess_power / self.mass * delta + v_0
        return delta, v_0_neu

    def turn_acceleration(
        self,
        v_start,
        turn_angle,
        chi_inkrement,
        *,
        lift_coefficient=None,
        turn_radius=None,
        phi=None,
        load_factor=None,
    ):
        """
        Returns the velocity at the end of the turn, the duration of the turn and the flight distance in a tuple.
        Needs the velocity at the bigin of the turn, the turn angle, the increment/step_size
        and a constant lift coefficient, a constant turn radius, or a constant rolling angle or load factor.
        chi_increment and turn angle in degrees
        """
        duration = 0
        distance1 = 0
        distance2 = 0
        logging.debug(f"v_start = {v_start}")
        current_velocity = v_start
        logging.debug(f"velocity = {current_velocity}")
        cl = float()
        r_k = float()
        number_of_steps = int((turn_angle // chi_inkrement) + 1)
        for angle in np.linspace(0, turn_angle, number_of_steps):
            thrust = generalfunctions.GeneralFunctions(self.plane).current_thrust(
                current_velocity
            )
            if lift_coefficient:
                cl = lift_coefficient
                r_k = self.turn_radius(v=current_velocity, cl=cl)
            if turn_radius:
                logging.debug(
                    f"velocity = {current_velocity}, turn_radius = {turn_radius}"
                )
                cl = self.turn_radius(v=current_velocity, r_k=turn_radius)[2]
                r_k = turn_radius
            elif phi:
                cl = self.turn_radius(v=current_velocity, phi=phi)[2]
                r_k = self.turn_radius(v=current_velocity, phi=phi)
            elif load_factor:
                cl = self.turn_radius(v=current_velocity, n=load_factor)[2]
                r_k = self.turn_radius(v=current_velocity, n=load_factor)
            else:
                logging.error("Error, too less arguments.")
            # drag estimation
            cd = generalfunctions.GeneralFunctions(self.plane).calcualate_drag(
                cl, velocity=current_velocity
            )

            logging.debug(f"cd = {cd}, cl = {cl}, thrust = {thrust}")
            excess_power = generalfunctions.GeneralFunctions(self.plane).excess_power(
                cd, cl, thrust
            )
            logging.debug(f"excess_power = {excess_power}")
            delta_time = self.delta_t(
                r_k, excess_power, current_velocity, chi_inkrement
            )
            duration += delta_time[0]
            distance1 += delta_time[0] * current_velocity
            logging.debug(f"velocity = {current_velocity}")
            current_velocity = delta_time[1]
            logging.debug(f"velocity = {current_velocity}")
            distance2 += delta_time[0] * current_velocity
        distance = (distance1 + distance2) / 2
        finish_velocity = current_velocity
        return finish_velocity, duration, distance
