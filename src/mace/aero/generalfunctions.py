from mace.domain import params

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


# ---Re-Zahl---

def get_reynolds_number(v, length):              # neuer Name
    rey = (v * length) / params.Constants.ny
    return rey

# ---Polaren erstellen---


def gen_polar(re):
    pass


def get_coeffs():
    pass

