import takeoff, climb, horizontalflight, turningflight, glidingflight, landing
from mace.domain.parser import PlaneParser
from mace.aero.implementations.avl.geometry_and_mass_files import GeometryFile, MassFile
from mace.aero.implementations.avl import athenavortexlattice
from mace.aero.implementations.viscousdrag import ViscousDrag
from mace.domain import params, Plane


class BuildMission:
    def __init__(self, plane: Plane):
        self.plane = plane

    def build_mission(self):

        berechnung_takeoff = input('Berechnung Takeoff? (Ja/Nein)')
        if berechnung_takeoff == 'Ja':
            v_min = float(input('Bitte Abhebegeschwindigkeit angeben:\n'))
            step = float(input('Bitte Schrittweite der Iterationsschritte angeben:\n'))
            v_timer_start = float(input('Bitte Startgeschwindigkeit für Timer angeben:\n'))
            takeoff.Takeoff(self.plane).takeoff(v_min, step, v_timer_start=v_timer_start)
            print(self.plane.flightconditions.takeoff.results)

        berechnung_climb = input('Berechnung Climb? (Ja/Nein)')
        if berechnung_climb == 'Ja':
            cl_start = float(input('Bitte cl_start angeben:'))
            cl_end = float(input('Bitte cl_end angeben:'))
            climb.Climb(self.plane).climb(cl_start, cl_end, cl_step=0.1, v_tolerance=0.01, it_max=20)
            # print(self.plane.flightconditions.climb.results)
            print(f'cl = {self.plane.flightconditions.climb.results.climb_data[:, 0]},\n'
                  f' velocity = {self.plane.flightconditions.climb.results.climb_data[:, 1]},\n'
                  f' v_vertical{self.plane.flightconditions.climb.results.climb_data[:, 2]},\n'
                  f' sin = {self.plane.flightconditions.climb.results.climb_data[:, 3]},\n'
                  f' cos = {self.plane.flightconditions.climb.results.climb_data[:, 4]},\n'
                  f' gamma1 ={self.plane.flightconditions.climb.results.climb_data[:, 5]},\n'
                  f' gamma2 = {self.plane.flightconditions.climb.results.climb_data[:, 6]},\n'
                  f' current_thrust = {self.plane.flightconditions.climb.results.climb_data[:, 7]}\n')




if __name__ == "__main__":
    testplane = PlaneParser("testplane.toml").get("Plane")
    GeometryFile(testplane).build_geometry_file(1)
    MassFile(testplane).build_mass_file()
    # athenavortexlattice.AVL(testplane).run_avl(lift_coefficient=testplane.aero_coeffs.lift_coeff.cl_roll)

    # athenavortexlattice.AVL(testplane).read_avl_output()
    #  print(testplane.avl.outputs.surface_dictionary)
    # result = ViscousDrag(testplane).create_avl_viscous_drag_from_xfoil(alfa_step=1)
    # print(f'overall_viscous_drag = {result[0]}, viscous_drag = {result[1]}')
    print(f'induced_drag_coefficient = {testplane.aero_coeffs.drag_coeff.cd_ind}')
    print(f'cd_overall = {testplane.aero_coeffs.drag_coeff.cd_viscous + testplane.aero_coeffs.drag_coeff.cd_ind}')
    print(f'cl_tot = {testplane.aero_coeffs.lift_coeff.cl_tot}')
    BuildMission(testplane).build_mission()