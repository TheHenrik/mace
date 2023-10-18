from mace.domain.wing import Wing, WingBinder, WingSegment
import numpy as np


def main():
    wing = Wing()

    ws = WingSegment()

    ws.inner_airfoil = "acc22"
    ws.nose_inner = np.array([0,0.5,0])
    ws.inner_chord = 0.322

    print(ws.get_rovings(3.0, 1.1))



if __name__ == "__main__":
    main()