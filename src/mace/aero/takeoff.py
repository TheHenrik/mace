import numpy as np
import math
import datatypes
from mace.domain import params as par
from mace.domain import plane as pl

# ---Strecken- und Zeitinkremente---


def delta_x(m, v1, v2, f, w, r):                        # Masse, Start-, Endgeschwindigkeit, F(V), W(V), R(V)
    del_x = (m * (v2**2 - v1**2)) / (2 * (f - w - r))
    return del_x


def delta_t(m, v1, v2, f, w, r):                        # Masse, Start-, Endgeschwindigkeit, F(V), W(V), R(V)
    del_t = (m * (v2 - v1)) / (f - w - r)
    return del_t


# ---Kräfte---

# (eventuell noch nach Matrix umschreiben, Schema bleibt identisch)
def schub(v, fv, ff):                       # aktuelle Geschwindigkeit, Datenpunkte Geschwindigkeit, Datenpunte Schub
    f = np.interp(v, fv, ff)
    return f


def auftrieb(ca_roll, rho, v, s_ref):      # CA beim Rollen, Luftdichte, aktuelle Geschwindigkeit, Referenzflügelfläche
    a = ca_roll * rho / 2 * v**2 *s_ref
    return a


def widerstand(cw_profil, cwi, phi_a, phi_w):   # CW des Profils beim Rollen, induzierter Widerstand, Phi_a, Phi_W
    cw_roll = cw_profil + cwi * phi_a**2 * phi_w
    return cw_roll


# ---Bodeneffekt---

# delta (für elliptischen Flügel sind delta_a = delta_w = 1)
def delta_a(lambd_k, lambd_g):                                                  # Zuspitzung, Streckung
    delt = 1 - 2.25 * (lambd_k**0.00273 - 0.997) * (lambd_g**0.717 + 13.6)
    return delt


def delta_w(lambd_k, lambd_g):                                                 # Zuspitzung, Streckung
    delt = 1 - 0.157 * (lambd_k**0.775 - 0.373) * (lambd_g**0.417 + 1.27)
    return delt


# beta
def beta_a(ca, lambd_g, h, b):          # CA beim Rollen, Streckung, Höhe des FlügelNP über Boden, Spannweite
    b_a = 1 + ((0.269 * ca**(1.45))/(lambd_g**(3.18) * (h/b)**1.12))
    return b_a


def beta_w(ca, lambd_g, h, b):          # CA beim Rollen, Streckung, Höhe des FlügelNP über Boden, Spannweite
    b_a = 1 + ((0.0361 * ca**(1.21))/(lambd_g**(1.19) * (h/b)**1.51))
    return b_a


# ---Reibung---


def reibung(my, m, g, a):          # Rollreibungskoeffizient, Masse, Gravitationskonstante, aktueller Auftrieb
    r = my * (m * g - a)
    return r


# phi (für elliptischen Flügel sind delta_a = delta_w = 1)
def phi_a(beta_a, delta_a, h, b, lambd_g):      # beta_a, delta_a, Höhe des FlügelNP über Boden, Spannweite, Streckung
    phi = (1/beta_a) * (1 + delta_a * (288*(h/b)**0.787)/(lambd_g**0.882) * math.exp(-9.14 * (h/b)**0.327))
    return phi


def phi_w(beta_w, delta_w, h, b):      # beta_w, delta_w, Höhe des FlügelNP über Boden, Spannweite
    phi = beta_w * (1 - delta_w * math.exp(-4.74 * (h/b)**0.814) - (h/b)**2 * math.exp(-3.88 * (h/b)**0.758))
    return phi


# ---Ermittlung der Abhebegeschwindigkeit---


def v_start(v_min, phi_a):
    v_takeoff = v_min * (1/phi_a)**0.5
    return v_takeoff


# ---------------------------------------------
# ---------------------------------------------

def takeoff(v0, v_min, num, g, rho, fv, ff, m, my, h, b, s_ref, lambd_k, lambd_g, ca_roll, ca_abheb, cw_profil, cwi):

    res_takeoff = datatypes.ResTakeoff

    vstart = v_start(v_min, phi_a(beta_a(ca_abheb, lambd_g, h, b), delta_a(lambd_k, lambd_g), h, b, lambd_g))

    res_takeoff.distance = 0
    res_takeoff.time = 0

    for element in np.linspace(v0, vstart, num):       # v0 = 0, v_start, Anzahl der Inkremente für Diskretisierung
        v1 = element
        v2 = element + (vstart - v0) / num
        v = element + (vstart - v0) / (2 * num)

        f = schub(v, fv, ff)

        betaa = beta_a(ca_roll, lambd_g, h, b)
        deltaa = delta_a(lambd_k, lambd_g)
        phia = phi_a(betaa, deltaa, h, b, lambd_g)

        betaw = beta_w(ca_roll, lambd_g, h, b)
        deltaw = delta_w(lambd_k, lambd_g)
        phiw = phi_w(betaw, deltaw, h, b)

        w = widerstand(cw_profil, cwi, phia, phiw)

        a = auftrieb(ca_roll, rho, v, s_ref)
        r = reibung(my, m, g, a)

        if delta_x(m, v1, v2, f, w, r) <= 0:
            res_takeoff.vrollmax = v1
            res_takeoff.distance = False
            res_takeoff.time = False
            return res_takeoff

        res_takeoff.distance += delta_x(m, v1, v2, f, w, r)
        res_takeoff.time += delta_t(m, v1, v2, f, w, r)

    res_takeoff.vrollmax = False
    return res_takeoff

# Auftrieb muss kleiner als Gewichtskraft sein!

# --------------------------------
# ---Test---
# --------------------------------


if __name__ == "__main__":

    p = pl.Plane

    # ---filling Plane with test values---
    LG = pl.LandingGear
    p.landing_gear = LG

    gwv = pl.GeometricWingValues
    wg = pl.Wing
    wg.geo_wing_values = gwv
    p.wing = wg

    lc = pl.Ca
    ac = pl.AeroCoeffs
    ac.lift_coeff = lc
    p.aero_coeffs = ac

    dc = pl.Cw
    ac = pl.AeroCoeffs
    ac.drag_coeff = dc
    p.aero_coeffs = ac

    # ------

    v0 = 0
    v_min = 10
    num = 10
    g = par.Constants.g
    rho = par.Constants.rho
    fv = np.array([0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20])
    ff = np.array([14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4])
    m = p.mass
    my = p.landing_gear.my
    h = p.wing.geo_wing_values.h
    b = p.wing.geo_wing_values.b
    s_ref = p.wing.geo_wing_values.s_ref
    lambd_k = p.wing.geo_wing_values.lambd_k
    lambd_g = p.wing.geo_wing_values.lambd_g
    ca_roll = p.aero_coeffs.lift_coeff.ca_roll
    ca_abheb = p.aero_coeffs.lift_coeff.ca_abheb
    cw_profil = p.aero_coeffs.drag_coeff.cw_profil
    cwi = p.aero_coeffs.drag_coeff.cwi


res = takeoff(v0, v_min, num, g, rho, fv, ff, m, my, h, b, s_ref, lambd_k, lambd_g, ca_roll, ca_abheb, cw_profil, cwi)
print(res.distance)

# Zeitmessung muss noch verbessert werden
