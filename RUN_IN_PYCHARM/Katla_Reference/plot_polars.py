from vehicle_setup import vehicle_setup
from mace.aero.implementations.aero import Aerodynamics
from mace.domain.params import Constants as cnst
import numpy as np
import matplotlib.pyplot as plt


if __name__ == '__main__':
    vehicle = vehicle_setup()

    Aero = Aerodynamics(vehicle)
    
    print('Wing area ', vehicle.wings['main_wing'].reference_area)

    ref_data = np.loadtxt('T2-VLM2-2_3kg-x0_0m_OnlyWing.csv', skiprows=7, delimiter=',')
    plt.plot(ref_data[:,3], ref_data[:,2], label='XFLR5-induced')
    plt.plot(ref_data[:,4], ref_data[:,2], label='XFLR5-visc')


    cl_list = np.linspace(0.01, 1.2, 30)
    cd_list = np.zeros_like(cl_list)
    cd_ind = np.zeros_like(cl_list)
    cd_visc = np.zeros_like(cl_list)

    mass = 2.25
    v_list = (2 * mass * 9.81 / cnst.rho / vehicle.wings['main_wing'].reference_area / cl_list)**0.5
    #v_list = 15. * np.ones_like(cl_list)

    for i, cl in enumerate(cl_list):
        Aero.evaluate(cl, v_list[i], 0)
        cd_ind[i] = Aero.plane.aero_coeffs.drag_coeff.cd_ind
        cd_visc[i] = Aero.plane.aero_coeffs.drag_coeff.cd_visc / 1.09
        cd_list[i] = Aero.plane.aero_coeffs.drag_coeff.cd_ind + cd_visc[i]

    plt.plot(cd_ind, cl_list, label='MACE-induced')
    plt.plot(cd_visc, cl_list, label='MACE-visc')

    plt.grid('on')
    plt.xlabel(r'$c_D$')
    plt.ylabel(r'$c_L$')
    plt.axis([0, 0.1, -0.2, 1.1])
    plt.legend()
    plt.show()

    L_D_mace = cl_list/cd_list
    L_D_xflr = ref_data[:,2] / ref_data[:,5]
    # plt.plot(ref_data[:,5], ref_data[:,2], label="XFLR5")
    # plt.plot(cd_list, cl_list, label="MACE")
    plt.plot(ref_data[:, 2], L_D_xflr, label="XFLR5")
    plt.plot(cl_list, L_D_mace, label="MACE")
    plt.grid('on')
    plt.legend()
    plt.show()
