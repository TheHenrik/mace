import math

import numpy as np
from mace.aero.implementations.avl import athenavortexlattice, geometry_and_mass_files
from mace.aero.implementations.viscousdrag import ViscousDrag
from mace.domain import params, Plane


class TurningFlight:
    def __init__(self, plane: Plane):
        self.plane = plane
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho

    # ---Kurvengeschwindigkeit---

    def velocity_turning_flight(self, cl, phi):
        """
        Returns the velocity of the plane during a horizontal turning flight.
        """
        v_k = ((2 * self.mass * self.g) / (self.rho * self.s_ref * cl * math.cos(phi)))**0.5
        return v_k

    def min_velocity_turning_flight(self, cl_max, phi):
        """
        Returns the minimum velocity of the plane during a horizontal turning flight.
        """
        v_k_min = self.velocity_turning_flight(cl_max, phi)
        return v_k_min

    # ---Kurvenradius---

    def turn_radius(self, *, v=None, r_k=None, cl=None, n=None, phi=None) -> (float, float, float, float, float):
        """This fuction recieves 2 input parameters (not n and phi, either or) and returns a tupel with all 5 turning flight defining parameters.
        (velocity, radius of turning flight, lift coefficient, load faktor, rolling angle, turning_velocity chi_dot)

        phi in degrees
        phi dot in degrees/s
        """
    # umschreiben zu z.B. if v is not None and r_k is not none:
        m = self.mass

        if v and r_k:                           # v, r_k
            n = ((v**2) / (self.g * r_k))**2 + 1
            phi = math.degrees(math.acos(1/n))
            cl = (2 * m) / (self.rho * self.s_ref * r_k * (1/n) * (n**2 - 1)**0.5)
            return v, r_k, cl, n, phi

        elif v and cl:                         # v, ca

            n = (cl * self.rho/2 * v**2 * self.s_ref) / (self.mass * self.g)
            phi = math.degrees(math.acos(1 / n))
            r_k = (v**2) / (self.g * (n**2 - 1)**0.5)
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif v and n:                         # v, n
            r_k = (v**2) / (self.g * (n**2 - 1)**0.5)
            phi = math.degrees(math.acos(1 / n))
            cl = (2 * m) / (self.rho * self.s_ref * r_k * (1 / n) * (n ** 2 - 1) ** 0.5)
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif v and phi:                         # v, phi
            n = 1 / math.cos(math.radians(phi))
            r_k = (v ** 2) / (self.g * (n ** 2 - 1) ** 0.5)
            cl = (2 * m) / (self.rho * self.s_ref * r_k * (1 / n) * (n ** 2 - 1) ** 0.5)
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif r_k and cl:                         # r_k, cl
            cos_phi = (1 - (2 * m) / (self.rho * self.s_ref * cl * r_k))**0.5
            phi = math.degrees(math.acos((1 - (2 * m) / (self.rho * self.s_ref * cl * r_k))**0.5))
            n = 1 / cos_phi
            v = (r_k / (self.g * ((1 / cos_phi)**2 - 1)**0.5))**0.5
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif r_k and n:                         # r_k, n
            v = (r_k / (self.g * (n**2 - 1)**0.5))**0.5
            phi = math.degrees(math.acos(1 / n))
            cl = (2 * m) / (self.rho * self.s_ref * r_k * (1 / n) * (n ** 2 - 1) ** 0.5)
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif r_k and phi:                         # r_k, phi
            n = 1 / math.cos(math.radians(phi))
            v = (r_k / (self.g * (n**2 - 1)**0.5))**0.5
            cl = (2 * m) / (self.rho * self.s_ref * r_k * (1 / n) * (n ** 2 - 1) ** 0.5)
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif cl and n:                         # cl, n
            phi = math.degrees(math.acos(1 / n))
            r_k = (2 * m) / (self.rho * self.s_ref * cl * (1 - (math.cos(math.radians(phi)))**2)**0.5)
            v = (r_k / (self.g * (n ** 2 - 1) ** 0.5)) ** 0.5
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif cl and phi:                         # cl, phi
            n = 1 / math.cos(math.radians(phi))
            r_k = (2 * m) / (self.rho * self.s_ref * cl * (1 - (math.cos(math.radians(phi))) ** 2) ** 0.5)
            v = (r_k / (self.g * (n ** 2 - 1) ** 0.5)) ** 0.5
            return v, r_k, cl, n, phi, self.turning_velocity(v, r_k)

        elif n and phi:                        # n, phi
            print("error: n and phi are too less arguments")

        else:
            print("error: wrong arguments")

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
            print("Bitte Parameter n oder phi ausfüllen.")
        elif n:
            phi = math.degrees(math.acos(1 / n))
        needed_thrust = cd/cl * (self.mass * self.g) / (math.cos(math.radians(phi)))
        return needed_thrust


# ---beschleunigte/abgebremste Kurve---


def ueberschusskraft_kurve(f, schubbedarf):
    ueberschuss = f - schubbedarf
    return ueberschuss


def delta_chi(f_ueberschuss, r_k, m, t, v_0):
    delta = f_ueberschuss / (2 * r_k * m) * t**2 + v_0 / r_k * t
    v_0_neu = f_ueberschuss / m * t + v_0
    return delta, v_0_neu


def delta_t(r_k, m, f_ueberschuss, v_0, chi_inkrement):
    delta = (r_k * m / f_ueberschuss) * (
                (v_0 / r_k) ** 2 + 2 * chi_inkrement * f_ueberschuss / (r_k * m) ** 0.5 - v_0 / r_k)
    v_0_neu = f_ueberschuss / m * delta + v_0
    return delta, v_0_neu


def kurve_beschleunigt(v_start, winkel, winkelinkrement):
    kurvendauer = 0
    v_aktuell = v_start
    for kurvenwinkel in np.linspace(0,winkel,winkelinkrement):
        delta_time = delta_t(r_k,m, f_ueberschuss,v_aktuell,chi_inkrement)
        kurvendauer += delta_time[1]
        v_aktuell = delta_time[2]
    v_ende = v_aktuell
    return v_ende, kurvendauer
