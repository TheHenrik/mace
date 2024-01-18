def evaluate_points(distance, energy):
    return distance**2 / (energy + 2 * distance)

h0 = 2.47 * 19.8

v_motor_on = 18.
t_motor_on = 90.
i_motor_on = 6.

v_motor_off = 16.


t_motor_off = 90.0 - t_motor_on
distance = (v_motor_on * t_motor_on + v_motor_off * t_motor_off) / 1000
energy = i_motor_on * 11.5 * t_motor_on / 3600
points = evaluate_points(distance, energy)
print('t motor on', t_motor_on)
print('Points', points)

# 0.675 abgleiten
# 0.5575 nur möglichst kurze motorlaufzeit

