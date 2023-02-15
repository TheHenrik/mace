from dataclasses import dataclass
from mace.domain.plane import Plane


# ---Klassen für Eingabe für Berechnungsfunktionen---

class Inputdata:
    def __init__(self):
        v0 = None              # Geschwindigkeiten
        self.v_min = None

        self.num = None             # Auflösung (Anzahl Inkremente)

        self.g = None               # Konstanten
        self.rho = None

        self.fv = None              # Flugzeugkonfiguration
        self.ff = None
        self.m = None
        self.my = None
        self.h = None
        self.b = None
        self.s_ref = None
        self.lambd_k = None
        self.lambd_g = None

        self.ca_roll = None         # Aerodynamische Beiwerte
        self.ca_abheb = None
        self.cw_profil = None
        self.cwi = None


# ---Klassen für Ergebnisse der Berechnungsfunktionen---


@dataclass()
class Logfile:
    pass


@dataclass()
class ResTakeoff:

    does_takeoff: bool = None

    distance: float = None          # wird als False belegt, wenn vrollmax ausgegeben wird
    time: float = None              # wird als False belegt, wenn vrollmax ausgegeben wird
    vrollmax: float = None          # wird als False belegt, wenn distance und time erfolgreich verwendet

    # Inputdata
    inputdata: Plane = None
    # Logfile
    logfile: Logfile = None
