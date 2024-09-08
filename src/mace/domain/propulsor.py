import numpy as np

from mace.utils.file_path import root


class Propulsor:
    def __init__(self):
        self.thrust_array: np.ndarray = None
        self.battery_capacity: float = None

    def get_thrust_force(self, velocity: float, current: float, time: float):
        thrust_force = np.interp(
            velocity, self.thrust_array[:, 0], self.thrust_array[:, 1]
        )

        return thrust_force

    def get_battery_voltage(self, current: float, time: float):
        C_rate = current / self.battery_capacity

        a = -0.262388
        b = 12.665
        battery_voltage = a * np.log(C_rate) + b

        return battery_voltage


if __name__ == "__main__":
    prop = Propulsor()
    prop.battery_capacity = 2.5

    import os

    tool_path = root()
    prop_surrogate_path = os.path.join(
        tool_path, "data", "prop_surrogates", "aeronaut14x8.csv"
    )
    prop.thrust_array = np.loadtxt(prop_surrogate_path, skiprows=1)

    import matplotlib.pyplot as plt

    x = np.linspace(2.5, 15 * 2.5, 100)
    y = prop.get_battery_voltage(x, 0)
    plt.plot(x, y)
    plt.show()
