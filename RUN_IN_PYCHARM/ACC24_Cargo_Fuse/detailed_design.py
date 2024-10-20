from vehicle_setup import vehicle_setup
import numpy as np
def check_if_aircraft_nicks(Vehicle):
    delta_x = vehicle.center_of_gravity[0] - vehicle.landing_gear.wheels[1].origin[0]
    delta_z = vehicle.center_of_gravity[2] - (vehicle.landing_gear.wheels[1].origin[2] - vehicle.landing_gear.wheels[1].diameter / 2)
    mu = 0.2
    if (delta_x) > (delta_z * mu):
        print('Aircraft does not nick')
    else:
        print('Aircraft nicks')
    neigungswinkel = np.arctan(delta_x / delta_z) * 180 / np.pi
    print('Neigungswinkel %.1f deg' % neigungswinkel)
    print('Landing gear delta_z %.2f m' % delta_z)



main_wing_x = 0.18
front_wheel_percent_mac = 0.24

vehicle = vehicle_setup(
    payload=0,
    wing_area=0.65, #ACC17=1.22, ACC22=0.61
    aspect_ratio=10., #ACC17=12.52, ACC22=9.6
    airfoil="acc24", #acc22
    num_fowler_segments=0, #ACC17=0, ACC22=4
    battery_capacity=3.,
    propeller="freudenthaler14x8",
    main_wing_x=main_wing_x,
    battery_origin_x=0.9,
    front_wheel_percent_mac = front_wheel_percent_mac)
vehicle.plot_vehicle(azim=230, elev=30)
print('-----------------------------------------')
check_if_aircraft_nicks(vehicle)
print('Battery in rear')
print('payload %.2f kg' % vehicle.results.mass_payload)
print('mass empty %.2f kg' % vehicle.results.mass_empty)
print('x cg %.3f m' % (vehicle.results.x_center_of_gravity - vehicle.wings['main_wing'].origin[0]))
print('static margin %.1f ' % (100*vehicle.results.static_margin))
print('c_m_alpha %.3f' % vehicle.results.c_m_alpha)
print('percent mac %.3f' % vehicle.results.percent_mac)

vehicle = vehicle_setup(
    payload=4.25-0.17,
    wing_area=0.65, #ACC17=1.22, ACC22=0.61R
    aspect_ratio=10., #ACC17=12.52, ACC22=9.6
    airfoil="acc24", #acc22
    num_fowler_segments=0, #ACC17=0, ACC22=4
    battery_capacity=3.,
    propeller="freudenthaler14x8",
    main_wing_x=main_wing_x,
    front_wheel_percent_mac = front_wheel_percent_mac)
#vehicle.plot_vehicle(azim=230, elev=30)


print('-----------------------------------------')
check_if_aircraft_nicks(vehicle)
print('Battery in front')
print('payload %.2f kg' % vehicle.results.mass_payload)
print('mass empty %.2f kg' % vehicle.results.mass_empty)
print('x cg %.3f m' % (vehicle.results.x_center_of_gravity - vehicle.wings['main_wing'].origin[0]))
print('static margin %.1f ' % (100*vehicle.results.static_margin))
print('c_m_alpha %.3f' % vehicle.results.c_m_alpha)
print('percent mac %.3f' % vehicle.results.percent_mac)

vehicle = vehicle_setup(
    payload=4.25+0.17,
    wing_area=0.65, #ACC17=1.22, ACC22=0.61
    aspect_ratio=10., #ACC17=12.52, ACC22=9.6
    airfoil="acc24", #acc22
    num_fowler_segments=0, #ACC17=0, ACC22=4
    battery_capacity=3.,
    propeller="freudenthaler14x8",
    main_wing_x=main_wing_x,
    front_wheel_percent_mac = front_wheel_percent_mac)
#vehicle.plot_vehicle(azim=230, elev=30)

print('-----------------------------------------')
check_if_aircraft_nicks(vehicle)
print('Battery in front')
print('payload %.2f kg' % vehicle.results.mass_payload)
print('mass empty %.2f kg' % vehicle.results.mass_empty)
print('x cg %.3f m' % (vehicle.results.x_center_of_gravity - vehicle.wings['main_wing'].origin[0]))
print('static margin %.1f ' % (100*vehicle.results.static_margin))
print('c_m_alpha %.3f' % vehicle.results.c_m_alpha)
print('percent mac %.3f' % vehicle.results.percent_mac)
print('-----------------------------------------')
