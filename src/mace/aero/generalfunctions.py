import numpy as np
from scipy.interpolate import interp1d

from mace.domain import params
from mace.domain.vehicle import Vehicle


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
    def __init__(self, plane: Vehicle):
        self.plane = plane
        self.mass = self.plane.mass
        self.s_ref = self.plane.reference_values.s_ref
        self.g = params.Constants.g
        self.rho = params.Constants.rho

    # ---Thrust in Newton---

    def current_thrust(self, V):
        """
        Returns thrust in Newton related to a current velocity of the plane.
        """
        thrust_array = self.plane.propulsion.thrust
        interp = interp1d(thrust_array[:, 0], thrust_array[:, 1], kind="quadratic",
                          fill_value=0, bounds_error=False)
        thrust = interp(V)
        return thrust

    def thrust_supply(self, cd, cl):  # Schubbedarf
        thrust = cd / cl * self.mass * self.g
        return thrust

    def excess_power(self, cd, cl, thrust):
        print(f'thrust_supply = {self.thrust_supply(cd, cl)}')
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



