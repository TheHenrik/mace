from mace.domain import params, Plane
from mace.aero.implementations.avl import athenavortexlattice, geometry_and_mass_files
from mace.aero.implementations.viscousdrag import ViscousDrag
import numpy as np


# ---lineare Interpolation---


# einfach
"""def lin_interpol(x,x1,y1,x2,y2):
    y = y1 + (x - x1) * ((y2 - y1)/(x2 - x1))

    return y
"""
# Scipy (example)
"""from scipy.interpolate import interp1d

X = [1, 2, 3, 4, 5]  # random x values
Y = [11, 2.2, 3.5, -88, 1]  # random y values

interpolate_x = 2.5  # test Value

y_interp = interp1d(X, Y)  # interpolation"""
# print("Value of Y at x = {} is".format(interpolate_x),
#       y_interp(interpolate_x))

# Numpy (example)
"""
x = np.linspace(0, 10, num=11)  # random x values
y = np.cos(-x**2 / 9.0)  # random y values

xnew = np.linspace(0, 10, num=1001)
ynew = np.interp(xnew, x, y)  # interpolation"""


# ---lineare Schnittpunkte---

def get_intersect(a1, a2, b1, b2):
    """
    Returns the point of intersection of the lines passing through a2,a1 and b2,b1.
    a1: [x, y] a point on the first line
    a2: [x, y] another point on the first line
    b1: [x, y] a point on the second line
    b2: [x, y] another point on the second line
    """
    s = np.vstack([a1, a2, b1, b2])            # s for stacked
    h = np.hstack((s, np.ones((4, 1))))     # h for homogeneous
    l1 = np.cross(h[0], h[1])               # get first line
    l2 = np.cross(h[2], h[3])               # get second line
    x, y, z = np.cross(l1, l2)              # point of intersection
    if z == 0:                              # lines are parallel
        return float('inf'), float('inf')
    return x / z, y / z


# ---Reynoldsnumber---

def get_reynolds_number(v, length):              # neuer Name
    rey = (v * length) / params.Constants.ny
    return rey

# ------------------------


class GeneralFunctions:
    def __init__(self, plane: Plane):
        self.plane = plane
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho

    # ---Thrust in Newton---

    def current_thrust(self, current_velocity):
        """
        Returns thrust in Newton related to a current velocity of the plane.
        """
        velocity_arr = self.plane.propulsion.thrust[:, 0]
        thrust_arr = self.plane.propulsion.thrust[:, 1]
        print(f'velocity_array: {velocity_arr}, thrust_array: {thrust_arr}')
        thrust = np.interp(current_velocity, velocity_arr, thrust_arr)
        return thrust

    def thrust_supply(self, cd, cl):  # Schubbedarf
        thrust = cd / cl * self.mass * self.g
        return thrust

    def excess_power(self, cd, cl, thrust):
        excess_power = thrust - self.thrust_supply(cd, cl)
        return excess_power

    # ---Lift---

    def coefficient_to_lift_or_drag(self, velocity, coefficient):
        """
        Returns the lift/drag at given velocity and lift/drag coefficient.
        """
        s_ref = self.plane.reference_values.s_ref
        rho = params.Constants.rho
        lift = coefficient * rho / 2 * velocity**2 * s_ref
        return lift

    def calcualate_drag(self, lift_coefficient, *, velocity):
        # AVL
        geometry_and_mass_files.GeometryFile(self.plane).build_geometry_file(
            self.plane.reference_values.number_of_surfaces)
        geometry_and_mass_files.MassFile(self.plane).build_mass_file()
        athenavortexlattice.AVL(self.plane).run_avl(lift_coefficient=lift_coefficient)
        athenavortexlattice.AVL(self.plane).read_avl_output()
        # Viscous drag
        if velocity:
            ViscousDrag(self.plane).create_avl_viscous_drag_from_xfoil(velocity=velocity)
        else:
            ViscousDrag(self.plane).create_avl_viscous_drag_from_xfoil()
        cd = self.plane.aero_coeffs.drag_coeff.cd_viscous + self.plane.aero_coeffs.drag_coeff.cd_ind
        return cd

# ---Polaren erstellen---


def gen_polar(re):
    pass


def get_coeffs():
    pass

