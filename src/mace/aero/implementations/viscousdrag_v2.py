import numpy.ma

from mace.aero.implementations.avl import athenavortexlattice
from mace.aero import generalfunctions
from mace.aero.implementations.xfoil import xfoilpolars
from mace.domain import params, Plane
from mace.aero.implementations.avl.athenavortexlattice import AVL
import numpy as np
import math
from mace.domain.parser import PlaneParser
from mace.aero.implementations.avl.geometry_and_mass_files import GeometryFile, MassFile
from pathlib import Path
import os


class ViscousDrag:
    def __init__(self, plane: Plane):
        self.plane = plane


    def get_reynolds(self, cl_global):
        velocity = ((2 * self.plane.mass[0] * params.Constants.g) / (cl_global * params.Constants.rho *
                                                                     self.plane.avl.outputs.s_ref)) ** 0.5
        reynolds = generalfunctions.get_reynolds_number(velocity, self.plane.avl.outputs.c_ref)
        return reynolds

    def get_local_reynolds(self, cl_global, local_chord_length):
        global_reynolds = self.get_reynolds(cl_global)
        local_reynolds = local_chord_length / self.plane.avl.outputs.c_ref * global_reynolds
        return local_reynolds

    def get_reynolds_step(self, reynolds_min, reynolds_max):
        reynolds_st = (reynolds_max - reynolds_min) / 8
        return reynolds_st

    def in_between_calculation_for_y_le_mac(self, yi, ya, li, la, y):
        result = 1 / 2 * (li + (li - la) * yi / (ya - yi)) * y ** 2 + 1 / 3 * (la - li) / (ya - yi) * y ** 3
        return result

    def get_y_le_mac(self, y_le_inner, y_le_outer, chord_inner, chord_outer, area):
        y_le_mac = 2 / area * (self.in_between_calculation_for_y_le_mac(
            y_le_inner, y_le_outer, chord_inner, chord_outer, y_le_outer) -
                               self.in_between_calculation_for_y_le_mac(y_le_inner, y_le_outer, chord_inner,
                                                                        chord_outer, y_le_inner))
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

    def create_avl_viscous_drag_from_xfoil(self, *, velocity=None, alfa_step=1):
        """
        This is written for stationary horizontal flight.
        For other velocities please intput them. The function will compare it with horizontal flight and
        will use an optimized reynoldsnumber. (Therefore cl has to be higher than 0.)
        """
        tool_path = Path(__file__).resolve().parents[4]
        logfile_path = os.path.join(tool_path, "temporary", "logfile.txt")

        logfile = open(logfile_path, 'w')
        cd_local_to_global = 0
        viscous_drag = np.zeros(self.plane.avl.outputs.number_of_surfaces)
        overall_viscous_drag = 0
        area_for_reference = 0
        cl_global = self.plane.aero_coeffs.lift_coeff.cl_tot
        logfile.write(f'cl_global ={cl_global}\n')
        # Compare v_horizontal with new velocity
        if velocity is None:
            v_factor = 1
            logfile.write(f'v_factor = {v_factor}\n')
        else:
            v_horizontal = ((2 * self.mass[0] * self.g) / (cl_global * self.rho * self.s_ref)) ** 0.5
            v_factor = velocity / v_horizontal
            logfile.write(f'v_horizontal = {v_horizontal}, v_factor = {v_factor}\n')

        for surface in range(1, self.plane.avl.outputs.number_of_surfaces + 1):  # 1, 2, 3, ... , last surface
            surface_original = surface
            if surface % 2 == 0:
                surface -= 1
            logfile.write(f'original_surface = {surface_original}, using surface: {surface}\n')
            cl_min = math.floor(self.get_cl_min_of_surface(surface) * 10) / 10  # abgerundet [0.1]
            cl_max = math.ceil(self.get_cl_max_of_surface(surface) * 10) / 10  # aufgerundet [0.1]
            chord_min = math.floor(self.get_chord_min_of_surface(surface) * 1000) / 1000  # abgerundet [mm]
            chord_max = math.ceil(self.get_chord_max_of_surface(surface) * 1000) / 1000  # aufgerundet [mm]
            logfile.write(f'cl_min = {cl_min}, cl_max = {cl_max}, chord_min = {chord_min}, chord_max = {chord_max}\n')
            reynolds_min = math.floor((v_factor * self.get_local_reynolds(cl_global, chord_min)) / 10000) * 10000
            # abgerundet auf 1000 [integer]
            logfile.write(f'reynolds_min = {reynolds_min}\n')
            reynolds_max = math.ceil(
                (v_factor * self.get_local_reynolds(cl_global, chord_max)) / 10000) * 10000  # aufgerundet [integer]
            logfile.write(f'reynolds_max = {reynolds_max}\n')
            reynolds_steps = math.ceil(self.get_reynolds_step(reynolds_min, reynolds_max))  # aufgerundet [integer]
            logfile.write(f'reynolds_steps = {reynolds_steps}\n')

            list_index = int()
            number_of_wing_segments_per_halfspan = len(self.plane.wing.segments)
            logfile.write(f'number of wing segments per halfspan: {number_of_wing_segments_per_halfspan}\n')
            if surface > number_of_wing_segments_per_halfspan * 2:
                pass  # skip to empennage, implemented later
            elif surface % 2 != 0:  # right wing
                logfile.write(f'right wing\n')
                list_index = int((surface - 1) / 2)
            elif surface % 2 == 0:  # left wing
                logfile.write(f'left wing\n')
                list_index = int(surface / 2)

            # hier noch unterscheiden zwischen Naca und nicht Naca
            inner_airfoil = self.plane.wing.segments[list_index].inner_airfoil.type.filepath
            outer_airfoil = self.plane.wing.segments[list_index].outer_airfoil.type.filepath

            alfa_min = [0, 0]  # [inner_airfoil, outer_airfoil]
            alfa_max = [0, 0]  # [inner_airfoil, outer_airfoil]
            # alfa_step = 1
            reserve = 0  # degrees
            cl_below_zero = False
            logfile.write(f'inner_airfoil: {inner_airfoil}, outer_airfoil: {outer_airfoil}\n')
            # ---Calculation of alfa_start and alfa_end---
            i = 0
            for airfoil in [inner_airfoil, outer_airfoil]:
                cl_of_alfa_zero = xfoilpolars.get_xfoil_polar(airfoil, reynolds_min, alfa=0)[1]
                logfile.write(f'cl_of_alfa_zero (profile) = {cl_of_alfa_zero}\n')
                # Auftriebsanstieg: cl = 0.11 * alfa[Grad]
                logfile.write(f'cl_min of wing = {cl_min}\n')
                logfile.write(f'cl_min of wing < cl_of_alfa_zero = {cl_min < cl_of_alfa_zero}\n')
                if cl_min < cl_of_alfa_zero:  # derzeit noch nicht einsatzbereit
                    cl_below_zero = True
                    cl_dif_neg = cl_of_alfa_zero - cl_min
                    alfa_min[i] = -math.ceil(cl_dif_neg / 0.11 + reserve)  # Auftriebsabfall = 0.11 /Grad - Reserve
                else:
                    alfa_min[i] = 0  # für bessere Konvergenz
                cl_dif = cl_max - cl_of_alfa_zero
                alfa_max[i] = math.ceil(cl_dif / 0.11 + reserve)  # Auftriebsanstieg = 0.11 /Grad + Reserve
                i += 1
            logfile.write(f'alfa_min = {alfa_min}, alfa_max = {alfa_max}, alfa_step = {alfa_step}\n')

            # ---Polar calculations---

            inner_polar = np.ndarray
            outer_polar = np.ndarray
            # list_of_reynolds = range(reynolds_min, reynolds_max, reynolds_steps)
            list_of_reynolds = np.linspace(reynolds_min, reynolds_max, 5)
            first_iteration = True
            logfile.write(f'alfa_min = {alfa_min}, alfa_max = {alfa_max}, alfa_step = {alfa_step}\n')
            logfile.write(f'list_of_reynolds = {list_of_reynolds}\n')
            for reynolds in list_of_reynolds:
                logfile.write(f'reynolds: {reynolds}\n')
                if first_iteration:
                    inner_polar = xfoilpolars.get_xfoil_polar(inner_airfoil, reynolds,
                                                              alfa_start=0, alfa_end=alfa_max[0],
                                                              alfa_step=alfa_step)
                    logfile.write(f'inner_polar: {inner_polar}\n')
                    if cl_below_zero:
                        inner_polar_below_zero = xfoilpolars.get_xfoil_polar(inner_airfoil, reynolds,
                                                                             alfa_start=0, alfa_end=alfa_min[0],
                                                                             alfa_step=alfa_step)
                        logfile.write(f'inner_polar_below_zero: {inner_polar_below_zero}\n')
                        inner_polar = np.vstack((inner_polar, inner_polar_below_zero))
                        logfile.write(f'inner_polar: {inner_polar}\n')
                        inner_polar = inner_polar[np.argsort(inner_polar[:, 0])]
                        logfile.write(f'inner_polar sorted: {inner_polar}\n')

                    outer_polar = xfoilpolars.get_xfoil_polar(outer_airfoil, reynolds,
                                                              alfa_start=0, alfa_end=alfa_max[1],
                                                              alfa_step=alfa_step)
                    logfile.write(f'outer_polar: {outer_polar}\n')
                    if cl_below_zero:
                        outer_polar_below_zero = xfoilpolars.get_xfoil_polar(outer_airfoil, reynolds,
                                                                             alfa_start=0, alfa_end=alfa_min[1],
                                                                             alfa_step=alfa_step)
                        logfile.write(f'outer_polar_below_zero: {outer_polar_below_zero}\n')
                        outer_polar = np.vstack((outer_polar, outer_polar_below_zero))
                        logfile.write(f'outer_polar: {outer_polar}\n')
                        outer_polar = outer_polar[np.argsort(outer_polar[:, 0])]
                        logfile.write(f'outer_polar sorted (first iteration): {outer_polar}\n')
                        logfile.write(f'#############################################################\n')
                else:
                    new_inner_values = xfoilpolars.get_xfoil_polar(inner_airfoil, reynolds,
                                                                   alfa_start=0, alfa_end=alfa_max[0],
                                                                   alfa_step=alfa_step)
                    logfile.write(f'new_inner_values: {new_inner_values}\n')
                    if cl_below_zero:
                        new_inner_polar_below_zero = xfoilpolars.get_xfoil_polar(inner_airfoil, reynolds,
                                                                                 alfa_start=0, alfa_end=alfa_min[0],
                                                                                 alfa_step=alfa_step)
                        logfile.write(f'new_inner_values_below_zero: {new_inner_polar_below_zero}\n')
                        new_inner_values = np.vstack((new_inner_values, new_inner_polar_below_zero))
                        logfile.write(f'new_inner_values: {new_inner_values}\n')
                        new_inner_values = new_inner_values[np.argsort(new_inner_values[:, 0])]
                        logfile.write(f' new_inner_values sorted: {new_inner_values}\n')

                    logfile.write(f'shape_new_inner_values = {new_inner_values.shape},'
                                  f'shape_inner_polar = {inner_polar.shape}\n')
                    logfile.write(f'inner_polar = {inner_polar}\n')
                    logfile.write(f'new_inner_values = {new_inner_values}\n')
                    inner_polar = np.dstack((inner_polar, new_inner_values))
                    logfile.write(f'inner_polar: {inner_polar}\n')

                    new_outer_values = xfoilpolars.get_xfoil_polar(outer_airfoil, reynolds,
                                                                   alfa_start=0, alfa_end=alfa_max[1],
                                                                   alfa_step=alfa_step)
                    logfile.write(f'new_outer_values: {new_outer_values}\n')
                    if cl_below_zero:
                        new_outer_polar_below_zero = xfoilpolars.get_xfoil_polar(outer_airfoil, reynolds,
                                                                                 alfa_start=0, alfa_end=alfa_min[1],
                                                                                 alfa_step=alfa_step)
                        logfile.write(f'new_outer_values_below_zero: {new_outer_polar_below_zero}\n')
                        new_outer_values = np.vstack((new_outer_values, new_outer_polar_below_zero))
                        logfile.write(f'new_outer_values: {new_outer_values}\n')
                        new_outer_values = new_outer_values[np.argsort(new_outer_values[:, 0])]
                        logfile.write(f' new_outer_values sorted: {new_outer_values}\n')
                    outer_polar = np.dstack((outer_polar, new_outer_values))
                    logfile.write(f'outer_polar: {outer_polar}\n')
                    logfile.write(f'####################################################################\n')
                    # inner_polar = xfoilpolars.get_xfoil_polar(inner_airfoil, reynolds,
                    #                                          alfa_start=alfa_start[0], alfa_end=alfa_end[0],
                    #                                          alfa_step=alfa_step)
                    # outer_polar = xfoilpolars.get_xfoil_polar(outer_airfoil, reynolds,
                    #                                          alfa_start=alfa_start[1], alfa_end=alfa_end[1],
                    #                                          alfa_step=alfa_step)
                first_iteration = False
                # oder:
                """inner_polar[i] = xfoilpolars.get_xfoil_polar(inner_airfoil, reynolds,
                                                             cl_start=cl_min, cl_end=cl_max)
                outer_polar[i] = xfoilpolars.get_xfoil_polar(outer_airfoil, reynolds,
                                                             cl_start=cl_min, cl_end=cl_max)"""

            # strips = self.plane.avl.outputs.strip_forces[:, 0]
            strips = self.plane.avl.outputs.surface_dictionary[surface]["strips"][:, 0]
            logfile.write(f'strips = {strips}\n')
            for element in strips:
                # surface_index = self.mach_strip_to_surface(element)
                # strip_values = self.plane.avl.outputs.strip_forces[:, element-1]
                strip_values = self.plane.avl.outputs.surface_dictionary[surface]["strips"][int(element - 1), :]
                logfile.write(f'strip_values: {strip_values}\n')

                """if element == strips[-1]:
                    strip_values_outer = self.plane.avl.outputs.strip_forces[:, element] # nächstes Element, noch ändern
                else:
                    strip_values_outer = None"""

                chord = strip_values[4]
                local_cl = strip_values[9]  # 9 und nicht 6 (cl_norm)
                global_cl = self.plane.aero_coeffs.lift_coeff.cl_tot
                local_reynolds = v_factor * self.get_local_reynolds(global_cl, chord)
                logfile.write(f'local_chord = {chord}, local_cl = {local_cl},'
                              f'global_cl = {global_cl}, local_reynolds = {local_reynolds}\n')

                # inner_polar: (alfa, polar_data, reynoldsnumber)

                # interpolate polar for inner_airfoil (with local_reynolds)
                shape = np.shape(inner_polar)
                logfile.write(f'shape_inner = {shape}\n')
                new_inner_polar = np.zeros((shape[0], shape[1]))
                for i in range(shape[0]):  # Reduzierung um Anstellwinkel auf (Re-Zahl, Polarendaten)
                    alfa_polar = inner_polar[i, :, :]
                    logfile.write(f'alfa_polar = {alfa_polar}\n')
                    for j in range(shape[1]):  # Reduzierung um Polarendaten auf (Re-Zahl-Abhängigkeit)
                        polar_data = np.interp(local_reynolds, list_of_reynolds, inner_polar[i, j, :])
                        new_inner_polar[i, j] = polar_data
                        logfile.write(f'polar_data = {polar_data}\n')
                logfile.write(f'new_inner_polar_for_interpolation = {new_inner_polar}\n')
                # new_inner_polar: (Alfa, Polarendaten)

                #       interpolate cd for given cl for inner_airfoil
                cd_new_inner = np.interp(local_cl, new_inner_polar[:, 1], new_inner_polar[:, 2])  # cl_new, cl, cd
                logfile.write(f'local_cl = {local_cl}, cd_new_inner = {cd_new_inner}\n')

                # interpolate polar for outer_airfoil (with local_reynolds)
                shape_outer = np.shape(outer_polar)
                logfile.write(f'shape_outer = {shape_outer}\n')
                new_outer_polar = np.zeros((shape_outer[0], shape_outer[1]))
                logfile.write(f'new_inner_polar = {new_outer_polar}\n')
                for i in range(shape_outer[0]):  # Reduzierung um Anstellwinkel auf (Re-Zahl, Polarendaten)
                    alfa_polar_outer = outer_polar[i, :, :]
                    logfile.write(f'alfa_polar_outer = {alfa_polar_outer}\n')
                    for j in range(shape[1]):  # Reduzierung um Polarendaten auf (Re-Zahl-Abhängigkeit)
                        polar_data = np.interp(local_reynolds, list_of_reynolds, outer_polar[i, j, :])
                        new_outer_polar[i, j] = polar_data
                        logfile.write(f'polar_data_outer = {polar_data}\n')
                logfile.write(f'new_outer_polar_for_interpolation = {new_outer_polar}\n')
                # new_inner_polar: (Alfa, Polarendaten)

                #       interpolate cd for given cl for outer_airfoil
                cd_new_outer = np.interp(local_cl, new_outer_polar[:, 1], new_outer_polar[:, 2])  # cl_new, cl, cd
                logfile.write(f'local_cl = {local_cl}, cd_new_outer = {cd_new_outer}\n')

                # interpolate profile_cd for position between inner and outer strip.
                y_le_inner = float()
                y_le_outer = float()
                if surface > number_of_wing_segments_per_halfspan * 2:
                    pass  # skip to empennage, implemented later
                else:
                    # print(surface)
                    # print(list_index)
                    y_le_inner = self.plane.wing.segments[list_index].nose_inner[1]     # davor surface
                    y_le_outer = self.plane.wing.segments[list_index].nose_outer[1]     # davor surface
                interp = np.array([y_le_inner, y_le_outer])
                cd_list = np.array([cd_new_inner, cd_new_outer])
                cd_local = np.interp(strip_values[2], interp, cd_list)  # (y_le, interp, cd_list)
                logfile.write(f'y_le_inner = {y_le_inner}, y_le_outer = {y_le_outer},\n'
                              f'cd_new_inner = {cd_new_inner}, cd_new_outer = {cd_new_outer},\n'
                              f'y_le = {strip_values[2]}, cd_local = {cd_local}\n')

                # adapt profile_cd to s_ref with CD = profile_cd*strip_area/s_ref
                area = strip_values[5]
                cd_local_to_global = cd_local * area / self.plane.avl.outputs.s_ref
                area_for_reference += area
                logfile.write(f'strip_area = {area}, reference_wing_area = {self.plane.avl.outputs.s_ref},\n'
                              f'area_for_reference  = {area_for_reference},\n'
                              f'cd_local_to_global = {cd_local_to_global}\n')

                viscous_drag[surface_original - 1] += cd_local_to_global  # noch mit surface Dopplung schauen
            overall_viscous_drag += viscous_drag[surface_original - 1]
        logfile.close()
        self.plane.aero_coeffs.drag_coeff.cd_viscous = overall_viscous_drag
        return overall_viscous_drag, viscous_drag


# Tests: veränderung der Größe des viskosen Widerstandes mit Erhöhung von Stripanzahl untersuchen.
# -> Validierung der Software


if __name__ == "__main__":
    plane = PlaneParser("aachen.toml").get("Plane")
    GeometryFile(plane).build_geometry_file(1)
    MassFile(plane).build_mass_file()
    athenavortexlattice.AVL(plane).run_avl(lift_coefficient=0.8)

    athenavortexlattice.AVL(plane).read_avl_output()
    # print(plane.avl.outputs.surface_dictionary)
    result = ViscousDrag(plane).create_avl_viscous_drag_from_xfoil()
    print(f'overall_viscous_drag = {result[0]}, viscous_drag = {result[1]}')
    print(f'induced_drag = {plane.aero_coeffs.drag_coeff.cd_ind}')
    print(f'cd_overall = {plane.aero_coeffs.drag_coeff.cd_viscous + plane.aero_coeffs.drag_coeff.cd_ind}')
    print(f'cl_tot = {plane.aero_coeffs.lift_coeff.cl_tot}')
