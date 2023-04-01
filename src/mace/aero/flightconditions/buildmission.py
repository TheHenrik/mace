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
        v_min = float(input('Bitte Abhebegeschwindigkeit angeben:\n'))
        num = int(input('Anzahl Iterationsschritte angeben:\n'))
        v_timer_start = float(input('Bitte Startgeschwindigkeit für Timer angeben:\n'))
        takeoff.Takeoff(self.plane).takeoff(v_min, num, v_timer_start=v_timer_start)
        print(self.plane.flightconditions.takeoff.results)


if __name__ == "__main__":
    testplane = PlaneParser("testplane.toml").get("Plane")
    GeometryFile(testplane).build_geometry_file(1)
    MassFile(testplane).build_mass_file()
    athenavortexlattice.AVL(testplane).run_avl(lift_coefficient=1)

    athenavortexlattice.AVL(testplane).read_avl_output()
    # print(plane.avl.outputs.surface_dictionary)
    result = ViscousDrag(testplane).create_avl_viscous_drag_from_xfoil(alfa_step=1)
    print(f'overall_viscous_drag = {result[0]}, viscous_drag = {result[1]}')
    print(f'induced_drag = {testplane.aero_coeffs.drag_coeff.cd_ind}')
    print(f'cd_overall = {testplane.aero_coeffs.drag_coeff.cd_viscous + testplane.aero_coeffs.drag_coeff.cd_ind}')
    print(f'cl_tot = {testplane.aero_coeffs.lift_coeff.cl_tot}')
    BuildMission(testplane).build_mission()
