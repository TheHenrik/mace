from mace.aero.implementations.airfoil_analyses import Airfoil
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import os

if __name__ == '__main__':
    airfoil_name = "ag40"
    re_list = [3e5, 6e5]
    cl_list = np.linspace(-0.5, 1.5, 60)
    flap_angle = 6

    airfoil = Airfoil(airfoil_name, flap_angle=flap_angle)
    airfoil.x_hinge = 0.75
    airfoil.re_list = re_list
    airfoil.build_surrogate()

    fig = plt.figure(dpi=400)
    ax = fig.add_subplot(111)

    for re in re_list:
        cdplot = []
        clplot = []
        for cl in cl_list:
            if cl < airfoil.get_cl_max(re):
                cdplot.append(airfoil.get_cd(re, cl))
                clplot.append(cl)
        ax.plot(cdplot, clplot, label="re="+str(int(re)))

    tool_path = Path(__file__).resolve().parents[2]
    if flap_angle == 6:
        reference_path = os.path.join(tool_path, "data", "reference_values", "T1_Re0.600_M0.00_N9.0_6f_2.csv")
        highre_ref = np.loadtxt(reference_path, delimiter=";")
        reference_path = os.path.join(tool_path, "data", "reference_values", "T1_Re0.300_M0.00_N9.0_6f_2.csv")
        lowre_ref = np.loadtxt(reference_path, delimiter=";")
    else:
        reference_path = os.path.join(tool_path, "data", "reference_values", "T1_Re0.600_M0.00_N9.0_2.csv")
        highre_ref = np.loadtxt(reference_path, delimiter=";")
        reference_path = os.path.join(tool_path, "data", "reference_values", "T1_Re0.300_M0.00_N9.0_2.csv")
        lowre_ref = np.loadtxt(reference_path, delimiter=";")
    ax.scatter(highre_ref[:, 1], highre_ref[:, 0], label="XFLR5", marker="x")
    ax.scatter(lowre_ref[:, 1], lowre_ref[:, 0], label="XFLR5", marker="x")
    ax.set_xlabel('cd')
    ax.set_ylabel('cl')
    ax.set_xlim(0, 0.06)
    plt.legend()
    plt.grid()
    plt.tick_params(which='major', labelsize=6)
    plt.title(airfoil_name, fontsize=10)
    plt.show()

