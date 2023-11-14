from pathlib import Path
import os
import numpy as np
import scipy.interpolate as interp

class Propeller:
    def __init__(self, propeller_tag):
        tool_path = Path(__file__).resolve().parents[3]
        self.propeller_tag = propeller_tag
        self.surrogate_path = os.path.join(tool_path, "data", "prop_surrogates", propeller_tag + ".csv")
        self.surrogate_delimiter = ","
        self.reference_voltage = 11.3
        self.reference_current = 30.

    def evaluate_thrust(self, V):
        thrust_array = np.loadtxt(self.surrogate_path, skiprows=1, delimiter=self.surrogate_delimiter)
        thrust_force = interp.interp1d(thrust_array[:, 0], thrust_array[:, 1],kind='linear')(V)
        return thrust_force

if __name__ == '__main__':
    propeller_tag = "aeronaut14x8"
    prop = Propeller(propeller_tag)

    import matplotlib.pyplot as plt
    x = np.linspace(0., 25., 100)
    y = np.zeros_like(x)
    for i, _ in enumerate(x):
        y[i] = prop.evaluate_thrust(x[i])
    plt.plot(x, y)
    plt.show()
