import math

import numpy as np


# ---Kurvengeschwindigkeit---


def kurvengeschwindigkeit(m, g, rho, s_ref, ca, phi):
    v_k = ((2 * m * g) / (rho * s_ref * ca * math.cos(phi)))**0.5
    return v_k


def min_kurvengeschw(m, g, rho , s_ref, ca_max, phi):
    v_k_min = kurvengeschwindigkeit(m, g, rho , s_ref, ca_max, phi)
    return v_k_min


# ---Kurvenradius---
# Achtung Winkel sind noch in Rad

def check_mode():
    pass


def kurvenradius(arg1, arg2, mode, masse) -> (float, float, float, float, float):
    """This fuction recieves 2 input parameters and returns a tupel with all 5 turning flight defining parameters.
    (velocity, radius of turning flight, lift coefficient, load faktor, rolling angle)

    Mode 1: v and r_k
    Mode 2: v and ca
    Mode 3: v and n
    Mode 4: v and phi
    Mode 5: r_k and ca
    Mode 6: r_k and n
    Mode 7: r_k and phi
    Mode 8: ca and n
    Mode 9: ca and phi
    Mode 10: n and phi"""
# umschreiben zu z.B. if v is not None and r_k is not none:
    m = masse

    if mode == 1:                           # v, r_k
        v = arg1
        r_k = arg2
        n = ((v**2) / (g * r_k))**2 + 1
        phi = math.acos(1/n)
        ca = (2 * m) / (rho * s_ref * r_k * (1/n) * (n**2 - 1)**0.5)
        return arg1, arg2, ca, n, phi

    elif mode == 2:                         # v, ca
        v = arg1
        ca = arg2
        n = (ca * rho/2 * v**2 * s_ref) / (m * g)
        phi = math.acos(1 / n)
        r_k = (v**2) / (g * (n**2 - 1)**0.5)
        return arg1, r_k, arg2, n, phi

    elif mode == 3:                         # v, n
        v = arg1
        n = arg2
        r_k = (v**2) / (g * (n**2 - 1)**0.5)
        phi = math.acos(1 / n)
        ca = (2 * m) / (rho * s_ref * r_k * (1 / n) * (n ** 2 - 1) ** 0.5)
        return arg1, r_k, ca, arg2, phi

    elif mode == 4:                         # v, phi
        v = arg1
        phi = arg2
        n = 1 / math.cos(phi)
        r_k = (v ** 2) / (g * (n ** 2 - 1) ** 0.5)
        ca = (2 * m) / (rho * s_ref * r_k * (1 / n) * (n ** 2 - 1) ** 0.5)
        return arg1, r_k, ca, n, arg2

    elif mode == 5:                         # r_k, ca
        r_k = arg1
        ca = arg2
        cos_phi = (1 - (2 * m) / (rho * s_ref * ca * r_k))**0.5
        phi = math.acos((1 - (2 * m) / (rho * s_ref * ca * r_k))**0.5)
        n = 1 / cos_phi
        v = (r_k / (g * ((1 / cos_phi)**2 - 1)**0.5))**0.5
        return v, arg1, arg2, n, phi

    elif mode == 6:                         # r_k, n
        r_k = arg1
        n = arg2
        v = (r_k / (g * (n**2 - 1)**0.5))**0.5
        phi = math.acos(1 / n)
        ca = (2 * m) / (rho * s_ref * r_k * (1 / n) * (n ** 2 - 1) ** 0.5)
        return v, arg1, ca, arg2, phi

    elif mode == 7:                         # r_k, phi
        r_k = arg1
        phi = arg2
        n = 1 / math.cos(phi)
        v = (r_k / (g * (n**2 - 1)**0.5))**0.5
        ca = (2 * m) / (rho * s_ref * r_k * (1 / n) * (n ** 2 - 1) ** 0.5)
        return v, arg1, ca, n, arg2

    elif mode == 8:                         # ca, n
        ca = arg1
        n = arg2
        phi = math.acos(1 / n)
        r_k = (2 * m) / (rho * S * ca * (1 - (math.cos(phi))**2)**0.5)
        v = (r_k / (g * (n ** 2 - 1) ** 0.5)) ** 0.5
        return v, r_k, arg1, arg2, phi

    elif mode == 9:                         # ca, phi
        ca = arg1
        phi = arg2
        n = 1 / math.cos(phi)
        r_k = (2 * m) / (rho * S * ca * (1 - (math.cos(phi)) ** 2) ** 0.5)
        v = (r_k / (g * (n ** 2 - 1) ** 0.5)) ** 0.5
        return v, r_k, arg1, n, arg2

    elif mode == 10:                        # n, phi
        print("error: n and phi are too less arguments")

    else:
        print("error: Mode has to be between 1 and 10")


# ---Wendegeschwindigkeit und Wendedauer---


def wendegeschwindigkeit(v, r_k):
    chi_punkt = v / r_k
    return chi_punkt

"""
def wendegeschwindigkeit2(v, g, rho, m, s_ref, ca):
    chi_punkt = (g * (((ca * rho/2 * v**2 *s_ref) / (m * g))**2 - 1)**0.5) / (v)
    return chi_punkt
"""

def wendedauer(winkel, wendegeschw):
    t = winkel / wendegeschw
    return t


# ---Schubbedarf für stationäre Kurve___


def schubbedarf_kurve(cw, ca, m, g, phi):
    f = cw/ca * (m *g) / (math.cos(phi))
    return f


# ---beschleunigte/abgebremste Kurve---


def ueberschusskraft_kurve(f, schubbedarf):
    ueberschuss = f - schubbedarf
    return ueberschuss


def delta_chi(f_ueberschuss, r_k, m, t, v_0):
    delta = f_ueberschuss / (2 * r_k * m) * t**2 + v_0 / r_k * t
    v_0_neu = f_ueberschuss / m * t + v_0
    return delta, v_0_neu


def delta_t(r_k, m, f_ueberschuss, v_0, chi_inkrement):
    delta = (r_k * m / f_ueberschuss) * (
                (v_0 / r_k) ** 2 + 2 * chi_inkrement * f_ueberschuss / (r_k * m) ** 0.5 - v_0 / r_k)
    v_0_neu = f_ueberschuss / m * delta + v_0
    return delta, v_0_neu


def kurve_beschleunigt(v_start, winkel, winkelinkrement):
    kurvendauer = 0
    v_aktuell = v_start
    for kurvenwinkel in np.linspace(0,winkel,winkelinkrement):
        delta_time = delta_t(r_k,m, f_ueberschuss,v_aktuell,chi_inkrement)
        kurvendauer += delta_time[1]
        v_aktuell = delta_time[2]
    v_ende = v_aktuell
    return v_ende, kurvendauer
