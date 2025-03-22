import re
from functools import cache
from pathlib import Path

import numpy as np

from pymace.utils.file_path import root


def tri_area(first: np.ndarray, second: np.ndarray, third: np.ndarray) -> float:
    """ Calculates the signed area created by three vectors

    Args:
        first (np.ndarray): Vector
        second (np.ndarray): Vector
        third (np.ndarray): Vector

    Returns:
        float: Area
    """
    return np.sum(np.linalg.norm(np.cross(second - first, third - first), axis=1)) / 2


def tri_volume(first: np.ndarray, second: np.ndarray, third: np.ndarray) -> float:
    """ Calculates the signed volume of the span of three vectors.

    Args:
        first (np.ndarray): Vector
        second (np.ndarray): Vector
        third (np.ndarray): Vector

    Returns:
        float: Volume
    """
    return np.sum(np.cross(first, second) * third) / 6


def tri_point(first: np.ndarray, second: np.ndarray, third: np.ndarray) -> np.ndarray:
    """
    Calculate the centroid of a triangle in 3D space.

    Parameters:
    first (np.ndarray): A 1D array representing the coordinates of the first vertex of the triangle.
    second (np.ndarray): A 1D array representing the coordinates of the second vertex of the triangle.
    third (np.ndarray): A 1D array representing the coordinates of the third vertex of the triangle.

    Returns:
    np.ndarray: A 1D array representing the coordinates of the centroid of the triangle.
    """
    return (
        np.linalg.norm(np.cross(second - first, third - first), axis=1)
        @ (first + second + third)
    ) / 6


def scale(factors, vecs):
    """
    Scales the given vectors by the specified factors.

    Parameters:
    factors (array-like): A 1D array of scaling factors.
    vecs (array-like): A 1D or 2D array of vectors to be scaled.

    Returns:
    numpy.ndarray: A 2D array where each vector from `vecs` is scaled by the corresponding factor from `factors`.
    """
    return (factors * np.repeat(vecs[np.newaxis], len(factors), axis=0).T).T


def gen_profile(
    profil_innen, profil_außen, start_innen, end_innen, start_außen, end_außen
):
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


def get_profil(airfoil: str) -> np.ndarray:
    """Returns the profile with the given name.uv

    Args:
        airfoil (str): Namme of the file of the profile.

    Returns:
        np.ndarray: Array of the profile coordinates.
    """
    file_location = Path(f"{root()}/data/airfoils/{airfoil}.dat")
    with open(file_location, "rt") as f:
        data = re.findall(r"([01]\.\d+) +([0\-]{1,2}\.\d+)", f.read())
    profil = [list(map(float, point)) for point in data]
    return np.asarray(profil)


@cache
def get_profil_thickness(airfoil: str) -> float:
    """
    Calculate the maximum thickness of an airfoil profile.

    This function retrieves the airfoil profile data and computes the maximum
    thickness by finding the maximum difference between the upper and lower
    surfaces of the airfoil.

    Args:
        airfoil (str): The name or identifier of the airfoil.

    Returns:
        float: The maximum thickness of the airfoil profile.
    """
    profil = get_profil(airfoil)
    return max(profil[i][1] - profil[-i][1] for i in range(len(profil) // 2))


def mesh(profil_innen, profil_außen):
    """
    Calculate the area, volume, and centroid of a mesh defined by inner and outer airfoils.

    Args:
        profil_innen (list or np.ndarray): The inner profile points of the mesh.
        profil_außen (list or np.ndarray): The outer profile points of the mesh.

    Returns:
        tuple: A tuple containing:
            - area (float): The total area of the mesh.
            - volume (float): The total volume of the mesh.
            - p (np.ndarray): The centroid of the mesh as a 3D point.
    """
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

    p = np.array([0.0, 0.0, 0.0])
    p += tri_point(io1s, io2s, ao2s)
    p += tri_point(io1s, ao2s, ao1s)
    p += tri_point(iu1s, iu2s, au2s)
    p += tri_point(iu1s, au2s, au1s)
    p /= area

    return area, volume, p


if __name__ == "__main__":
    print(get_profil_thickness("ag19"))
