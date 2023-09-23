import re
from functools import cache

import numpy as np
from pathlib import Path

def tri_area(first: np.ndarray, second: np.ndarray, third: np.ndarray):
    return np.sum(np.linalg.norm(np.cross(second - first, third - first), axis=1)) / 2


def tri_volume(first: np.ndarray, second: np.ndarray, third: np.ndarray):
    return np.sum(np.cross(first, second) * third) / 6


def scale(factors, vecs):
    return (factors * np.repeat(vecs[np.newaxis], len(factors), axis=0).T).T


def gen_profile(profil_innen, profil_außen, start_innen, end_innen, start_außen, end_außen):
    innen_strecke = end_innen - start_innen
    außen_strecke = end_außen - start_außen
    innen_außen = (start_außen - start_innen) / np.linalg.norm(
        start_außen - start_innen
    )
    höhen_strecke = np.cross(innen_außen, innen_strecke)

    profil_innen = (
        start_innen
        + scale(profil_innen[:, 0], innen_strecke)
        + scale(profil_innen[:, 1], höhen_strecke)
    )
    profil_außen = (
        start_außen
        + scale(profil_außen[:, 0], außen_strecke)
        + scale(profil_außen[:, 1], höhen_strecke)
    )
    return profil_innen, profil_außen


@cache
def get_profil(airfoil: str) -> list:
    file_location = Path(f"{Path(__file__).parents[3]}/data/airfoils/{airfoil}.dat")
    with open(file_location, "rt") as f:
        raw_data = f.read()
        data = re.findall(r"([01].\d+) +([0\-].\d+)", raw_data)

    profil = []
    for point in data:
        profil.append(list(map(float, point)))

    return np.asarray(profil)


def mesh(profil_innen, profil_außen):
    area = 0
    volume = 0
    assert len(profil_innen) == len(profil_außen)
    indices = np.arange(len(profil_innen) // 2)
    io1s, io2s = profil_innen[indices], profil_innen[indices + 1]
    iu1s, iu2s = profil_innen[-indices], profil_innen[-indices - 1]
    ao1s, ao2s = profil_außen[indices], profil_außen[indices + 1]
    au1s, au2s = profil_außen[-indices], profil_außen[-indices - 1]

    volume += tri_volume(io1s, io2s, ao2s)
    volume += tri_volume(io1s, ao2s, ao1s)
    volume += tri_volume(iu1s, au2s, iu2s)
    volume += tri_volume(iu1s, au1s, au2s)
    volume += tri_volume(io1s, iu1s, iu2s)
    volume += tri_volume(io1s, iu2s, io2s)
    volume += tri_volume(ao1s, au2s, au1s)
    volume += tri_volume(ao1s, ao2s, au2s)

    area += tri_area(io1s, io2s, ao2s)
    area += tri_area(io1s, ao2s, ao1s)
    area += tri_area(iu1s, iu2s, au2s)
    area += tri_area(iu1s, au2s, au1s)

    return area, volume
