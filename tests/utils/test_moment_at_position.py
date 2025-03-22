import pytest
from pymace.domain.params import Constants
from pymace.utils.weight import moment_at_position

def test_moment_at_position_no_multiplier():
    # position greater than or equal to 10% of the half wing span, no 1.5 multiplier.
    mass = 100
    half_wing_span = 10
    position = 2  # abs(2) is 2, which is >= 1.0 (10% of 10)
    expected = ((half_wing_span - abs(position)) * mass * Constants.g) * 2
    result = moment_at_position(mass, position, half_wing_span)
    assert result == pytest.approx(expected)

def test_moment_at_position_with_multiplier():
    # position less than 10% of the half wing span, so 1.5 multiplier is applied.
    mass = 100
    half_wing_span = 10
    position = 0.5  # abs(0.5) is 0.5, which is less than 1.0 (10% of 10)
    moment = (half_wing_span - abs(position)) * mass * Constants.g
    moment *= 1.5  # bonus multiplier
    expected = moment * 2
    result = moment_at_position(mass, position, half_wing_span)
    assert result == pytest.approx(expected)

def test_moment_at_position_negative():
    # Negative position should be treated as its absolute value.
    mass = 100
    half_wing_span = 10
    position = -0.5  # abs(-0.5) is 0.5, so multiplier applies as before.
    moment = (half_wing_span - abs(position)) * mass * Constants.g
    moment *= 1.5
    expected = moment * 2
    result = moment_at_position(mass, position, half_wing_span)
    assert result == pytest.approx(expected)