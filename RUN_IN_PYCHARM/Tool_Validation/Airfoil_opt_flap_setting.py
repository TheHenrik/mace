from mace.aero.implementations.airfoil_analyses import Airfoil
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os

tool_path = Path(__file__).resolve().parents[2]

# for i in range(len(airfoil.re_list)):
#     polar = np.loadtxt(airfoil.surrogate_path, delimiter=",", skiprows=1)
#     polar_re = polar[np.where(polar[:, 0] == airfoil.re_list[i])[0], :]
#     plt.figure()
#     plt.scatter(polar_re[:, 3], polar_re[:, 2], label='optimized', marker='x')
#
#     for flap_angle in airfoil.flap_angle_list:
#         surrogate_path = os.path.join(tool_path, "data", "surrogates",
#                                            airfoil.foil_name
#                                            + "_"
#                                            + str(int(round((100 - airfoil.x_hinge * 100), 0)))
#                                            + "f" +
#                                            str(int(round(flap_angle, 0))) + ".csv")
#         polar = np.loadtxt(surrogate_path, delimiter=",", skiprows=1)
#         polar_re = polar[np.where(polar[:, 0] == airfoil.re_list[i])[0], :]
#         plt.plot(polar_re[:, 3], polar_re[:, 2], label=str(int(round(flap_angle, 0))) + " deg")
#     plt.legend()
#     plt.show()

re = 970000

airfoil = Airfoil("ag19")
cl_min = airfoil.get_cl_min(re)
cl_max = airfoil.get_cl_max(re)
cls = np.linspace(cl_min, cl_max, 50)
cds = np.zeros_like(cls)

for i, cl in enumerate(cls):
    best_flap_angle = airfoil.check_for_best_flap_setting(re, cl)
    print("cl: %.2f, flap angle: %.2f" % (cl, best_flap_angle))
    airfoil = Airfoil("ag19", flap_angle=best_flap_angle)
    cds[i] = airfoil.get_cd(re, cl)

plt.figure()
airfoil = Airfoil("ag19", use_opt_flap_setting=True)
polar = np.loadtxt(airfoil.surrogate_path, delimiter=",", skiprows=1)
polar_re = polar[np.where(polar[:, 0] == re)[0], :]
plt.plot(polar_re[:, 3], polar_re[:, 2], label="optimized")
plt.scatter(cds, cls)
plt.show()
