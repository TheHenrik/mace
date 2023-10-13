import numpy as np

from mace.domain import params
from mace.utils.mesh import mesh


class FuselageSegment:
    profile: np.ndarray
    circumference: float
    shape: str
    width: float
    height: float
    origin: np.ndarray

    def __init__(self, origin, shape, width, height):    
        self.width = width
        self.height = height
        self.origin = origin
        if shape == "rectangular":
            dx = 0
            dy = self.width/2
            dz = self.height/2
            p1 = origin + np.array([dx, +dy, +dz])
            p2 = origin + np.array([dx, -dy, +dz])
            p3 = origin + np.array([dx, -dy, -dz])
            p4 = origin + np.array([dx, +dy, -dz])
            self.profile = np.array([p1,p2,p3,p4])
            self.circumference = 2 * (self.height + self.width)
            self.shape = shape
        elif shape == "elliptical":
            angle = np.linspace(0, 2*np.pi, 100)
            p = [np.array([0, np.sin(a)*self.height, np.cos(a)*self.width]) for a in angle]
            self.profile = np.array(p)
            lbda = self.height - self.width / (self.width + self.height)
            self.circumference = (
                np.pi
                * (self.width + self.height)
                * (1 + 3 * lbda**2 / (10 + (4 - 3 * lbda**2) ** 0.5))
            )
            self.shape = shape


class Fuselage:
    def __init__(self):
        self.origin: np.ndarray = np.array([0.0, 0.0, 0.0])
        self.length: float = 0.0
        self.diameter: float = 0.0
        self.segments = []
        self.drag_correction: float = 2.6

    def add_segment(self, origin, shape, width, height) -> None:
        self.segments.append(FuselageSegment(origin, shape, width, height))

    def get_wetted_area(self):
        # A_wetted = 0.0
        # for i, segment in enumerate(self.segments):
        #     if i == 0:
        #         last_segment_circumference = segment.get_circumference()
        #         last_segment_x = segment.origin[0]
        #     else:
        #         last_segment_circumference = this_segment_circumference
        #         last_segment_x = this_segment_x
        #     this_segment_circumference = segment.get_circumference()
        #     this_segment_x = segment.origin[0]
        #     length = abs(this_segment_x - last_segment_x)
        #     A_wetted += (
        #         length * (last_segment_circumference + this_segment_circumference) / 2
        #     )

        A_wetted = 0.0
        for i in range(len(self.segments) - 1):
            a, b = mesh(self.segments[i].profile, self.segments[i + 1].profile)
            A_wetted += a
        return A_wetted

    def build(self):
        most_forward_point = 0.0
        most_backward_point = 0.0
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
        C_D_wet = (1 + 1.5 * d_l**1.5 + 7 * d_l**3) * C_D_turb
        C_D_fuse = self.drag_correction * C_D_wet * S_wet / S_ref

        return C_D_fuse

    def get_mass(self):
        lenght = len(self.segments)
        area, volume = 0, 0
        cog = np.array([0.,0.,0.])
        for i in range(lenght - 1):
            a, b, c = mesh(self.segments[i].profile, self.segments[i+1].profile)
            cog += c * area
            area += a
            volume += b
        self.mass = area * 320 * 2.2 / 1000
        self.volume = volume
        self.area = area
        self.cog = cog*area

        return self.mass, cog * self.mass


if __name__ == "__main__":
    Re_L = 3e6
    c_w_1 = 0.427 / (np.log10(Re_L) - 0.407) ** 2.64
    c_w_2 = 0.455 / (np.log10(Re_L)) ** 2.58
    c_w_3 = 0.074 / Re_L**0.2

    print(c_w_1)
    print(c_w_2)
    print(c_w_3)
