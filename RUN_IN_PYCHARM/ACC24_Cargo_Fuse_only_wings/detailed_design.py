from vehicle_setup import vehicle_setup

main_wing_x = 0.20

vehicle = vehicle_setup(payload=4.25, main_wing_x=main_wing_x)
vehicle.plot_vehicle(azim=230, elev=30)

cog_times_mass = vehicle.results.x_center_of_gravity * vehicle.results.mass_total
print(cog_times_mass)
cog_times_mass -= vehicle.results.mass_payload * vehicle.center_of_gravity_payload[0]
print(cog_times_mass)
cog = cog_times_mass / vehicle.results.mass_empty
print(cog)

vehicle = vehicle_setup(payload=0., main_wing_x=main_wing_x)
#vehicle.plot_vehicle(azim=230, elev=30)

print('-----------------------------------------')
print('payload %.2f kg' % vehicle.results.mass_payload)
print('mass empty %.2f kg' % vehicle.results.mass_empty)
print('x cg %.3f m' % vehicle.results.x_center_of_gravity)
print('static margin %.1f ' % (100*vehicle.results.static_margin))
print('c_m_alpha %.3f' % vehicle.results.c_m_alpha)
print('percent mac %.3f' % vehicle.results.percent_mac)

vehicle = vehicle_setup(payload=3.91, main_wing_x=main_wing_x)
#vehicle.plot_vehicle(azim=230, elev=30)

print('-----------------------------------------')
print('payload %.2f kg' % vehicle.results.mass_payload)
print('mass empty %.2f kg' % vehicle.results.mass_empty)
print('x cg %.3f m' % vehicle.results.x_center_of_gravity)
print('static margin %.1f ' % (100*vehicle.results.static_margin))
print('c_m_alpha %.3f' % vehicle.results.c_m_alpha)
print('percent mac %.3f' % vehicle.results.percent_mac)

vehicle = vehicle_setup(payload=4.25, main_wing_x=main_wing_x)
#vehicle.plot_vehicle(azim=230, elev=30)

print('-----------------------------------------')
print('payload %.2f kg' % vehicle.results.mass_payload)
print('mass empty %.2f kg' % vehicle.results.mass_empty)
print('x cg %.3f m' % vehicle.results.x_center_of_gravity)
print('static margin %.1f ' % (100*vehicle.results.static_margin))
print('c_m_alpha %.3f' % vehicle.results.c_m_alpha)
print('percent mac %.3f' % vehicle.results.percent_mac)
print('-----------------------------------------')
