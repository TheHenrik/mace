from pathlib import Path
import os
import numpy as np
class battery_model:
    def __init__(self):
        tool_path = Path(__file__).resolve().parents[1]
        model = "bat_model_v1"

        self.surrogate_path = os.path.join(tool_path, "data", "battery_surrogates", model + ".csv")
        self.capacity = 3.0
        self.print_warnings = True

    def get_voltage(self, i, t):
        batt_data = np.loadtxt(self.surrogate_path, delimiter=";", skiprows=1)
        c_list = np.unique(batt_data[:, 0])
        print(c_list)
        c_rate = i / self.capacity
        soc = 1 - c_rate * t / 3600
        if c_rate > c_list[-1]:
            if self.print_warnings:
                print(
                    "Warning: C_Rate=%.0f above max C in surrogate model"
                    % (c_rate)
                )
            c_rate = c_list[-1]
        upper_c = c_list[np.where(c_list >= c_rate)[0][0]]
        if np.where(c_list >= c_rate)[0][0] == 0:
            lower_c = c_list[np.where(c_list >= c_rate)[0][0]]
            if self.print_warnings:
                print(
                    "Warning: C_Rate=%.0f below min C in surrogate model"
                    % (c_rate)
                )
        else:
            lower_c = c_list[np.where(c_list >= c_rate)[0][0] - 1]

        batt_data_upper = batt_data[np.where(batt_data[:, 0] == upper_c)[0], :]
        batt_data_lower = batt_data[np.where(batt_data[:, 0] == lower_c)[0], :]
        print(upper_c)
        print(lower_c)
        
        u_upper = np.interp(
            soc, batt_data_upper[:, 2], batt_data_upper[:, 3]#, left=2.0, right=0.0
        )
        u_lower = np.interp(
            soc, batt_data_lower[:, 2], batt_data_lower[:, 3]#, left=3.0, right=-1.0
        )
        #print(batt_data_lower[:, 2])
        # print(batt_data_lower[:, 3])
        print(batt_data_upper[:, 2])
        print('\n')
        print(batt_data_upper[:, 3])
        asdjpo = batt_data_upper[:, 2]
        wedfwe = batt_data_upper[:, 3]

        u = np.interp(c_rate, [lower_c, upper_c], [u_lower, u_upper])

        return u, soc



if __name__ == '__main__':
    model = battery_model()
    import matplotlib.pyplot as plt

    t = np.linspace(5, 100., 1)
    u = np.zeros_like(t)
    soc = np.zeros_like(t)

    for i in range(len(t)):
        u[i], soc[i] = model.get_voltage(i=30., t=t[i])

    plt.plot(t, soc)
    plt.show()