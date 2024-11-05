import logging


from pymace.aero.generalfunctions import GeneralFunctions, get_reynolds_number
from pymace.aero.implementations.aero import Aerodynamics
from pymace.aero.implementations.airfoil_analyses import Airfoil
from pymace.domain import params
from pymace.domain.vehicle import Vehicle


class TakeOff:
    def __init__(self, plane: Vehicle):
        self.plane = plane
        self.mu = 0.125
        self.aero = Aerodynamics(self.plane)
        self.aero.XFOIL.print_re_warnings = False
        self.get_force = GeneralFunctions(self.plane).coefficient_to_lift_or_drag
        # self.get_thrust = GeneralFunctions(self.plane).current_thrust
        self.get_thrust = plane.evaluate_thrust
        self.flap_angle = 0.0
        self.t_step = 0.4
        self.cl_safety_factor = 1.0
        self.v_wind = 0.0
        self.v_start_counter = 0.0
        self.manual_cl_max = 0
        self.show_plot = False
        self.delta_cl_fowler = 1.08
        self.cl_max_factor = 1.0

    def get_friction(self, lift):
        return (self.plane.mass * params.Constants.g - lift) * self.mu

    def evaluate(self):
        S_REF = self.plane.reference_values.s_ref
        MASS = self.plane.mass
        DELTA_T = self.t_step
        V_wind = self.v_wind
        V_start_counter = self.v_start_counter
        G = params.Constants.g
        RHO = params.Constants.rho
        WingAirfoil = Airfoil(
            self.plane.wings["main_wing"].airfoil,
            flap_angle=self.flap_angle,
            x_hinge=(1 - self.plane.wings["main_wing"].segments[0].flap_chord_ratio),
        )
        WingAirfoil.print_re_warnings = False
        MAC = self.plane.wings["main_wing"].mean_aerodynamic_chord

        T = 0.0
        T_total = 0.0
        S = 0.0
        V = 0.0
        CL_MAX = 0.0
        REQ_CL = 1.0

        S_vec = []
        V_vec = []
        while CL_MAX < self.cl_safety_factor * REQ_CL and T < 20:
            self.aero.evaluate(CL=None, V=V, FLAP=self.flap_angle, ALPHA=2.0)
            CL = self.plane.aero_coeffs.lift_coeff.cl_tot
            CD = self.plane.aero_coeffs.drag_coeff.cd_tot

            LIFT = self.get_force(V + V_wind, CL)
            DRAG = self.get_force(V + V_wind, CD)
            FRICTION = self.get_friction(0)
            THRUST = self.get_thrust(V + V_wind, T_total)

            ACCELL = (THRUST - DRAG - FRICTION) / MASS
            if V >= V_start_counter:
                T += DELTA_T
            T_total += DELTA_T
            S += 1 / 2 * ACCELL * DELTA_T**2 + V * DELTA_T
            V += ACCELL * DELTA_T
            # V_exakt = ACCELL * T
            # S_exakt = 1 / 2 * ACCELL * T**2

            if self.show_plot:
                S_vec.append(S)
                V_vec.append(V)

            REQ_CL = (MASS * G) / (1 / 2 * RHO * (V + V_wind) ** 2 * S_REF)
            if self.manual_cl_max == 0:
                RE_AT_MAC = get_reynolds_number((V + V_wind), MAC)
                CL_MAX = WingAirfoil.get_cl_max(RE_AT_MAC)
                S_FOWLER = 0.0
                for segment in self.plane.wings["main_wing"].segments:
                    if segment.control_name == "fowler":
                        S_FOWLER += 2 * segment.area
                delta_CL_flap = self.delta_cl_fowler * S_FOWLER / S_REF
                CL_MAX += delta_CL_flap
                CL_MAX *= self.cl_max_factor
            else:
                CL_MAX = self.manual_cl_max

        res = self.plane.results
        res.take_off_length = S
        res.take_off_time_from_counter_start = T
        res.take_off_time_total = T_total
        res.cl_max_at_take_off = CL_MAX
        res.required_cl_at_take_off = REQ_CL
        res.assumed_wind_speed = V_wind
        res.take_off_ground_speed = V
        res.take_off_air_speed = V + V_wind
        (
            res.takeoff_battery_voltage,
            res.takeoff_battery_soc,
        ) = self.plane.battery.get_voltage(i=30.0, t=T_total)

        if T >= 20:
            logging.info("Takeoff failed")

        if self.show_plot:
            import matplotlib.pyplot as plt

            plt.plot(S_vec, V_vec)
            plt.grid("on")
            plt.show()

        return S, T
