from mace.aero.implementations.avl import athenavortexlattice
from mace.aero import generalfunctions
from mace.aero.implementations.xfoil import xfoilpolars
from mace.domain import params, Plane
from mace.aero.implementations.avl.athenavortexlattice import AVL
import numpy as np
import math
from mace.domain.parser import PlaneParser
from mace.aero.implementations.avl.geometry_and_mass_files import GeometryFile, MassFile



class ViscousDrag:
    def __init__(self, plane: Plane):
        self.plane = plane
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho
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

    def get_cl_min_of_surface(self, surface):
        # cl_min = np.min(self.plane.avl.outputs.strip_forces[:, 6])    # (zeile, element) von allen Reihen 6. Element
        cl_min = np.min(self.plane.avl.outputs.surface_dictionary[surface]["strips"][:, 6])
        return cl_min

    def get_cl_max_of_surface(self, surface):
        # cl_max = np.max(self.plane.avl.outputs.strip_forces[:, 6])    # (zeile, element)
        cl_max = np.max(self.plane.avl.outputs.surface_dictionary[surface]["strips"][:, 6])
        return cl_max

    def get_chord_min_of_surface(self, surface):
        # chord_min = np.min(self.plane.avl.outputs.strip_forces[:, 4])    # (zeile, element)
        # print(self.plane.avl.outputs.surface_dictionary[surface]["strips"][:, 4])
        chord_min = np.min(self.plane.avl.outputs.surface_dictionary[surface]["strips"][:, 4])
        return chord_min  # außen sollte noch bedacht werden

    def get_chord_max_of_surface(self, surface):
        # chord_max = np.max(self.plane.avl.outputs.strip_forces[:, 4])    # (zeile, element)
        chord_max = np.max(self.plane.avl.outputs.surface_dictionary[surface]["strips"][:, 4])
        return chord_max  # außen sollte noch bedacht werden

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
        reynolds_st = (reynolds_max - reynolds_min) / 4
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

    def create_avl_viscous_drag_from_xfoil(self, *, velocity=None):
        """
        This is written for stationary horizontal flight.
        For other velocities please intput them. The function will compare it with horizontal flight and
        will use an optimized reynoldsnumber. (Therefore cl has to be higher than 0.)
        """
        cd_local_to_global = 0
        viscous_drag = np.zeros(self.plane.avl.outputs.number_of_surfaces)
        overall_viscous_drag = 0
        cl_global = self.plane.aero_coeffs.lift_coeff.cl_tot
        print(f'cl_global ={cl_global}')
        # Compare v_horizontal with new velocity
        if velocity is None:
            v_factor = 1
        else:
            v_horizontal = ((2 * self.mass * self.g) / (cl_global * self.rho * self.s_ref)) ** 0.5
            v_factor = velocity / v_horizontal

        for surface in range(1, self.plane.avl.outputs.number_of_surfaces + 1):  # 1, 2, 3, ... , last surface
            if surface % 2 == 0:
                surface -= 1
            cl_min = math.floor(self.get_cl_min_of_surface(surface) * 10) / 10  # abgerundet [0.1]
            cl_max = math.ceil(self.get_cl_max_of_surface(surface) * 10) / 10  # aufgerundet [0.1]
            chord_min = math.floor(self.get_chord_min_of_surface(surface) * 1000) / 1000  # abgerundet [mm]
            chord_max = math.ceil(self.get_chord_max_of_surface(surface) * 1000) / 1000  # aufgerundet [mm]
            print(f'cl_min = {cl_min}, cl_max = {cl_max}, chord_min = {chord_min}, chord_max = {chord_max}')
            reynolds_min = math.floor((v_factor * self.get_local_reynolds(cl_global, chord_min))/1000)*1000
            # abgerundet auf 1000 [integer]
            print(f'reynolds_min = {reynolds_min}')
            reynolds_max = math.ceil((v_factor * self.get_local_reynolds(cl_global, chord_max))/1000)*1000  # aufgerundet [integer]
            print(f'reynolds_max = {reynolds_max}')
            reynolds_steps = math.ceil(self.get_reynolds_step(reynolds_min, reynolds_max))  # aufgerundet [integer]
            print(f'reynolds_steps = {reynolds_steps}')

            list_index = int()
            number_of_wing_segments_per_halfspan = len(self.plane.wing.segments)
            if surface > number_of_wing_segments_per_halfspan * 2:
                pass  # skip to empennage, implemented later
            elif surface % 2 != 0:  # right wing
                list_index = int((surface - 1) / 2)
            elif surface % 2 == 0:  # left wing
                list_index = int(surface / 2)

            # hier noch unterscheiden zwischen Naca und nicht Naca
            inner_airfoil = self.plane.wing.segments[list_index].inner_airfoil.type.filepath
            outer_airfoil = self.plane.wing.segments[list_index].outer_airfoil.type.filepath

            alfa_start = [0, 0]  # [inner_airfoil, outer_airfoil]
            alfa_end = [0, 0]  # [inner_airfoil, outer_airfoil]
            alfa_step = 1
            reserve = 2  # degrees
            print(inner_airfoil, outer_airfoil)
            # ---Calculation of alfa_start and alfa_end---
            i = 0
            for airfoil in [inner_airfoil, outer_airfoil]:
                cl_of_alfa_zero = xfoilpolars.get_xfoil_polar(airfoil, reynolds_min, alfa=0)[1]
                print(f'cl_of_alfa_zero = {cl_of_alfa_zero}')
                # Auftriebsanstieg: cl = 0.11 * alfa[Grad]
                print(f'cl_min < cl_of_alfa_zero = {cl_min < cl_of_alfa_zero}')
                if cl_min < cl_of_alfa_zero:
                    cl_dif_neg = cl_of_alfa_zero - cl_min
                    alfa_start[i] = -(cl_dif_neg / 0.11 + reserve)  # Auftriebsabfall = 0.11 /Grad - Reserve
                else:
                    alfa_start[i] = 0  # für bessere Konvergenz
                cl_dif = cl_max - cl_of_alfa_zero
                alfa_end[i] = math.ceil(cl_dif / 0.11 + reserve)  # Auftriebsanstieg = 0.11 /Grad + Reserve
                i += 1
                print(f'alfa_start = {alfa_start}')
                print(f'alfa_end = {alfa_end}')  # eventuell noch aufrunden, aber alfa step geht eh höher

            # ---Polar calculations---

            inner_polar = np.ndarray
            outer_polar = np.ndarray
            # list_of_reynolds = range(reynolds_min, reynolds_max, reynolds_steps)
            list_of_reynolds = np.linspace(reynolds_min, reynolds_max, 5)
            first_iteration = True
            print(f'alfa_start = {alfa_start}, alfa_end = {alfa_end}, alfa_step = {alfa_step}')
            print(f'list_of_reynolds = {list_of_reynolds}')
            for reynolds in list_of_reynolds:
                if first_iteration:
                    inner_polar = xfoilpolars.get_xfoil_polar(inner_airfoil, reynolds,
                                                              alfa_start=alfa_start[0], alfa_end=alfa_end[0],
                                                              alfa_step=alfa_step)
                    outer_polar = xfoilpolars.get_xfoil_polar(outer_airfoil, reynolds,
                                                              alfa_start=alfa_start[1], alfa_end=alfa_end[1],
                                                              alfa_step=alfa_step)
                    print(f'################################################'
                          f'inner_polar(first iteration) = {inner_polar}')
                else:
                    new_inner_values = xfoilpolars.get_xfoil_polar(inner_airfoil, reynolds,
                                                                   alfa_start=alfa_start[0], alfa_end=alfa_end[0],
                                                                   alfa_step=alfa_step)
                    print('##############################################################################')
                    print(f'shape_new_inner = {new_inner_values.shape}, shape_inner = {inner_polar.shape}')
                    print(f'inner_polar = {inner_polar}')
                    print(f'new_inner_values = {new_inner_values}')
                    inner_polar = np.dstack((inner_polar, new_inner_values))

                    new_outer_values = xfoilpolars.get_xfoil_polar(outer_airfoil, reynolds,
                                                                   alfa_start=alfa_start[1], alfa_end=alfa_end[1],
                                                                   alfa_step=alfa_step)
                    outer_polar = np.dstack((outer_polar, new_outer_values))

                    print(f'#####################################################'
                          f'inner_polar(other iterations) = {inner_polar}')
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
            print(f'strips = {strips}')
            for element in strips:
                # surface_index = self.mach_strip_to_surface(element)
                # strip_values = self.plane.avl.outputs.strip_forces[:, element-1]
                strip_values = self.plane.avl.outputs.surface_dictionary[surface]["strips"][int(element - 1), :]

                """if element == strips[-1]:
                    strip_values_outer = self.plane.avl.outputs.strip_forces[:, element] # nächstes Element, noch ändern
                else:
                    strip_values_outer = None"""

                chord = strip_values[4]
                local_cl = strip_values[6]
                global_cl = self.plane.aero_coeffs.lift_coeff.cl_tot
                local_reynolds = v_factor * self.get_local_reynolds(global_cl, chord)
                # lokales cl, anstatt auf globales.

                # inner_polar: (alfa, polar_data, reynoldsnumber)

                print(f'local_reynolds = {local_reynolds}, list_of_reynolds = {list_of_reynolds},'
                      f'inner_polar = {inner_polar}')
                print(f'inner_polar = {inner_polar}')
                print()
                # interpolate polar for inner_airfoil (with local_reynolds)
                shape = np.shape(inner_polar)
                print(f'shape = {shape}')
                new_inner_polar = np.zeros((shape[0], shape[1]))
                print(f'new_inner_polar = {new_inner_polar}')
                for i in range(shape[0]):          # Reduzierung um Anstellwinkel auf (Re-Zahl, Polarendaten)
                    alfa_polar = inner_polar[i, :, :]
                    print(f'alfa_polar = {alfa_polar}')
                    for j in range(shape[1]):                  # Reduzierung um Polarendaten auf (Re-Zahl-Abhängigkeit)
                        polar_data = np.interp(local_reynolds, list_of_reynolds, inner_polar[i, j, :])
                        new_inner_polar[i, j] = polar_data
                        print(f'polar_data = {polar_data}')
                print(f'new_inner_polar = {new_inner_polar}') # new_inner_polar: (Alfa, Polarendaten)

                #       interpolate cd for given cl for inner_airfoil
                cd_new_inner = np.interp(local_cl, new_inner_polar[:, 1], new_inner_polar[:, 2])  # cl_new, cl, cd
                print(f'local_cl = {local_cl}')
                print(f'cd_new_inner = {cd_new_inner}')

                # interpolate polar for outer_airfoil (with local_reynolds)
                shape_outer = np.shape(outer_polar)
                print(f'shape = {shape_outer}')
                new_outer_polar = np.zeros((shape_outer[0], shape_outer[1]))
                print(f'new_inner_polar = {new_outer_polar}')
                for i in range(shape_outer[0]):  # Reduzierung um Anstellwinkel auf (Re-Zahl, Polarendaten)
                    alfa_polar_outer = outer_polar[i, :, :]
                    print(f'alfa_polar = {alfa_polar_outer}')
                    for j in range(shape[1]):  # Reduzierung um Polarendaten auf (Re-Zahl-Abhängigkeit)
                        polar_data = np.interp(local_reynolds, list_of_reynolds, outer_polar[i, j, :])
                        new_outer_polar[i, j] = polar_data
                        print(f'polar_data = {polar_data}')
                print(f'new_outer_polar = {new_outer_polar}')  # new_inner_polar: (Alfa, Polarendaten)

                #       interpolate cd for given cl for outer_airfoil
                cd_new_outer = np.interp(local_cl, new_outer_polar[:, 1], new_inner_polar[:, 2])  # cl_new, cl, cd
                print(f'local_cl = {local_cl}')
                print(f'cd_new_inner = {cd_new_inner}')

                # interpolate profile_cd for position between inner and outer strip.
                y_le_inner = float()
                y_le_outer = float()
                if surface > number_of_wing_segments_per_halfspan * 2:
                    pass  # skip to empennage, implemented later
                else:
                    y_le_inner = self.plane.wing.segments[list_index].nose_inner[1]
                    y_le_outer = self.plane.wing.segments[list_index].nose_outer[1]
                interp = np.array([y_le_inner, y_le_outer])
                cd_list = np.array([cd_new_inner, cd_new_outer])
                cd_local = np.interp(strip_values[2], interp, cd_list)  # (y_le, interp, cd_list)

                # adapt profile_cd to s_ref with CD = profile_cd*strip_area/s_ref
                area = strip_values[5]
                cd_local_to_global = cd_local * area / self.plane.avl.outputs.s_ref

            viscous_drag[surface-1] += cd_local_to_global       # noch mit surface Dopplung schauen
            overall_viscous_drag += viscous_drag[surface]

        return overall_viscous_drag, viscous_drag


# Tests: veränderung der Größe des viskosen Widerstandes mit Erhöhung von Stripanzahl untersuchen.
# -> Validierung der Software


if __name__ == "__main__":
    plane = PlaneParser("testplane.toml").get("Plane")
    GeometryFile(plane).build_geometry_file(1)
    MassFile(plane).build_mass_file()
    athenavortexlattice.AVL(plane).run_avl()

    athenavortexlattice.AVL(plane).read_avl_output()
    # print(plane.avl.outputs.surface_dictionary)
    result = ViscousDrag(plane).create_avl_viscous_drag_from_xfoil()
    print(f'overall_viscous_drag = {result[0]}, viscous_drag = {result[1]}')