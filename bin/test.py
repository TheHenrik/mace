import numpy as np

profil = np.array([[0,0,0]])


def gen_profile(profil, start_innen, end_innen, start_außen, end_außen):
    innen_strecke = end_innen - start_innen
    außen_strecke = end_außen - start_außen
    innen_außen = (start_außen - start_innen)/np.linalg.norm(start_außen - start_innen)
    höhen_strecke = np.cross(innen_außen, innen_strecke)

    def scale(factors, vecs):
        return (factors * np.repeat(vecs[np.newaxis], len(factors), axis=0).T).T

    profil_innen = (
        start_innen
        + scale(profil[:, 0], innen_strecke)
        + scale(profil[:, 1], höhen_strecke)
    )
    profil_außen = (
        start_außen
        + scale(profil[:, 0], außen_strecke)
        + scale(profil[:, 1], höhen_strecke)
    )
    return profil_innen, profil_außen

print(gen_profile())