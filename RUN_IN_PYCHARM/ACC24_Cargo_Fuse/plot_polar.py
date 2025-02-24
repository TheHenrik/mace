import numpy as np
from mace.aero.implementations.aero import Aerodynamics as Aero
from vehicle_setup import *
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt

vehicle = vehicle_setup()
polar = Aero(vehicle)

flap_vec = [-4, 0, 4, 8, 12]
v = np.linspace(6, 45, 20)

mass = 2.7 + 10 * 0.17
cl = mass * 9.81 / (0.5 * 1.225 * v ** 2 * 0.65)

cd_fuse = np.zeros((len(v), len(flap_vec)))
cd_fuse_w_induced = np.zeros((len(v), len(flap_vec)))
cd_tot = np.zeros((len(v), len(flap_vec)))

# Diagramm erstellen
fig, ax = plt.subplots()

# Dicke und Farbe der Achsenlinien ändern
ax.spines['left'].set_linewidth(2)  # Y-Achse
ax.spines['left'].set_color('black')  # Y-Achse Farbe
ax.spines['bottom'].set_linewidth(2)  # X-Achse
ax.spines['bottom'].set_color('black')  # X-Achse Farbe


for j, flap in enumerate(flap_vec):
    print(f'Flap: {flap}')

    cd_fuse_w_induced[:,j]        = np.zeros_like(cl)
    cd_fuse[:,j]     = np.zeros_like(cl)
    cd_tot[:,j]     = np.zeros_like(cl)

    for i, cli in enumerate(cl):
        polar.evaluate(CL=cli, V=v[i], FLAP=flap)
        cd_fuse[i,j] = polar.plane.aero_coeffs.drag_coeff.cd_fuse
        cd_fuse_w_induced[i,j] = polar.plane.aero_coeffs.drag_coeff.cd_fuse + polar.plane.aero_coeffs.drag_coeff.cd_ind
        cd_tot[i,j] = polar.plane.aero_coeffs.drag_coeff.cd_tot



    if j==0:
        plt.plot(cd_fuse[:,0], cl, label='Fuselage', color='orange', linewidth=2)
        plt.plot(cd_fuse_w_induced[:,0], cl, label='Fuselage + Induced', color='blue', linewidth=2)
        plt.plot(cd_tot[:, j], cl, linestyle='dotted', label='Fuselage + Induced + Airfoil Viscous (Single Flap)',
                 color='grey', linewidth=0.4)
    else:
        plt.plot(cd_tot[:,j], cl, linestyle='dotted', color='grey', linewidth=2)

print('cl')
print(cl)
print('cd_tot')
print(cd_tot[:,0])

plt.plot(np.min(cd_tot, axis=1), cl, color='red', label='Fuselage + Induced + Airfoil Visc. (Flaps optimized)', linewidth=2)
plt.xlabel(r'$C_D$', fontsize=12)
plt.ylabel(r'$C_L$', fontsize=12)
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)
plt.legend(fontsize=10, loc='lower right')  # (1, 1) gibt die Position der Legende an
plt.axis([0, 0.1, 0, 1.5])
plt.grid()
plt.savefig('polar.pdf')
plt.show()