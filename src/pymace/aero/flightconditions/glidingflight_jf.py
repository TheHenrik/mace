import math

import numpy as np

from pymace.aero.implementations.aero import Aerodynamics
from pymace.domain import params
from pymace.domain.vehicle import Vehicle


class GlidingFlight:
    def __init__(self, plane: Vehicle):
        self.plane = plane
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho

        self.cl_start = 0.1
        self.cl_end = 1.0
        self.cl_step = 0.1
        self.max_number_of_iterations = 20
        self.velocity_tolerance = 0.1

        self.results = None

        self.aero = Aerodynamics(self.plane)
        self.flap_angle = 0.0

    def v_gliding_flight(self, cd, cl):
        """
        Returns the velocity in gliding flight
        """
        v = ((2 * self.mass * self.g) / (self.rho * self.s_ref)) ** 0.5 * (
            cd**2 + cl**2
        ) ** (-0.25)
        return v

    def gamma(self, cd, cl):
        """
        Returns the gliding angle for gliding flight in a tuple:
        (degrees, radians)
        """
        gam = math.atan(-cd / cl)
        gam_deg = math.degrees(gam)
        return gam_deg, gam

    def v_vertical(self, velocity, cd):
        """
        Returns the vertical velocity for gliding flight
        """
        v_v = velocity**3 * ((-self.rho / 2) * self.s_ref * cd) / (self.mass * self.g)
        return v_v

    def evaluate(self):
        gliding_data = np.array([])

        CL_list = np.arange(self.cl_start, self.cl_end + self.cl_step, self.cl_step)

        for i, CL in enumerate(CL_list):
            # AVL -> cd_ind
            if i == 0:
                V_old = self.v_gliding_flight(CL / 20, CL)
            else:
                V_old = V_new

            self.aero.evaluate(CL=CL, V=V_old, FLAP=self.flap_angle)
            CD = self.plane.aero_coeffs.drag_coeff.cd_tot
            V_new = self.v_gliding_flight(CD, CL)

            i = 0
            while (
                abs(V_old - V_new) > self.velocity_tolerance
                or i >= self.max_number_of_iterations
            ):
                V_old = V_new
                self.aero.evaluate(CL=CL, V=V_old, FLAP=self.flap_angle)
                CD = self.plane.aero_coeffs.drag_coeff.cd_tot
                V_new = self.v_gliding_flight(CD, CL)
                i += 1

            gamma = self.gamma(CD, CL)[0]

            results = np.array([CL, CD, V_old, self.v_vertical(V_old, CD), gamma])

            if i == 0:
                gliding_data = results
            else:
                gliding_data = np.vstack((gliding_data, results))

        self.results = gliding_data

        return gliding_data

    def lost_height(self, v_vertical, time):
        """
        Returns the lost height.
        """
        h = v_vertical * time
        return h

    def gliding_time(self, height, v_vertical):
        """
        Returns the gliding time.
        """
        time = height / -v_vertical
        return time

    def gliding_distance(self, v_glide, gamma, time):
        """
        Returns the gliding distance. Input gamma in degrees.
        """
        distance = v_glide * math.cos(math.radians(gamma)) * time
        return distance

    def get_glide_time(self, height):
        if self.results is None:
            results = self.evaluate()
        else:
            results = self.results
        v_vertical_min = np.min(results[:, 3])
        time = self.gliding_time(height, v_vertical_min)
        return time
