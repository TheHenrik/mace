from mace.domain.plane import EmpennageType, Plane, TEmpennage, Wing, WingSegment
from mace.mass.mesh import gen_profile, get_profil, mesh


def estimate_mass_plane(plane: Plane):
    if plane.wing is not None:
        mass, wing = estimate_mass_wing(plane.wing)
        plane.mass += mass
        plane.wing = wing
    return plane


def estimate_mass_wing(wing: Wing):
    mass, segments = estimate_mass_segments(wing.segments, wing.airfoil)
    wing.mass = mass
    wing.segments = segments
    return mass, wing


def estimate_mass_empannage(empennage: EmpennageType):
    if empennage.typ is TEmpennage:
        pass


def estimate_mass_segments(segments: list[WingSegment], airoil_name: str):
    airfoil = get_profil(airoil_name)
    new_segments, mass = [], 0
    for segment in segments:
        profil_innen, profil_außen = gen_profile(
            airfoil,
            segment.nose_inner,
            segment.back_inner,
            segment.nose_outer,
            segment.back_outer,
        )
        area, volume = mesh(profil_innen, profil_außen)
        segment.mass += area * 1
        segment.mass += volume * 0
        segment.area = area
        segment.volume = volume
        mass = segment.mass
        new_segments.append(segment)
    return mass, new_segments
