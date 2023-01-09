from mace.domain.vector import Vectorcalc


class Mesh:
    def mesh(triangles: tuple):
        area = 0
        volume = 0
        for triangle in triangles:
            area += Vectorcalc.tri_area(*triangle)
            volume += Vectorcalc.tri_volume(*triangle)
        return area, -volume
