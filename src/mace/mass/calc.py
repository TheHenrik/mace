import re
from functools import cache
from operator import attrgetter

from mace.domain.vector import Vector, Vectorcalc
from mace.domain.plane import Fluegel, Fluegelsegment, Flugzeug, Leitwerktyp, TLeitwerk


def scaleProfil(profil: list, nase: Vector, hinterkante: Vector) -> list:
    scale_factor = abs(hinterkante - nase)
    return [nase + scale_factor * coord for coord in profil]


def get_profil(airfoil: str) -> list:
    file_location = f"./././data/airfoils/{airfoil}.dat"
    with open(file_location, "rt") as f:
        raw_data = f.read()
        data = re.findall(r"([01].\d+) +([0\-].\d+)", raw_data)

    upper, lower = [], []
    mode, start = "u", float(data[0][0])
    for point in data:
        x, y = map(float, point)
        v = Vector(x, y, 0.0)
        if mode == "u":
            upper.append(v)
        elif mode == "l":
            lower.append(v)
        if abs(start - x) == 1:
            mode = "l"

    upper.sort(key=attrgetter("x"), reverse=False)
    lower.sort(key=attrgetter("x"), reverse=True)
    return upper + lower


def mesh(points, profil_innen, profil_außen):
    area = 0
    volume = 0
    for i in range(points // 2):
        io1, io2 = profil_innen[i], profil_innen[i + 1]
        iu1, iu2 = profil_innen[-i], profil_innen[-i - 1]
        ao1, ao2 = profil_außen[i], profil_außen[i + 1]
        au1, au2 = profil_außen[-i], profil_außen[-i - 1]

        volume += Vectorcalc.tri_volume(io1, io2, ao2)
        volume += Vectorcalc.tri_volume(io1, ao2, ao1)
        volume += Vectorcalc.tri_volume(iu1, au2, iu2)
        volume += Vectorcalc.tri_volume(iu1, au1, au2)
        volume += Vectorcalc.tri_volume(io1, iu1, iu2)
        volume += Vectorcalc.tri_volume(io1, iu2, io2)
        volume += Vectorcalc.tri_volume(ao1, au2, au1)
        volume += Vectorcalc.tri_volume(ao1, ao2, au2)

        area += Vectorcalc.tri_area(io1, io2, ao2)
        area += Vectorcalc.tri_area(io1, ao2, ao1)
        area += Vectorcalc.tri_area(iu1, iu2, au2)
        area += Vectorcalc.tri_area(iu1, au2, au1)
    return area, -volume
    for i in range(points - 1):
        volume += Vectorcalc.tri_volume(
            profil_innen[i], profil_innen[i + 1], profil_außen[i + 1]
        )
        volume += Vectorcalc.tri_volume(
            profil_innen[i], profil_außen[i + 1], profil_außen[i]
        )
        area += Vectorcalc.tri_area(
            profil_innen[i], profil_innen[i + 1], profil_außen[i + 1]
        )
        area += Vectorcalc.tri_area(
            profil_innen[i], profil_außen[i + 1], profil_außen[i]
        )

    for i in range(points // 2):
        volume += Vectorcalc.tri_volume(
            profil_innen[i], profil_innen[points - i - 1], profil_innen[points - i - 2]
        )
        volume += Vectorcalc.tri_volume(
            profil_innen[i], profil_innen[points - i - 2], profil_innen[i + 1]
        )
        volume += Vectorcalc.tri_volume(
            profil_außen[i], profil_außen[points - i - 2], profil_außen[points - i - 1]
        )
        volume += Vectorcalc.tri_volume(
            profil_außen[i], profil_außen[i + 1], profil_außen[points - i - 2]
        )
    return area, -volume


def get_mass_wing(wing: Fluegel):
    mass = 0
    profil = get_profil(wing.airfoil)
    points = len(profil)

    for segment in wing.fluegelsegment:
        profil_innen = scaleProfil(profil, segment.nose_inner, segment.back_inner)
        profil_außen = scaleProfil(profil, segment.nose_outer, segment.back_outer)

        area, volume = mesh(points, profil_innen, profil_außen)
        mass += area * 1
        mass += volume * 10_000

    return mass


def get_mass_empennage(empennage: Leitwerktyp):
    mass = 0
    if type(empennage.typ) is TLeitwerk:
        segments = empennage.typ.hoehenleitwerk
    profil = get_profil(empennage.typ.hoehenleitwerk)
    points = len(profil)

    for segment in segments:
        profil_innen = scaleProfil(profil, segment.nose_inner, segment.back_inner)
        profil_außen = scaleProfil(profil, segment.nose_outer, segment.back_outer)

        area, volume = mesh(points, profil_innen, profil_außen)
        mass += area * 1
        mass += volume * 10_000

    return mass


def get_mass_aircraft(aircraft: Flugzeug):
    mass = 0
    mass += get_mass_wing(aircraft.fluegel)
    mass += get_mass_empennage(aircraft.leitwerk)

    return mass
