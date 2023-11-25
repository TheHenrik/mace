import os
from pathlib import Path

import numpy as np
import scipy.interpolate as interp

from mace.utils.file_path import root


class battery_model:
    def __init__(self):
        tool_path = root()
        model = "bat_model_v1"

        self.surrogate_path = os.path.join(
            tool_path, "data", "battery_surrogates", model + ".csv"
        )
        self.capacity = 3.0
        self.print_warnings = False

        self.capacity_specific_mass = 0.0776
        self.mass_offset = 0.0272

    def get_voltage(self, i, t):
        # Correction to account slow current increase (wrong esc setting during measurement)
        t = t + 5.0

        # Surrogate
        batt_data = np.loadtxt(self.surrogate_path, delimiter=";", skiprows=1)
        c_list = np.unique(batt_data[:, 0])
        c_rate = i / self.capacity
        soc = 1 - c_rate * t / 3600

        if c_rate > c_list[-1]:
            if self.print_warnings:
                print("Warning: C_Rate=%.0f above max C in surrogate model" % (c_rate))
            upper_c = c_list[-1]
            lower_c = c_list[-2]
        elif c_rate < c_list[0] == 0:
            if self.print_warnings:
                print("Warning: C_Rate=%.0f below min C in surrogate model" % (c_rate))
            lower_c = c_list[np.where(c_list >= c_rate)[0][0]]
            upper_c = c_list[np.where(c_list >= c_rate)[0][0] + 1]
        else:
            lower_c = c_list[np.where(c_list >= c_rate)[0][0] - 1]
            upper_c = c_list[np.where(c_list >= c_rate)[0][0]]

        batt_data_upper = batt_data[np.where(batt_data[:, 0] == upper_c)[0], :]
        batt_data_lower = batt_data[np.where(batt_data[:, 0] == lower_c)[0], :]

        # Interpolate
        u_upper = interp.interp1d(
            batt_data_upper[:, 2],
            batt_data_upper[:, 3],
            fill_value="extrapolate",
            kind="linear",
        )(soc)
        u_lower = interp.interp1d(
            batt_data_lower[:, 2],
            batt_data_lower[:, 3],
            fill_value="extrapolate",
            kind="linear",
        )(soc)
        u = u_upper + (u_lower - u_upper) * (c_rate - upper_c) / (lower_c - upper_c)
        return u, soc

    def get_mass(self):
        return self.capacity_specific_mass * self.capacity + self.mass_offset


# Validation
if __name__ == "__main__":
    model1 = battery_model()
    model1.capacity = 3.0

    model2 = battery_model()
    model2.capacity = 2.4
    print(model2.get_mass())
    import matplotlib.pyplot as plt

    T_ref = 17.837
    u_ref = 11.35

    t = np.linspace(0, 220.0, 100)
    u = np.zeros_like(t)
    soc = np.zeros_like(t)
    F = np.zeros_like(t)
    u2 = np.zeros_like(t)
    soc2 = np.zeros_like(t)

    for i in range(len(t)):
        u[i], soc[i] = model1.get_voltage(i=30.0, t=t[i])
        u2[i], soc2[i] = model2.get_voltage(i=30.0, t=t[i])

    F = T_ref * u / u_ref
    # plt.plot(t, F, label="calculated 3000mAh", color="blue")

    F2 = T_ref * u2 / u_ref
    # plt.plot(t, F2, label="calculated 2400mAh", color="red")

    plt.plot(t, u2, label="calculated 2400mAh", color="red")
    plt.plot(t, u, label="calculated 3000mAh", color="blue")

    tool_path = root()
    reference_data_path_1 = os.path.join(
        tool_path, "data", "battery_surrogates", "thrust_measurement_3000mAh.csv"
    )
    reference_data_1 = np.loadtxt(reference_data_path_1, delimiter=",", skiprows=1)

    reference_data_path_2 = os.path.join(
        tool_path, "data", "battery_surrogates", "thrust_measurement_2400mAh.csv"
    )
    reference_data_2 = np.loadtxt(reference_data_path_2, delimiter=",", skiprows=1)

    reference_data_path_3 = os.path.join(
        tool_path, "data", "battery_surrogates", "voltage_measurement_2400mAh.csv"
    )
    reference_data_3 = np.loadtxt(reference_data_path_3, delimiter=",", skiprows=1)

    reference_data_path_4 = os.path.join(
        tool_path, "data", "battery_surrogates", "voltage_measurement_3000mAh.csv"
    )
    reference_data_4 = np.loadtxt(reference_data_path_4, delimiter=",", skiprows=1)

    # plt.scatter(reference_data_1[:, 0], reference_data_1[:, 1], label="measured thrust 3000mAh", color="blue")
    # plt.scatter(reference_data_2[:, 0], reference_data_2[:, 1], label="measured thrust 2400mAh", color="red")
    plt.plot(
        reference_data_3[:, 0],
        reference_data_3[:, 1],
        label="measurement voltage 2400mAh",
        linestyle="--",
        color="red",
    )
    plt.plot(
        reference_data_4[:, 0],
        reference_data_4[:, 1],
        label="measurement voltage 3000mAh",
        linestyle="--",
        color="blue",
    )

    plt.legend()
    plt.show()

    # capacities = [1.7, 2.0, 2.5, 3.0]
    #
    # for capacity in capacities:
    #     model = battery_model()
    #     model.capacity = capacity
    #     u = np.zeros_like(t)
    #     soc = np.zeros_like(t)
    #     for i in range(len(t)):
    #         u[i], soc[i] = model.get_voltage(i=30., t=t[i])
    #     F = T_ref * u / u_ref
    #     plt.plot(t, F, label="calculated %imAh" % (capacity*1000), color="blue")
    #
    # Fmax = T_ref * 12.6 / u_ref * np.ones_like(t)
    # plt.plot(t, Fmax, label="max thrust", color="black")
    # plt.legend()
    # plt.show()
