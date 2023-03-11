from mace.domain import params, Plane

# ---lineare Interpolation---


# einfach
def lin_interpol(x,x1,y1,x2,y2):
    y = y1 + (x - x1) * ((y2 - y1)/(x2 - x1))

    return y

# Scipy (example)
from scipy.interpolate import interp1d

X = [1, 2, 3, 4, 5]  # random x values
Y = [11, 2.2, 3.5, -88, 1]  # random y values

interpolate_x = 2.5  # test Value

y_interp = interp1d(X, Y)  # interpolation
print("Value of Y at x = {} is".format(interpolate_x),
      y_interp(interpolate_x))

# Numpy (example)
import numpy as np
x = np.linspace(0, 10, num=11)  # random x values
y = np.cos(-x**2 / 9.0)  # random y values

xnew = np.linspace(0, 10, num=1001)
ynew = np.interp(xnew, x, y)  # interpolation


# ---Reynoldsnumber---

def get_reynolds_number(v, length):              # neuer Name
    rey = (v * length) / params.Constants.ny
    return rey

# ------------------------


class GeneralFunctions:
    def __init__(self, plane: Plane):
        self.plane = plane

    # ---Thrust in Newton---

    def current_thrust(self, current_velocity):
        """
        Returns thrust in Newton related to a current velocity of the plane.
        """
        velocity_arr = self.plane.propulsion.thrust[0, :]
        thrust_arr = self.plane.propulsion.thrust[1, :]
        thrust = np.interp(current_velocity, velocity_arr, thrust_arr)
        return thrust

    # ---Lift---

    def coefficient_to_lift_or_drag(self, velocity, coefficient):
        """
        Returns the lift/drag at given velocity and lift/drag coefficient.
        """
        s_ref = self.plane.reference_values.s_ref
        rho = params.Constants.rho
        lift = coefficient * rho / 2 * velocity**2 * s_ref
        return lift



# ---Polaren erstellen---


def gen_polar(re):
    pass


def get_coeffs():
    pass

