import numpy as np
import pytest
from pymace.utils.mesh import tri_area

def test_tri_area_unit_right_triangle():
    # Single right triangle in 3D (but wrapped in an extra dimension for broadcasting)
    first = np.array([[0, 0, 0]])
    second = np.array([[1, 0, 0]])
    third = np.array([[0, 1, 0]])
    expected_area = 0.5
    result = tri_area(first, second, third)
    assert result == pytest.approx(expected_area), "Area of a unit right triangle should be 0.5"

def test_tri_area_collinear_points():
    # Points along the same line should yield zero area.
    first = np.array([[0, 0, 0]])
    second = np.array([[1, 1, 1]])
    third = np.array([[2, 2, 2]])
    result = tri_area(first, second, third)
    assert result == pytest.approx(0.0), "Collinear points should have zero area"

def test_tri_area_multiple_triangles():
    # Test with two triangles computed in one call
    # First triangle: vertices (0,0,0), (1,0,0), (0,1,0) => area 0.5
    # Second triangle: vertices (0,0,0), (2,0,0), (0,2,0) => area 2.0
    first = np.array([[0, 0, 0], [0, 0, 0]])
    second = np.array([[1, 0, 0], [2, 0, 0]])
    third = np.array([[0, 1, 0], [0, 2, 0]])
    expected_total_area = 0.5 + 2.0
    result = tri_area(first, second, third)
    assert result == pytest.approx(expected_total_area), "Total area should be the sum of individual triangle areas"