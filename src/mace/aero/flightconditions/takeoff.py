import math

import numpy as np

from mace.aero.generalfunctions import GeneralFunctions
from mace.aero.implementations.avl.athenavortexlattice import AVL

# import datatypes
# from mace.domain import params as par
# from mace.domain import plane as pl
from mace.domain import Plane, params


class Takeoff:
    def __init__(self, plane: Plane):
        self.plane = plane
        # AVL ausführen für Rollanstellwinkel -> cl_roll
        # AVL(self.plane).read_avl_output()
        self.mass = self.plane.mass
        self.lambda_k = self.plane.reference_values.lambd_k
        self.lambda_g = self.plane.reference_values.lambd_g
        self.h = self.plane.reference_values.h  # Höhe des FlügelNPs über Boden
        self.b = self.plane.reference_values.b  # Spannweite
        self.my = self.plane.flightconditions.takeoff.my  # Rollreibungskoeffizient
        self.delta_a()
        self.delta_a = self.plane.flightconditions.takeoff.delta_a
        logging.debug(self.delta_a)
        self.delta_w()
        self.delta_w = self.plane.flightconditions.takeoff.delta_w
        logging.debug(self.delta_w)
        self.cl_roll = (
            self.plane.aero_coeffs.lift_coeff.cl_roll
        )  # initialisieren mit höherer Geschwindigkeit, cl sollte sich ja nicht ändern
        logging.debug(self.cl_roll)
        self.beta_a(self.cl_roll)
        self.beta_a = self.plane.flightconditions.takeoff.beta_a
        logging.debug(self.beta_a)
        self.beta_w(self.cl_roll)
        self.beta_w = self.plane.flightconditions.takeoff.beta_w
        logging.debug(self.beta_w)
        self.phi_a()
        self.phi_a = self.plane.flightconditions.takeoff.phi_a
        logging.debug(self.phi_a)
        self.phi_w()
        self.phi_w = self.plane.flightconditions.takeoff.phi_w
        logging.debug(self.phi_w)

        """self.plane.propulsion.thrust[0, :]
        self.plane.propulsion.thrust[1, :]"""  # initialisieren

    # ---Strecken- und Zeitinkremente---

    def delta_x(
        self, v1, v2, f, w, r
    ):  # Masse, Start-, Endgeschwindigkeit, F(V), W(V), R(V)
        del_x = (self.mass[0] * (v2**2 - v1**2)) / (2 * (f - w - r))
        return del_x

    def delta_t(
        self, v1, v2, f, w, r
    ):  # Masse, Start-, Endgeschwindigkeit, F(V), W(V), R(V)
        del_t = (self.mass[0] * (v2 - v1)) / (f - w - r)
        return del_t

    def lift_rolling(self, current_velocity):
        """
        Returns the lift while given plane is rolling on the ground.
        """
        cl_roll = self.plane.aero_coeffs.lift_coeff.cl_roll
        lift = GeneralFunctions(self.plane).coefficient_to_lift_or_drag(
            current_velocity, cl_roll
        )
        return lift

    def drag_rolling_coefficient(self):
        """
        Returns the drag !coefficient! while given plane is rolling on the ground.
        """
        viscous_drag = self.plane.flightconditions.takeoff.cd_viscous
        # viscous_drag = self.plane.aero_coeffs.drag_coeff.cd_viscous
        induced_drag = self.plane.aero_coeffs.drag_coeff.cd_ind
        cd_roll = viscous_drag + induced_drag * self.phi_a**2 * self.phi_w
        logging.debug(f"cd_visc = {viscous_drag}, cd_ind = {induced_drag}, cd_roll = {cd_roll}")
        # cd_roll = cw_profil + cwi * phi_a**2 * phi_w
        return cd_roll

    def drag_rolling(self, current_velocity):
        """
        Returns the drag while given plane is rolling on the ground.
        """
        cd_roll = self.drag_rolling_coefficient()
        drag = GeneralFunctions(self.plane).coefficient_to_lift_or_drag(
            current_velocity, cd_roll
        )
        logging.debug(f"rolling_drag (profile) = {drag}")
        return drag

        # ---Reibung---

    def rollreibung(
        self, rolling_friction_coefficient, lift
    ):  # Rollreibungskoeffizient, aktueller Auftrieb
        """
        Returns the rolling friction dependent on the current lift.
        """
        gravitational_constant = params.Constants.g
        r = rolling_friction_coefficient * (
            self.mass[0] * gravitational_constant - lift
        )
        return r

    # ---Bodeneffekt---

    # delta (für elliptischen Flügel sind delta_a = delta_w = 1)
    def delta_a(self):  # Zuspitzung, Streckung
        """
        Calculates delta_a for a given wing layout.
        """
        delt = 1 - 2.25 * (self.lambda_k**0.00273 - 0.997) * (
            self.lambda_g**0.717 + 13.6
        )
        self.plane.flightconditions.takeoff.delta_a = delt
        # return delt

    def delta_w(self):  # Zuspitzung, Streckung
        """
        Calculates delta_w for a given wing layout.
        """
        delt = 1 - 0.157 * (self.lambda_k**0.775 - 0.373) * (
            self.lambda_g**0.417 + 1.27
        )
        self.plane.flightconditions.takeoff.delta_w = delt
        # return delt

    # beta
    def beta_a(self, cl):  # CA beim Rollen
        """
        Calculates beta_a for a given wing layout.
        """
        b_a = 1 + (
            (0.269 * cl**1.45) / (self.lambda_g**3.18 * (self.h / self.b) ** 1.12)
        )
        self.plane.flightconditions.takeoff.beta_a = b_a
        # return b_a

    def beta_w(self, cl):  # CA beim Rollen
        """
        Calculates beta_a for a given wing layout.
        """
        b_w = 1 + (
            (0.0361 * cl**1.21) / (self.lambda_g**1.19 * (self.h / self.b) ** 1.51)
        )
        self.plane.flightconditions.takeoff.beta_w = b_w
        # return b_w

    # phi (für elliptischen Flügel sind delta_a = delta_w = 1)
    def phi_a(
        self,
    ):  # beta_a, delta_a, Höhe des FlügelNP über Boden, Spannweite, Streckung
        """
        Calculates phi_a for a given wing layout.
        """
        phi = (1 / self.beta_a) * (
            1
            + self.delta_a
            * (288 * (self.h / self.b) ** 0.787)
            / (self.lambda_g**0.882)
            * math.exp(-9.14 * (self.h / self.b) ** 0.327)
        )
        self.plane.flightconditions.takeoff.phi_a = phi
        # return phi

    def phi_w(self):  # beta_w, delta_w, Höhe des FlügelNP über Boden, Spannweite
        """
        Calculates phi_w for a given wing layout.
        """
        phi = self.beta_w * (
            1
            - self.delta_w * math.exp(-4.74 * (self.h / self.b) ** 0.814)
            - (self.h / self.b) ** 2 * math.exp(-3.88 * (self.h / self.b) ** 0.758)
        )
        self.plane.flightconditions.takeoff.phi_w = phi
        # return phi

    # ---Ermittlung der Abhebegeschwindigkeit---

    def v_start(self, v_min):
        """
        Calculates the the takeoff velocity with influence of ground effect.
        """
        v_takeoff = v_min * (1 / self.phi_a) ** 0.5
        return v_takeoff

    # ---------------------------------------------
    # ---------------------------------------------

    def takeoff(self, v_min, step, v_timer_start=0):
        """
        Calculates rolling distance and rolling time or maximum rolling velocity for takeoff.
        """
        self.plane.flightconditions.takeoff.results.v_timer_start = v_timer_start
        self.plane.flightconditions.takeoff.results.rolling_distance = 0
        self.plane.flightconditions.takeoff.results.rolling_time = 0

        AVL(self.plane).run_avl(lift_coefficient=self.cl_roll)
        AVL(self.plane).read_avl_output()
        v_takeoff = self.v_start(v_min)
        v0 = 0
        num = int((v_takeoff - v0) // step)
        logging.debug(f"step = {step}, number of steps = {num}")
        logging.debug(f"v_array = {np.linspace(v0, v_takeoff, num + 1)}")
        for element in np.linspace(
            v0, v_takeoff, num + 1
        ):  # v0 = 0, v_start, Anzahl der Inkremente für Diskretisierung
            v1 = element
            v2 = element + (v_takeoff - v0) / num
            v = element + (v_takeoff - v0) / (
                2 * num
            )  # eventuell quadratisch mitteln -> rechts der Mitte

            logging.debug(f"current_velocity: {v}, v1 = {v1}, v2 = {v2}")
            f = GeneralFunctions(self.plane).current_thrust(v)

            # delta, beta und phi sind bereits in __init__ berechnet

            # AVL bei aktueller Geschwindigkeit durchlaufen lassen
            # eventuell noch viscous_drag, wenn Performance erhöht

            w = self.drag_rolling(v)  # Widerstand
            a = self.lift_rolling(v)  # Auftrieb
            r = self.rollreibung(self.my, a)  # Rollreibungswiderstand
            if r < 0:
                r = 0

            logging.debug(
                f"v1 = {v1}, v2 = {v2}, f = {f}, w = {w}, a = {a}, G = {9.81 * self.mass[0]},r = {r}"
            )
            logging.debug(f"delta_x = {self.delta_x(v1, v2, f, w, r)}")
            logging.debug(f"delta_x < 0 : {self.delta_x(v1, v2, f, w, r) <= 0}")

            if self.delta_x(v1, v2, f, w, r) <= 0:
                self.plane.flightconditions.takeoff.results.v_max_rolling = v1
                self.plane.flightconditions.takeoff.results.rolling_distance = False
                self.plane.flightconditions.takeoff.results.rolling_time = False
                return self.plane.flightconditions.takeoff.results

            self.plane.flightconditions.takeoff.results.rolling_distance += (
                self.delta_x(v1, v2, f, w, r)
            )
            logging.debug(
                f"current rolling_distance: {self.plane.flightconditions.takeoff.results.rolling_distance}"
            )
            if v1 > v_timer_start:
                self.plane.flightconditions.takeoff.results.rolling_time += (
                    self.delta_t(v1, v2, f, w, r)
                )
                logging.debug(
                    f"current rolling_time: {self.plane.flightconditions.takeoff.results.rolling_time}"
                )

        self.plane.flightconditions.takeoff.results.v_max_rolling = False
        return self.plane.flightconditions.takeoff.results
