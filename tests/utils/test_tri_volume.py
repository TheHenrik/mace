import numpy as np
import pytest
from pymace.utils.mesh import tri_volume

def test_tri_volume_unit_cube_corner():
    # Three mutually perpendicular vectors:
    # first = [1,0,0], second = [0,1,0], third = [0,0,1]
    # Expected tetrahedron volume: dot(cross(first, second), third) /6 = 1/6.
    first = np.array([[1, 0, 0]])
    second = np.array([[0, 1, 0]])
    third = np.array([[0, 0, 1]])
    expected_volume = 1/6
    result = tri_volume(first, second, third)
    assert result == pytest.approx(expected_volume), "Volume for perpendicular unit vectors should be 1/6"

def test_tri_volume_collinear_vectors():
    # Collinear vectors should yield zero volume.
    first = np.array([[1, 0, 0]])
    second = np.array([[2, 0, 0]])
    third = np.array([[3, 0, 0]])
    expected_volume = 0.0
    result = tri_volume(first, second, third)
    assert result == pytest.approx(expected_volume), "Collinear vectors should produce zero volume"

def test_tri_volume_multiple_vectors():
    # Test with two sets of vectors in one call:
    # First set: [1,0,0], [0,1,0], [0,0,1] -> volume = 1/6.
    # Second set: [2,0,0], [0,2,0], [0,0,2] -> volume = (dot(cross([2,0,0],[0,2,0]), [0,0,2]))/6
    #       cross([2,0,0],[0,2,0]) = [0,0,4] and dot([0,0,4],[0,0,2]) = 8 so volume = 8/6.
    # Total expected volume = 1/6 + 8/6 = 9/6 = 1.5
    first = np.array([[1, 0, 0], [2, 0, 0]])
    second = np.array([[0, 1, 0], [0, 2, 0]])
    third = np.array([[0, 0, 1], [0, 0, 2]])
    expected_volume = 1.5
    result = tri_volume(first, second, third)
    assert result == pytest.approx(expected_volume), "Total volume should be the sum of individual volumes"