import os

import numpy as np
import scipy.interpolate as interp

from pymace.utils.file_path import root


class Propeller:
    def __init__(self, propeller_tag):
        tool_path = root()
        self.propeller_tag = propeller_tag
        self.surrogate_path = os.path.join(
            tool_path, "data", "prop_surrogates", propeller_tag + ".csv"
        )
        self.surrogate_delimiter = ","
        self.reference_voltage = 11.3
        self.reference_current = 30.0

    def evaluate_thrust(self, V):
        thrust_array = np.loadtxt(
            self.surrogate_path, skiprows=1, delimiter=self.surrogate_delimiter
        )
        thrust_force = interp.interp1d(
            thrust_array[:, 0],
            thrust_array[:, 1],
            kind="quadratic",
            fill_value=0.0,
            bounds_error=False,
        )(V)
        return thrust_force


if __name__ == "__main__":
    propeller_tag = "aeronaut16x8"
    prop = Propeller(propeller_tag)
    thrust_array = np.loadtxt(
        prop.surrogate_path, skiprows=1, delimiter=prop.surrogate_delimiter
    )

    import matplotlib.pyplot as plt

    x = np.linspace(0.0, 40.0, 100)
    y = np.zeros_like(x)
    for i, _ in enumerate(x):
        y[i] = prop.evaluate_thrust(x[i])
    plt.plot(x, y)
    plt.scatter(thrust_array[:, 0], thrust_array[:, 1])

    propeller_tag = "vm14x10"
    prop = Propeller(propeller_tag)
    thrust_array = np.loadtxt(
        prop.surrogate_path, skiprows=1, delimiter=prop.surrogate_delimiter
    )
    x = np.linspace(0.0, 40.0, 100)
    y = np.zeros_like(x)
    for i, _ in enumerate(x):
        y[i] = prop.evaluate_thrust(x[i])
    plt.plot(x, y)
    plt.scatter(thrust_array[:, 0], thrust_array[:, 1])
    plt.show()
