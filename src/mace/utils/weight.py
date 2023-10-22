
def moment_at_position(mass: float, position: float, half_wing_span: float):
    moment = (half_wing_span - position) * mass * 10
    if position < 0.1 * half_wing_span:
        moment *= 1.5
    sicherheitsfaktor = 2
    return moment * sicherheitsfaktor