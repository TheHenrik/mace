import os

import numpy as np
import scipy.interpolate as interp

from pymace.utils.file_path import root


class Battery:
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
        self.origin = np.array([0.0, 0.0, 0.0])

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
