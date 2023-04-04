import math
import numpy as np
from mace.aero.implementations.avl import athenavortexlattice, geometry_and_mass_files
from mace.aero.implementations.viscousdrag import ViscousDrag
from mace.domain import params, Plane


class GlidingFlight:
    def __init__(self, plane: Plane):
        self.plane = plane
        self.mass = self.plane.mass[0]
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho

    def v_gliding_flight(self, cd, cl):
        """
        Returns the velocity in gliding flight
        """
        v = ((2 * self.mass * self.g) / (self.rho * self.s_ref)) ** 0.5 * (cd ** 2 + cl ** 2) ** (-0.25)
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
        v_v = velocity ** 3 * ((-self.rho / 2) * self.s_ref * cd) / (self.mass * self.g)
        return v_v

    # ---Iteration über V---

    def v_glide_iteration(self, cl_end, cl_start=0.1, cl_step=0.1, velocity_tolerance=0.1, it_max=20):
        """
        Returns a 2D numpy matrix containing following data in each row:
        [cl, cd, cd_viscous, cd_induced, velocity, vertical_velocity]

        cl_start has to be higher than 0 because of calculation of viscous drag and AVL.
        cl_end has be be higher than cl_start.
        """
        gliding_data = np.array([])
        self.plane.aero_coeffs.drag_coeff.cd_viscous = 0

        num = cl_end - cl_start / cl_step
        for cl in np.linspace(cl_start, cl_end, num):
            # AVL -> cd_ind
            geometry_and_mass_files.GeometryFile(self.plane).build_geometry_file(
                self.plane.reference_values.number_of_surfaces)
            geometry_and_mass_files.MassFile(self.plane).build_mass_file()
            athenavortexlattice.AVL(self.plane).run_avl(lift_coefficient=cl)
            athenavortexlattice.AVL(self.plane).read_avl_output()
            # if Fehler:
            #     error = False

            # ViscousDrag -> cd_vis: Iteration: v_glidingflight ausrechnen, ViscousDrag, dann neu
            cd = self.plane.aero_coeffs.drag_coeff.cd_viscous + self.plane.aero_coeffs.drag_coeff.cd_ind
            velocity_init = self.v_gliding_flight(cd, cl)
            ViscousDrag(self.plane).create_avl_viscous_drag_from_xfoil(velocity=velocity_init)
            cd = self.plane.aero_coeffs.drag_coeff.cd_viscous + self.plane.aero_coeffs.drag_coeff.cd_ind
            velocity = self.v_gliding_flight(cd, cl)
            i = 0
            while abs(velocity_init - velocity) > velocity_tolerance or i >= it_max:
                velocity_init = velocity
                ViscousDrag(self.plane).create_avl_viscous_drag_from_xfoil(velocity=velocity_init)
                cd = self.plane.aero_coeffs.drag_coeff.cd_viscous + self.plane.aero_coeffs.drag_coeff.cd_ind
                velocity = self.v_gliding_flight(cd, cl)
                i += 1

            results = np.array([cl, cd, self.plane.aero_coeffs.drag_coeff.cd_viscous,
                                self.plane.aero_coeffs.drag_coeff.cd_ind, velocity, self.v_vertical(velocity, cd)])

            if cl == cl_start:
                gliding_data = results
            else:
                gliding_data = np.vstack((gliding_data, results))
        self.plane.flightconditions.glidingflight.results.gliding_data = gliding_data
        self.best_glide()
        self.smallest_decline()

        return gliding_data

    # ---Auswertung---
    def best_glide(self):
        """
        Returns the best glide ratio and saves the corresponding data in the object plane.
        """
        # noch checken, ob min oder max
        cd_divided_by_cl = self.plane.flightconditions.glidingflight.results.gliding_data[:, 1] / \
                           self.plane.flightconditions.glidingflight.results.gliding_data[:, 0]
        row_index = np.argmin(cd_divided_by_cl)
        best_glide_ratio = np.argmin(cd_divided_by_cl)
        corresponding_data = self.plane.flightconditions.glidingflight.results.gliding_data[row_index, :]

        self.plane.flightconditions.glidingflight.results.best_glide_ratio = best_glide_ratio
        self.plane.flightconditions.glidingflight.results.row_index_best_glide_ratio = row_index
        self.plane.flightconditions.glidingflight.results.data_best_glide_ratio = corresponding_data

        return best_glide_ratio

    def smallest_decline(self):
        """
        Returns the smallest decline and saves the corresponding data in the object plane.
        """
        smallest_decline = np.min(self.plane.flightconditions.glidingflight.results.gliding_data[:, 5])
        row_index = np.argmin(self.plane.flightconditions.glidingflight.results.gliding_data[:, 5])
        corresponding_data = self.plane.flightconditions.glidingflight.results.gliding_data[row_index, :]

        self.plane.flightconditions.glidingflight.results.smallest_decline = smallest_decline
        self.plane.flightconditions.glidingflight.results.row_index_smallest_decline = row_index
        self.plane.flightconditions.glidingflight.results.data_smallest_decline = corresponding_data

        return smallest_decline

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
        time = height / v_vertical
        return time

    def gliding_distance(self, v_glide, gamma, time):
        """
        Returns the gliding distance. Input gamma in degrees.
        """
        distance = v_glide * math.cos(math.radians(gamma)) * time
        return distance
