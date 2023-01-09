from mace.domain.vector import Vectorcalc


class Mesh: 
    def mesh(points, profil_innen, profil_außen):
        area = 0
        volume = 0
        for i in range(points // 2):
            io1, io2 = profil_innen[i], profil_innen[i + 1]
            iu1, iu2 = profil_innen[-i], profil_innen[-i - 1]
            ao1, ao2 = profil_außen[i], profil_außen[i + 1]
            au1, au2 = profil_außen[-i], profil_außen[-i - 1]

            volume += Vectorcalc.tri_volume(io1, io2, ao2)
            volume += Vectorcalc.tri_volume(io1, ao2, ao1)
            volume += Vectorcalc.tri_volume(iu1, au2, iu2)
            volume += Vectorcalc.tri_volume(iu1, au1, au2)
            volume += Vectorcalc.tri_volume(io1, iu1, iu2)
            volume += Vectorcalc.tri_volume(io1, iu2, io2)
            volume += Vectorcalc.tri_volume(ao1, au2, au1)
            volume += Vectorcalc.tri_volume(ao1, ao2, au2)

            area += Vectorcalc.tri_area(io1, io2, ao2)
            area += Vectorcalc.tri_area(io1, ao2, ao1)
            area += Vectorcalc.tri_area(iu1, iu2, au2)
            area += Vectorcalc.tri_area(iu1, au2, au1)
        return area, -volume