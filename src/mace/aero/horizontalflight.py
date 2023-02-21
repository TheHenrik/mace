

def fluggeschwindigkeit(m, g, ca, rho, s_ref):
    v = ((2 * m * g)/(ca * rho * s_ref))**0.5
    return v


def min_fluggeschwindigkeit(ca_max, m, g, rho, s_ref):
    v_min = fluggeschwindigkeit(m, g, ca_max, rho, s_ref)
    return v_min


def schubbedarf(cw, ca, m, g):
    schub = cw / ca * m * g
    return schub


def fv_diagramm(ca_init, m, g, rho, s_ref, step, ca_max):

    ca = ca_init

    while ca <= ca_max:
        v = fluggeschwindigkeit(m, g, ca, rho, s_ref)
        # mit ca cw aus Polare ermitteln
        if no_polar_available:
            break
        schub = schubbedarf(cw, ca, m, g)

        res = v, schub

        ca += step
    return res


# ---Auswertung---


def min_schubkraft():
    pass


def max_fluggeschwindigkeit():
    pass


def flugstrecke(v, t):
    s = v * t
    return s


# ---Beschleunigung---


def ueberschusskraft():
    f_ueberschuss = f - schubbedarf(cw, ca, m, g)
    return f_ueberschuss


def delta_t(m, v2, v1):
    del_t = m / ueberschusskraft() * (v2 - v1)
    return del_t


def beschleunigung(v_begin, v_end, step, m):
    t = 0

    if v_begin < v_end:
        ueberschuss = ueberschusskraft()
        if ueberschuss < 0:
            print("error")
        else:
            v = v_begin
            while v <= v_end:
                t += delta_t(m, v+step, v)
                v += step
            return t
    elif v_end < v_begin:
        ueberschuss = ueberschusskraft()
        if ueberschuss > 0:
            print("error")
        else:
            v = v_begin
            while v <= v_end:
                t += delta_t(m, v + step, v)
                v += step
            return t
    else:
        return t
