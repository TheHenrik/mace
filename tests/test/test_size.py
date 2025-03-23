import sys
import pytest
from pymace.test.size import getsize
import math

def test_getsize_int():
    x = 10
    size = getsize(x)
    # The size should be at least sys.getsizeof(x)
    assert isinstance(size, int)
    assert size >= sys.getsizeof(x)


def test_getsize_list():
    lst = [1, 2, 3, [4, 5, [6, 7]]]
    size = getsize(lst)
    # The computed size should be greater than or equal to the shallow size.
    assert isinstance(size, int)
    assert size >= sys.getsizeof(lst)


def test_getsize_dict():
    d = {"a": 1, "b": [2, 3], "c": {"nested": "value"}}
    size = getsize(d)
    assert isinstance(size, int)
    assert size >= sys.getsizeof(d)


def test_getsize_complex_object():
    # Test with a nested structure
    complex_obj = {
        "list": [i for i in range(10)],
        "dict": {str(i): [i, i*2] for i in range(5)},
        "string": "pytest testing"
    }
    size = getsize(complex_obj)
    assert isinstance(size, int)
    assert size >= sys.getsizeof(complex_obj)


def test_getsize_invalid_types():
    # Ensure getsize fails for function and module types.
    with pytest.raises(TypeError):
        getsize(lambda x: x)
    with pytest.raises(TypeError):
        getsize(math)