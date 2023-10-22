import numpy as np

from mace.domain.wing import Wing, WingBinder, WingSegment


def main():
    wing = Wing()

    ws = WingSegment()

    ws.inner_airfoil = "ag19"
    ws.nose_inner = np.array([0, 0.0, 0])
    ws.inner_chord = 0.322

    print(ws.get_rovings(5.0, 1.1))


if __name__ == "__main__":
    main()
