import numpy as np
from mace.aero import generalfunctions


def v_climb(m, g, f, rho, s_ref, cw, ca) -> (float, float):
    a = ((m * g)**2 - f**2) / ((rho/2) * s_ref)
    b = (f * cw)**2 / ((rho/2) * s_ref * (cw**2 + ca**2))
    c = (rho/2) * s_ref * (cw**2 + ca**2)
    d = (f * cw) / ((rho/2) * s_ref * (cw**2 + ca**2))

    v = (((a + b) / c)**0.5 + d)**0.5
    v2 = ((a + b) / c)**0.5 + d
    return v, v2                        # gibt als Tupel V und V^2 zurück


def sin_gamma(f, rho, v2, s_ref, cw, m, g):         # v2 = V^2
    sin = (f - (rho/2) * v2 * s_ref * cw) / (m * g)
    return sin


def cos_gamma(rho, v2, s_ref, ca, m, g):         # V2 = V^2
    cos = ((rho/2) * v2 * s_ref * ca) / (m * g)
    return cos


def gamma(sin, cos):                # zu Vergleichszwecken doppelte Berechnung
    gamma1 = np.arcsin(sin)
    gamma2 = np.arccos(cos)
    return gamma1, gamma2           # wird als Tupel übergeben


def v_v(v, sin_gam):                # sin_gamma bereits vorher berechnen, ist übersichtlicher
    v_vert = v * sin_gam
    return v_vert


# ---Iteration über V---

def iteration(dif_re, tolerance_re, m, g, f, rho, s_ref, cw, ca, v_init: float, flaechentiefe, ny, it_max=20):

    v_shot = v_init
    i = 0
    while i < it_max or dif_re > tolerance_re:

        re = generalfunctions.re(v_shot, flaechentiefe, ny)

        generalfunctions.gen_polar(re)
        generalfunctions.get_coeffs()

        v_res, _ = v_climb(m, g, f, rho, s_ref, cw, ca)     # Unterstrich Platzhalter Platzhalter für Nichtbenutzung

        dif_re = (v_res - v_shot)
        v_shot = v_res

        i += 1


# ---Auswertung---

def steepest_climb():
    # gamma maximal
    pass


def fastest_climb():
    # V_v maximal
    pass


def gained_heigth(v_v, t):
    h = v_v * t
    return h


def gained_distance(v, cos_gam, t):
    s = v * cos_gam * t
    return s


# --------------------------------
# ---Test---
# --------------------------------


if __name__ == "__main__":
    x = gamma(0.4, 0.2)
    print(x)
