import numpy as np
from mace.domain import params

class FuselageSegment:
    def __init__(self):
        self.width: float = 0.
        self.height: float = 0.
        self.origin: np.ndarray = np.array([0., 0., 0.])
        self.shape: str = 'rectangular' # 'elliptical'
        self.circumference: float = 0.

    def get_circumference(self):
        if self.shape == 'rectangular':
            circumference = 2 * self.width + 2 * self.height
        if self.shape == 'elliptical':
            lbda = self.width - self.height / (self.width + self.height)
            circumference = math.pi * (self.width + self.height) * (1 + 3 * lbda**2 / (10 + (4 - 3*lbda**2)**0.5))
        self.circumference = circumference
        return circumference
class Fuselage:
    def __init__(self):
        self.origin: np.ndarray = np.array([0., 0., 0.])
        self.length: float = 0.
        self.diameter: float = 0.
        self.segments = []

    def add_segment(self, segment: FuselageSegment) -> None:
        self.segments.append(segment)

    def get_wetted_area(self):
        A_wetted = 0.
        for i, segment in enumerate(self.segments):
            if i == 0:
                last_segment_circumference = segment.get_circumference()
                last_segment_x = segment.origin[0]
            else:
                last_segment_circumference = this_segment_circumference
                last_segment_x = this_segment_x
            this_segment_circumference = segment.get_circumference()
            this_segment_x = segment.origin[0]
            length = abs(this_segment_x - last_segment_x)
            A_wetted += length * (last_segment_circumference + this_segment_circumference) / 2
        return A_wetted

    def build(self):
        most_forward_point = 0.
        most_backward_point = 0.
        for segment in self.segments:
            if segment.origin[0] > most_backward_point:
                most_backward_point = segment.origin[0]
            if segment.origin[0] < most_forward_point:
                most_forward_point = segment.origin[0]
            diameter = (segment.width + segment.height) / 2
            if diameter > self.diameter:
                self.diameter = diameter
        self.length = most_backward_point - most_forward_point

    def get_drag_coefficient(self, V, S_ref):
        Re_L = V * self.length / params.Constants.ny
        if Re_L == 0:
            Re_L = 1e3
        d_l = self.diameter / self.length
        S_wet = self.get_wetted_area()

        
        C_D_turb = 0.074 / Re_L**0.2
        C_D_wet = (1 + 1.5 * d_l ** 1.5 + 7 * d_l ** 3) * C_D_turb
        C_D_fuse = C_D_wet * S_wet / S_ref
        
        return C_D_fuse
    
        

if __name__ == '__main__':
    Re_L = 3e6
    c_w_1 = 0.427 / (np.log10(Re_L)-0.407)**2.64
    c_w_2 = 0.455 / (np.log10(Re_L))**2.58
    c_w_3 = 0.074 / Re_L**0.2

    print(c_w_1)
    print(c_w_2)
    print(c_w_3)