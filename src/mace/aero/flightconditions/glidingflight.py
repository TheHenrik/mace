import math
from mace.aero import generalfunctions as gf


def v_gleitflug():
    v = ((2 * m * g) / (rho * s_ref))**0.5 * (cw**2 + ca**2)**(-0.25)
    return v


def gamma(cw, ca):
    gam = math.atan(-cw / ca)
    return gam


def v_vertikal(v, rho, s_ref, cw, m, g):
    v_v = v**3 * ((-rho/2) * s_ref * cw) / (m * g)
    return v_v


# ---Iteration über V---


def v_gleit_iteration():
    re = gf.re(v_shot, l, ny)
    gf.gen_polar(re)
    gf.get_coeffs()
    v = v_gleitflug()
    while abs(v - v_shot) > tolerance:
        re = gf.re(v_shot, l, ny)
        gf.gen_polar(re)
        gf.get_coeffs()
        v = v_gleitflug()
    return v


# ---Auswertung---


def best_glide():
    pass


def smalest_decline():
    pass


def hoehenverlust(v_v, t):
    h = v_v * t
    return h


def abgleitdauer(hoehe, v_v):
    t = hoehe / v_v
    return t


def flugstrecke(v_gleit, gamma, t):
    s = v_gleit * math.cos(gamma) * t
    return s
