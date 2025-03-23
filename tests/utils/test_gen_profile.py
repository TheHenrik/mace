import numpy as np
from pymace.utils.mesh import gen_profile

def test_gen_profile_basic():
    # Define start and end points for the inner and outer segments.
    start_innen = np.array([0.0, 0.0, 0.0])
    end_innen = np.array([1.0, 0.0, 0.0])
    start_außen = np.array([0.0, 1.0, 0.0])
    end_außen = np.array([0.0, 2.0, 0.0])

    # Compute helper vectors:
    innen_strecke = end_innen - start_innen       # [1, 0, 0]
    außen_strecke = end_außen - start_außen       # [0, 1, 0]
    innen_außen = (start_außen - start_innen) / np.linalg.norm(start_außen - start_innen)  # [0, 1, 0]
    höhen_strecke = np.cross(innen_außen, innen_strecke)  # [0, 0, -1]

    # Define simple 2-point profiles (each row: [factor_along_seg, factor_along_height]).
    profil_innen = np.array([
        [0.0, 0.0],
        [1.0, 1.0]
    ])
    profil_außen = np.array([
        [0.0, 0.0],
        [2.0, 2.0]
    ])

    # Expected transformation:
    # For profil_innen:
    # Point0: start_innen + 0 * innen_strecke + 0 * höhen_strecke = [0, 0, 0]
    # Point1: start_innen + 1 * innen_strecke + 1 * höhen_strecke = [1, 0, -1]
    exp_innen = np.array([
        [0.0, 0.0, 0.0],
        [1.0, 0.0, -1.0]
    ])
    # For profil_außen:
    # Point0: start_außen + 0 * außen_strecke + 0 * höhen_strecke = [0, 1, 0]
    # Point1: start_außen + 2 * außen_strecke + 2 * höhen_strecke = [0, 1+2, 0-2] = [0, 3, -2]
    exp_außen = np.array([
        [0.0, 1.0, 0.0],
        [0.0, 3.0, -2.0]
    ])

    res_innen, res_außen = gen_profile(profil_innen, profil_außen, start_innen, end_innen, start_außen, end_außen)

    np.testing.assert_allclose(res_innen, exp_innen, rtol=1e-5,
                               err_msg="gen_profile did not compute the inner profile correctly.")
    np.testing.assert_allclose(res_außen, exp_außen, rtol=1e-5,
                               err_msg="gen_profile did not compute the outer profile correctly.")

def test_gen_profile_nontrivial():
    # Use a different set of points
    start_innen = np.array([1.0, 2.0, 3.0])
    end_innen = np.array([2.0, 2.0, 3.0])
    start_außen = np.array([1.0, 3.0, 3.0])
    end_außen = np.array([1.0, 4.0, 3.0])

    # Helper vectors:
    innen_strecke = end_innen - start_innen       # [1, 0, 0]
    außen_strecke = end_außen - start_außen       # [0, 1, 0]
    innen_außen = (start_außen - start_innen) / np.linalg.norm(start_außen - start_innen)  # [0, 1, 0]
    höhen_strecke = np.cross(innen_außen, innen_strecke)  # [0, 0, -1]

    # Define profiles with two points each.
    profil_innen = np.array([
        [0.5, 0.5],
        [1.0, 0.0]
    ])
    profil_außen = np.array([
        [0.0, 0.0],
        [0.5, 1.0]
    ])

    # Expected results computed in the same way as gen_profile applies:
    # For inner: for each point:
    # point = start_innen + (factor0 * innen_strecke) + (factor1 * höhen_strecke)
    exp_innen = np.array([
        start_innen + 0.5 * innen_strecke + 0.5 * höhen_strecke,
        start_innen + 1.0 * innen_strecke + 0.0 * höhen_strecke,
    ])
    # For outer:
    exp_außen = np.array([
        start_außen + 0.0 * außen_strecke + 0.0 * höhen_strecke,
        start_außen + 0.5 * außen_strecke + 1.0 * höhen_strecke,
    ])

    res_innen, res_außen = gen_profile(profil_innen, profil_außen, start_innen, end_innen, start_außen, end_außen)

    np.testing.assert_allclose(res_innen, exp_innen, rtol=1e-5,
                               err_msg="gen_profile did not compute the inner profile correctly in nontrivial case.")
    np.testing.assert_allclose(res_außen, exp_außen, rtol=1e-5,
                               err_msg="gen_profile did not compute the outer profile correctly in nontrivial case.")