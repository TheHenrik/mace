from mace.aero.implementations.avl import athenavortexlattice
from mace.aero import generalfunctions
from mace.aero.implementations.xfoil import xfoilpolars
from mace.domain import params, Plane
from mace.aero.implementations.avl.athenavortexlattice import AVL
import numpy as np


class ViscousDrag:
    def __init__(self, plane: Plane):
        self.plane = plane
        AVL(self.plane).read_avl_output()
        # self.s_ref = self.plane.avl.outputs.s_ref
        # self.number_of_surfaces = self.plane.avl.outputs.number_of_surfaces
        # self.surface_data = self.plane.avl.outputs.surface_data
        # matrix([number, chordwise-, spanwise-, first-strip], number_of_surfaces)
        """print(self.surface_data)
        print("Number of surface = {0}\n".format(self.surface_data[:, 0]))
        print("number of strips in chordwise direction = {0}\n".format(self.surface_data[:, 1]))
        print("number of strips in spanwise direction (important) = {0}\n".format(self.surface_data[:, 2]))
        print("surface begins with strip number = {0}\n".format(self.surface_data[:, 3]))"""
        # self.strip_forces = self.plane.avl.outputs.strip_forces

    def get_cl_min_of_surface(self):
        cl_min = np.min(self.plane.avl.outputs.strip_forces[6, :])    # (element, zeile)
        return cl_min

    def get_cl_max_of_surface(self):
        cl_max = np.max(self.plane.avl.outputs.strip_forces[6, :])    # (element, zeile)
        return cl_max

    def get_chord_min_of_surface(self):
        chord_min = np.min(self.plane.avl.outputs.strip_forces[4, :])    # (element, zeile)
        return chord_min    # außen sollte noch bedacht werden

    def get_chord_max_of_surface(self):
        chord_max = np.max(self.plane.avl.outputs.strip_forces[4, :])    # (element, zeile)
        return chord_max    # außen sollte noch bedacht werden

    def get_reynolds(self, length, cl):
        velocity = ((2 * self.plane.mass * params.Constants.g)/(cl * params.Constants.rho *
                                                                self.plane.avl.outputs.s_ref))**0.5
        reynolds = generalfunctions.get_reynolds_number(velocity, length)
        return reynolds

    def get_reynolds_step(self, reynolds_min, reynolds_max):
        reynolds_st = (reynolds_max - reynolds_min) / 4
        return reynolds_st

    def in_between_calculation_for_y_le_mac(self, yi, ya, li, la, y):
        result = 1/2 * (li + (li-la) * yi/(ya-yi)) * y**2 + 1/3 * (la-li)/(ya-yi) * y**3
        return result

    def get_y_le_mac(self, y_le_inner, y_le_outer, chord_inner, chord_outer, area):
        y_le_mac = 2/area * (self.in_between_calculation_for_y_le_mac(
            y_le_inner, y_le_outer, chord_inner, chord_outer, y_le_outer) -
            self.in_between_calculation_for_y_le_mac(y_le_inner, y_le_outer, chord_inner, chord_outer, y_le_inner))
        return y_le_mac

    def mach_strip_to_surface(self, strip):
        """
        returns surface_index, equals (number_of_surface - 1)
        """
        first_strip_of_surface = self.plane.avl.outputs.surface_data[:, 3]
        for surface_index in range(self.plane.avl.outputs.number_of_surfaces):
            if first_strip_of_surface[surface_index] < strip:
                continue
            else:
                return surface_index

    def create_avl_viscous_drag_from_xfoil(self):
        viscous_drag = np.array([])
        cl_min = self.get_cl_min_of_surface()                   # noch abrunden
        cl_max = self.get_cl_max_of_surface()                   # noch aufrunden
        chord_min = self.get_chord_min_of_surface()
        chord_max = self.get_chord_max_of_surface()
        reynolds_min = self.get_reynolds(chord_min, cl_min)     # noch abrunden
        reynolds_max = self.get_reynolds(chord_max, cl_max)     # noch aufrunden
        reynolds_steps = self.get_reynolds_step(reynolds_min, reynolds_max)
        inner_airfoil = None
        outer_airfoil = None
        alfa_start = [0, 0]
        alfa_end = [0, 0]
        alfa_step = 1

        # ---Calculation of alfa_start and alfa_end---
        for airfoil in [inner_airfoil, outer_airfoil]:
            i = 0
            cl_of_alfa_zero = xfoilpolars.get_xfoil_polar(airfoil, reynolds_min, alfa=0)[1]
            if cl_min < cl_of_alfa_zero:
                cl_dif_neg = cl_of_alfa_zero - cl_min
                alfa_start[i] = -0.11 / cl_dif_neg - 2     # Auftriebsabfall = 0.11 /Grad - Reserve
            else:
                alfa_start[i] = 0                          # für bessere Konvergenz
            cl_dif = cl_max - cl_of_alfa_zero
            alfa_end[i] = 0.11/cl_dif + 2                  # Auftriebsanstieg = 0.11 /Grad + Reserve
            i += 1

        # ---Polar calculations---

        i = 0
        inner_polar = []
        outer_polar = []
        list_of_reynolds = range(reynolds_min, reynolds_max, reynolds_steps)
        for reynolds in list_of_reynolds:
            inner_polar[i] = xfoilpolars.get_xfoil_polar(inner_airfoil, reynolds,
                                                         alfa_start=alfa_start, alfa_end=alfa_end, alfa_step=alfa_step)
            outer_polar[i] = xfoilpolars.get_xfoil_polar(outer_airfoil, reynolds,
                                                         alfa_start=alfa_start, alfa_end=alfa_end, alfa_step=alfa_step)
            # oder:
            """inner_polar[i] = xfoilpolars.get_xfoil_polar(inner_airfoil, reynolds,
                                                         cl_start=cl_min, cl_end=cl_max)
            outer_polar[i] = xfoilpolars.get_xfoil_polar(outer_airfoil, reynolds,
                                                         cl_start=cl_min, cl_end=cl_max)"""
            i += 1

        strips = self.plane.avl.outputs.strip_forces[0, :]
        for element in strips:
            surface_index = self.mach_strip_to_surface(element)
            strip_values = self.plane.avl.outputs.strip_forces[:, element-1]

            if element == strips[-1]:
                strip_values_outer = self.plane.avl.outputs.strip_forces[:, element]
            else:
                strip_values_outer = None

            chord = strip_values[4]
            local_cl = strip_values[6]
            local_reynolds = self.get_reynolds(chord, local_cl)

            # interpolate polar for inner_airfoil (with local_reynolds)
            new_inner_polar = np.interp(local_reynolds, list_of_reynolds, inner_polar)
            #       interpolate cd for given cl for inner_airfoil
            cd_new_inner = np.interp(local_cl, new_inner_polar[1, :], new_inner_polar[2, :])  # cl_new, cl, cd
            # interpolate polar for outer_airfoil (with local_reynolds)
            new_outer_polar = np.interp(local_reynolds, list_of_reynolds, outer_polar)
            #       interpolate cd for given cl for outer_airfoil
            cd_new_outer = np.interp(local_cl, new_outer_polar[1, :], new_outer_polar[2, :])  # cl_new, cl, cd

            # interpolate profile_cd for position between inner and outer strip.
            y_le_inner = strip_values[2]
            chord_inner = strip_values[4]
            if strip_values_outer is None:
                y_le_outer = self.plane.wing.segments[surface_index].nose_outer[0]
                chord_outer = self.plane.wing.segments[surface_index].chord_outer
            else:
                y_le_outer = strip_values_outer[2]
                chord_outer = strip_values_outer[4]
            # --- Calculation of y_l_my at Mean Aerodynamic Chord (MAC) of trapezial strip ---
            area = strip_values[5]
            y_le_mac = self.get_y_le_mac(y_le_inner, y_le_outer, chord_inner, chord_outer, area)
            interp = np.array([y_le_inner, y_le_outer])
            cd_list = np.array([cd_new_inner, cd_new_outer])
            cd_local = np.interp(y_le_mac, interp, cd_list)

            # adapt profile_cd to s_ref with CD = profile_cd*strip_area/s_ref
            cd_local_to_global = cd_local * area / self.plane.avl.outputs.s_ref

            # check to wich surface strip is located
            first_strip_of_surface = self.plane.avl.outputs.surface_data[:, 3]
            for surface in range(self.plane.avl.outputs.number_of_surfaces):
                if first_strip_of_surface[surface] < element:
                    continue
                else:
                    viscous_drag[surface] += cd_local_to_global

            overall_viscous_drag = sum(viscous_drag)

            return overall_viscous_drag, viscous_drag


# Tests: veränderung der Größe des viskosen Widerstandes mit Erhöhung von Stripanzahl untersuchen.
# -> Validierung der Software
