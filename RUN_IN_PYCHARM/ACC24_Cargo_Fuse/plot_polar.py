import numpy as np
from mace.aero.implementations.aero import Aerodynamics as Aero
from vehicle_setup import *

vehicle = vehicle_setup()
polar = Aero(vehicle)

mass = 2.7 + 17 * 0.17
flap = 0
v = np.linspace(10, 50, 10)
cl = mass * 9.81 / (0.5 * 1.2 * v ** 2 * 0.65)
cd = np.zeros_like(cl)

for i, cli in enumerate(cl):
    polar.evaluate(CL=cli, V=v[i], FLAP=flap)
    cd[i] = polar.plane.aero_coeffs.drag_coeff.cd_tot

import matplotlib.pyplot as plt

plt.plot(cd, cl)
plt.show()
#
# alphas = np.linspace(0, 10, 10)
# cl2 = np.zeros_like(alphas)
# for i, alpha in enumerate(alphas):
#     polar.evaluate(CL=0, V=20, FLAP=flap, ALPHA=alpha)
#     cl2[i] = polar.plane.aero_coeffs.lift_coeff.cl_tot
#
# plt.plot(alphas, cl2)
# plt.show()