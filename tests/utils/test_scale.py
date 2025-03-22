import numpy as np
from pymace.utils.mesh import scale

def test_scale_with_1d_vector():
    # Given a 1D vector and two scaling factors, we expect to obtain two scaled versions.
    factors = np.array([2, 3])
    vecs = np.array([10, 20])
    # Expected output: first row = [10*2, 20*2], second row = [10*3, 20*3]
    expected = np.array([[20, 40],
                         [30, 60]])
    result = scale(factors, vecs)
    np.testing.assert_array_equal(result, expected)

def test_scale_with_2d_array():
    # Given a 2D array of vectors (each row is a vector) and two scaling factors,
    # we expect to obtain the full set of scaled vectors for each factor.
    factors = np.array([2, 3])
    vecs = np.array([[1, 2],
                     [3, 4],
                     [5, 6]])
    # Expected output: shape (2, 3, 2) where:
    # result[0] is vecs scaled by 2 and result[1] is vecs scaled by 3.
    expected = np.array([vecs * 2, vecs * 3])
    result = scale(factors, vecs)
    np.testing.assert_array_equal(result, expected)