from pymace.domain.params import Constants


def moment_at_position(mass: float, position: float, half_wing_span: float):
    """
    Calculates the moment at a specified position along a wing span, factoring in gravitational force and safety considerations.

    Parameters:
        mass (float): The mass at the given position.
        position (float): The position along the wing; its absolute value is used.
        half_wing_span (float): Half of the total wing span.

    Returns:
        float: The computed moment, which is the product of the adjusted arm length, mass, gravitational constant (Constants.g), and a safety factor. The moment is increased by 50% if the position is within 10% of the half wing span, and then multiplied by an additional safety factor of 2.

    Notes:
        - The gravitational constant, Constants.g, is expected to be defined elsewhere in the code.
        - The absolute value of the position is used to ensure correct moment calculation regardless of direction.
    """
    position = abs(position)
    moment = (half_wing_span - position) * mass * Constants.g
    if position < 0.1 * half_wing_span:
        moment *= 1.5
    sicherheitsfaktor = 2
    return moment * sicherheitsfaktor
