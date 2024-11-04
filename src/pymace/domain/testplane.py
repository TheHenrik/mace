import numpy as np

from pymace.domain import plane

# --- Airfoil ---
a_airfoil_file = plane.AirfoilFile(
    filepath="C:/Users/Gregor/Documents/GitHub/mace/data/airfoils/n0012"
)
a_Airfoil = plane.Airfoil(type=plane.AirfoilFile(a_airfoil_file.filepath))

# --- Wing ---
# segment1
nose_inner = np.array([0.0, 100.0, 0.0])
nose_outer = np.array([0.0, 100.0, 100.0])
back_inner = np.array([100.0, 100.0, 0.0])
back_outer = np.array([100.0, 100.0, 100.0])
a_inc = 0
a_inc_outer = 0
inner_airfoil = a_Airfoil
outer_airfoil = a_Airfoil
wingsegment1 = plane.WingSegment(
    nose_inner=nose_inner,
    nose_outer=nose_outer,
    back_inner=back_inner,
    back_outer=back_outer,
    a_inc=a_inc,
    a_inc_outer=a_inc_outer,
    inner_airfoil=inner_airfoil,
    outer_airfoil=outer_airfoil,
)


segments = [wingsegment1]
wing = plane.Wing(segments=segments)

# --- Propulsion ---
thrust: np.ndarray = np.array(
    [[0, 20], [5, 19], [10, 18], [15, 16], [20, 14], [30, 10], [50, 5]]
)
# [[v0, f0], [v1, f1], [v2, f2], [v3, f3], ...]
propulsion = plane.Propulsion(thrust=thrust)

# --- Plane ---
name = "testplane"
mass = 5
testplane = plane.Plane(name=name, wing=wing, mass=mass, propulsion=propulsion)
