from vehicle_setup import vehicle_setup
from mace.aero.implementations.aero import Aerodynamics as Aero
import numpy as np
import matplotlib.pyplot as plt

Vehicle = vehicle_setup()
Aero = Aero(Vehicle)

mass = 6.08
g = 9.81
rho = 1.225
S = 0.65


v_vec = np.linspace(10, 30, 10)
cl_vec = mass * g / (0.5 * rho * v_vec**2 * S)
cl_cd_vec = np.zeros_like(cl_vec)

for i, v in enumerate(v_vec):
    Aero.evaluate(CL=cl_vec[i], V=v)
    cd = Vehicle.aero_coeffs.drag_coeff.cd_tot
    cl_cd_vec[i] = cl_vec[i] / cd

plt.plot(v_vec, cl_cd_vec)
plt.show()
