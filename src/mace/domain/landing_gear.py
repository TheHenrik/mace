import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from mace.domain import params


class Wheel:
    def __init__(self):
        self.mass: float = 0.
        self.origin: np.ndarray = np.array([0., 0., 0.])
        self.diameter: float = 0.

    def get_drag_coefficient(self, V, S_ref):
        Re_L = V * np.pi / 4 * self.diameter / params.Constants.ny
        if Re_L == 0:
            Re_L = 1000
        C_D_wet = 0.074 / Re_L**0.2
        C_D_wheel = 2 * C_D_wet * np.pi * self.diameter**2 / 4 / S_ref
        return C_D_wheel

class LandingGear:
    def __init__(self):
        self.mass: float = 0.
        self.center_of_gravity: np.ndarray = np.array([0., 0., 0.])
        self.wheels: List[Wheel] = []
        self.height: float = 0.

    def add_wheel(self, wheel: Wheel):
        self.wheels.append(wheel)

    def finalize(self):
        for wheel in self.wheels:
            self.mass += wheel.mass
            self.center_of_gravity += wheel.mass * wheel.origin
        self.center_of_gravity /= self.mass

    def plot(self, color='b'):
        for wheel in self.wheels:
            theta = np.linspace(0, 2 * np.pi, 201)
            x = wheel.diameter/2 * np.cos(theta) + wheel.origin[0]
            y = wheel.origin[1] * np.ones_like(theta)
            z = wheel.diameter/2 * np.sin(theta) + wheel.origin[2]
            plt.plot(x, y, z, color=color)

if __name__ == '__main__':
    landing_gear = LandingGear()

    wheel1 = Wheel()
    wheel1.diameter = 0.1
    wheel1.mass = 0.05
    wheel1.origin = np.array([0., 0., 0.])
    landing_gear.add_wheel(wheel1)

    wheel2 = Wheel()
    wheel2.diameter = 0.1
    wheel2.mass = 0.05
    wheel2.origin = np.array([0.1, 0.1, 0.])
    landing_gear.add_wheel(wheel2)

    landing_gear.finalize()

    fig = plt.figure(dpi=400)
    ax = fig.add_subplot(111, projection='3d')

    landing_gear.plot()
    
    plt.show()
