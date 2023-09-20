# import takeoff as to
import numpy as np

from mace.aero.flightconditions.takeoff import Takeoff
from mace.aero.generalfunctions import GeneralFunctions
from mace.domain import Plane, params


class Landing:
    def __init__(self, plane: Plane):
        self.plane = plane
        # AVL ausführen für Rollanstellwinkel -> cl_roll
        # AVL(self.plane).read_avl_output()
        self.mass = self.plane.mass
        self.lambda_k = self.plane.reference_values.lambd_k
        self.lambda_g = self.plane.reference_values.lambd_g
        self.h = self.plane.reference_values.h  # Höhe des FlügelNPs über Boden
        self.b = self.plane.reference_values.b  # Spannweite
        self.my = ...  # Rollreibungskoeffizient
        Takeoff(self.plane)
        self.delta_a = self.plane.flightconditions.takeoff.delta_a
        self.delta_w = self.plane.flightconditions.takeoff.delta_w
        self.cl_roll = (
            ...
        )  # initialisieren mit höherer Geschwindigkeit, cl sollte sich ja nicht ändern
        self.beta_a = self.plane.flightconditions.takeoff.beta_a
        self.beta_w = self.plane.flightconditions.takeoff.beta_w
        self.phi_a = self.plane.flightconditions.takeoff.phi_a
        self.phi_w = self.plane.flightconditions.takeoff.phi_w

    def landing(self, v_touchdown, num, v_timer_end=0):
        """
        Calculates rolling distance and rolling time or maximum rolling velocity for takeoff.
        """
        self.plane.flightconditions.takeoff.results.v_timer_start = v_timer_end
        self.plane.flightconditions.takeoff.results.rolling_distance = 0
        self.plane.flightconditions.takeoff.results.rolling_time = 0

        # calculate v_touchdown

        v0 = 0
        for element in np.linspace(
            v_touchdown, v0, num
        ):  # v0 = 0, v_start, Anzahl der Inkremente für Diskretisierung
            v1 = element
            v2 = element - (v_touchdown - v0) / (num - 1)
            v = element + (v_touchdown - v0) / (
                2 * (num - 1)
            )  # eventuell quadratisch mitteln -> rechts der Mitte

            # f = GeneralFunctions(self.plane).current_thrust(v)

            # delta, beta und phi sind bereits in __init__ berechnet

            # AVL bei aktueller Geschwindigkeit durchlaufen lassen
            w = Takeoff(self.plane).drag_rolling(v)  # Widerstand
            a = Takeoff(self.plane).lift_rolling(v)  # Auftrieb
            r = Takeoff(self.plane).rollreibung(self.my, a)  # Rollreibungswiderstand

            if Takeoff(self.plane).delta_x(v1, v2, 0, w, r) <= 0:  # thrust = 0
                self.plane.flightconditions.takeoff.results.v_max_rolling = v1
                self.plane.flightconditions.takeoff.results.rolling_distance = False
                self.plane.flightconditions.takeoff.results.rolling_time = False
                return self.plane.flightconditions.takeoff.results

            self.plane.flightconditions.takeoff.results.rolling_distance += (
                self.delta_x(v1, v2, f, w, r)
            )
            if v1 > v_timer_start:
                self.plane.flightconditions.takeoff.results.rolling_time += (
                    self.delta_t(v1, v2, f, w, r)
                )

        self.plane.flightconditions.takeoff.results.v_max_rolling = False
        return self.plane.flightconditions.takeoff.results
