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
        # Takeoff

        berechnung_takeoff = input('Berechnung Takeoff? (Ja/Nein)')
        if berechnung_takeoff == 'Ja':
            v_min = float(input('Bitte Abhebegeschwindigkeit angeben:\n'))
            step = float(input('Bitte Schrittweite der Iterationsschritte angeben:\n'))
            v_timer_start = float(input('Bitte Startgeschwindigkeit für Timer angeben:\n'))
            takeoff.Takeoff(self.plane).takeoff(v_min, step, v_timer_start=v_timer_start)
            print(self.plane.flightconditions.takeoff.results)

        # Climb

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
                  f' current_thrust = {self.plane.flightconditions.climb.results.climb_data[:, 7]},\n')
            print(f'steepest_climb = {self.plane.flightconditions.climb.results.gamma_max},\n'
                  f'fastest_climb = {self.plane.flightconditions.climb.results.v_vertical_max}\n')
            # gained height and distance

        # Horizontal Flight

        berechnung_horizontal = input('Berechnung Horizontal Flight? (Ja/Nein)')
        if berechnung_horizontal == 'Ja':
            horizontalflight.HorizontalFlight(self.plane).fv_diagramm(0.3, 0.5)
            print(f'velocity, needed_thrust = '
                  f'{self.plane.flightconditions.horizontalflight.results.thrust_velocity_correlation}')
            print(f'minimum_thrust = {self.plane.flightconditions.horizontalflight.results.minimum_thrust}')
            print(f'maximum_flight_velocity = '
                  f'{self.plane.flightconditions.horizontalflight.results.maximum_flight_velocity}')
            accel = horizontalflight.HorizontalFlight(self.plane).acceleration(10, 20, 0.1)
            print(f'Acceleration time = {accel[0]}, distance = {accel[1]}')

        # Turning Flight

        berechnung_turning = input('Berechnung Turning Flight? (Ja/Nein)')
        if berechnung_turning == 'Ja':
            result_turning = turningflight.TurningFlight(self.plane).turn_radius(v=10, r_k=25)
            print(f'velocity = {result_turning[0]}')
            print(f'radius of turning flight = {result_turning[1]}')
            print(f'lift coefficient = {result_turning[2]}')
            print(f'load faktor = {result_turning[3]}')
            print(f'rolling angel = {result_turning[4]}')
            print(f'turning velocity chi_dot = {result_turning[5]}')
            print(f'turning time for 180deg = '
                  f'{turningflight.TurningFlight(self.plane).turning_time(180, result_turning[5])}')
            print(f'needed_thrust = '
                  f'{turningflight.TurningFlight(self.plane).needed_thrust_for_turn(0.05, result_turning[2], n=result_turning[3])}')
            print(f'turn_acceleration = {turningflight.TurningFlight(self.plane).turn_acceleration(10, 180, 5, turn_radius=25)}')

        # Gliding Flight

        berechnung_gliding = input('Berechnung Gliding Flight? (Ja/Nein)')
        if berechnung_gliding == 'Ja':
            gliding_data = glidingflight.GlidingFlight(self.plane).v_glide_iteration(0.5, cl_start=0.2, cl_step=0.1, velocity_tolerance=1, it_max=5)
            print(f'[cl, cd, cd_viscous, cd_induced, velocity, vertical_velocity]')
            print(gliding_data)

        # Landing

        berechnung_landing = input('Berechnung Landing? (Ja/Nein)')
        if berechnung_landing == 'Ja':
            pass


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