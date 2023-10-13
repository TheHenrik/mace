
def moment_at_position(mass: float, position: float, half_wing_span: float):
    moment = (half_wing_span - position) * mass * 10
    if position < 0.1 * half_wing_span:
        moment *= 1.2
    # TODO Sicherheitsfaktor 10?
    sicherheitsfaktor = 4
    return moment * sicherheitsfaktor