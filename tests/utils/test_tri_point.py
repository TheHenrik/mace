import numpy as np
from pymace.utils.mesh import tri_point
import pytest

def test_tri_point_single_triangle():
    # Triangle vertices: (0,0,0), (1,0,0), (0,1,0)
    # The area weighted centroid is (norm(cross) * (A+B+C)) / 6.
    # For these points, np.cross([1,0,0], [0,1,0]) = [0,0,1] with norm 1, and A+B+C = [1,1,0].
    # Expected weighted centroid = [1,1,0] / 6.
    A = np.array([[0, 0, 0]])
    B = np.array([[1, 0, 0]])
    C = np.array([[0, 1, 0]])
    expected = np.array([1/6, 1/6, 0])
    result = tri_point(A, B, C)
    np.testing.assert_allclose(result, expected, rtol=1e-6)


@pytest.mark.skip(reason="Multiple Dimensions not implemented")
def test_tri_point_multiple_triangles():
    # Test with two triangles computed in one call.
    # Triangle 1: (0,0,0), (1,0,0), (0,1,0)
    #   cross norm = 1, A+B+C = [1,1,0] -> weighted centroid = [1,1,0] / 6.
    # Triangle 2: (0,0,0), (2,0,0), (0,2,0)
    #   cross norm = 4, A+B+C = [2,2,0] -> weighted centroid = (4*[2,2,0]) / 6 = [8/6, 8/6, 0] = [4/3, 4/3, 0].
    A = np.array([[0, 0, 0], [0, 0, 0]])
    B = np.array([[1, 0, 0], [2, 0, 0]])
    C = np.array([[0, 1, 0], [0, 2, 0]])
    expected_first = np.array([1/6, 1/6, 0])
    expected_second = np.array([4/3, 4/3, 0])
    result = tri_point(A, B, C)
    np.testing.assert_allclose(result[:][0], expected_first, rtol=1e-6)
    np.testing.assert_allclose(result[1], expected_second, rtol=1e-6)