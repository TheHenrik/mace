from mace.domain.plane import Fluegel, Fluegelsegment, Flugzeug, Leitwerktyp, TLeitwerk
from mace.mass.mesh import gen_profile, get_profil, mesh


def get_mass_plane(plane: Flugzeug):
    if plane.fluegel is not None:
        mass, wing = get_mass_wing(plane.fluegel)
        plane.mass += mass
        plane.fluegel = wing
    return plane


def get_mass_wing(wing: Fluegel):
    mass, segments = get_mass_segments(wing.fluegelsegment, wing.airfoil)
    wing.mass = mass
    wing.fluegelsegment = segments
    return mass, wing


def get_mass_empannage(empennage: Leitwerktyp):
    if empennage.typ is TLeitwerk:
        pass


def get_mass_segments(segments: list[Fluegelsegment], airoil: str):
    profil = get_profil(airoil)
    new_segments, mass = [], 0
    for segment in segments:
        profil_innen, profil_außen = gen_profile(
            profil,
            segment.nose_inner,
            segment.back_inner,
            segment.nose_outer,
            segment.back_outer,
        )
        area, volume = mesh(profil_innen, profil_außen)
        segment.mass = area * 0
        segment.mass = volume * 1
        mass += segment.mass
        new_segments.append(segment)
    return mass, new_segments
