from mace.domain.wing import Wing, WingSegment
from mace.domain.fuselage import Fuselage, FuselageSegment
from mace.domain.landing_gear import LandingGear, Wheel
from mace.domain.vehicle import Vehicle
import numpy as np
import matplotlib.pyplot as plt

def fuselage_setup():
    fuselage = Fuselage()

    segment = FuselageSegment()
    segment.origin[0] = -0.148
    segment.width = 0.04
    segment.height = 0.04
    fuselage.add_segment(segment)

    segment = FuselageSegment()
    segment.origin[0] = -0.1
    segment.width = 0.085
    segment.height = 0.107
    fuselage.add_segment(segment)

    segment = FuselageSegment()
    segment.origin[0] = -0.05
    segment.width = 0.099
    segment.height = 0.139
    fuselage.add_segment(segment)

    segment = FuselageSegment()
    segment.origin[0] = 0.
    segment.width = 0.102
    segment.height = 0.151
    fuselage.add_segment(segment)

    segment = FuselageSegment()
    segment.origin[0] = 0.38
    segment.width = 0.061
    segment.height = 0.084
    fuselage.add_segment(segment)

    segment = FuselageSegment()
    segment.origin[0] = 0.38 + 0.088
    segment.width = 0.04
    segment.height = 0.04
    fuselage.add_segment(segment)

    fuselage.build()
    return fuselage

def wheel_setup():
    landing_gear = LandingGear()

    Height = 0.25
    landing_gear.height = Height

    wheel1 = Wheel()
    wheel1.diameter = 0.1
    wheel1.mass = 0.05
    wheel1.origin = np.array([-0.1, 0., -0.2])
    landing_gear.add_wheel(wheel1)

    wheel2 = Wheel()
    wheel2.diameter = 0.16
    wheel2.mass = 0.05
    wheel2.origin = np.array([0., 0.27, -0.1])
    landing_gear.add_wheel(wheel2)

    wheel3 = Wheel()
    wheel3.diameter = wheel2.diameter
    wheel3.mass = wheel2.mass
    wheel3.origin = np.array([0., -0.27, -0.1])
    wheel3.origin[1] = -wheel2.origin[1]
    landing_gear.add_wheel(wheel3)

    landing_gear.finalize()

    l_calc = 0.
    for wheel in landing_gear.wheels:
        l_calc += (wheel.origin[1] ** 2 + wheel.origin[2] ** 2) ** 0.5 - vehicle.fuselages['fuselage'].diameter
    landing_gear.effective_drag_length = l_calc
    landing_gear.length_specific_cd = 0.0033

    return landing_gear

if __name__ == '__main__':
    vehicle = Vehicle()

    fuselage = fuselage_setup()
    vehicle.add_fuselage("fuselage", fuselage)

    landing_gear = wheel_setup()
    vehicle.landing_gear = landing_gear

    vehicle.plot_vehicle(azim=230, elev=30)

    rho = 1.15
    v_vector_windtunnel = [4.24, 9.51, 14.78, 19.71, 23.36]
    F_vector_windtunnel = [0.02655, 0.1985, 0.4385, 0.8582, 1.0674]

    v_vector_windtunnel_2 = [0, 4.2, 9.55, 14.84, 19.68, 23.25]
    wheel_drag_vector_windtunnel = [-0.0273, -0.0178, 0.0755, 0.2262, 0.3918, 0.6585]
    gestaenge_drag_vector_windtunnel = [0., 0.03378, 0.17873, 0.483, 0.925, 1.2235]

    v_vector = np.linspace(0, 25, 50)
    fuse_drag_vector = np.zeros_like(v_vector)
    wheel_drag_vector = np.zeros_like(v_vector)
    gestaenge_drag_vector = np.zeros_like(v_vector)
    for i, v in enumerate(v_vector):
        c_d_fuse = fuselage.get_drag_coefficient(v, 1)
        c_d_wheel = 0.
        for wheel in vehicle.landing_gear.wheels:
            c_d_wheel += wheel.get_drag_coefficient(v, 1)
        fuse_drag_vector[i] = rho / 2 * v**2 * c_d_fuse * 1
        wheel_drag_vector[i] = rho / 2 * v**2 * c_d_wheel * 1
        c_d_landing_gear = vehicle.landing_gear.get_drag_coefficient(v, 1) - c_d_wheel
        gestaenge_drag_vector[i] = rho / 2 * v**2 * c_d_landing_gear

    fig = plt.figure(dpi=400)
    ax = fig.add_subplot(111)
    ax.plot(v_vector, fuse_drag_vector, label='MACE Widerstand ACC Rumpf')
    ax.scatter(v_vector_windtunnel, F_vector_windtunnel, label='WINDKANAL Widerstand ACC Rumpf')
    ax.plot(v_vector, wheel_drag_vector, label='MACE Widerstand Räder')
    ax.scatter(v_vector_windtunnel_2, wheel_drag_vector_windtunnel, label='WINDKANAL Widerstand Räder')
    ax.plot(v_vector, gestaenge_drag_vector, label='MACE Widerstand Fahrwerk o. Räder')
    ax.scatter(v_vector_windtunnel_2, gestaenge_drag_vector_windtunnel, label='WINDKANAL Widerstand Fahrwerk o. Räder')
    ax.set_xlabel('V [m/s]')
    ax.set_ylabel('F [N]')
    plt.legend()
    plt.grid()
    plt.tick_params(which='major', labelsize=6)
    plt.title("Wind tunnel validation", fontsize=10)
    plt.show()


