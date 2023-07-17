from mace.aero.implementations.avl import athenavortexlattice
from mace.aero.implementations.viscous_drag import ViscousDrag
from mace.domain import Plane
from mace.domain.vehicle import Vehicle

class Aerodynamics:
    def __init__(self, plane: Vehicle):
        """
        :param plane: Plane object
        
        Initializes the aerodynamic analysis.
        """
        self.plane = plane
        self.AVL = athenavortexlattice.AVL(self.plane)
        self.XFOIL = ViscousDrag(self.plane)
        
    def evaluate(self, CL: float, V: float, FLAP: float = 0, ALPHA: float = None) -> None:
        """
        :param CL: Lift coefficient
        :param V: Velocity

        Returns the drag coefficient for a given lift coefficient.
        """
        self.plane.aero_coeffs.lift_coefficient = CL
        self.plane.aero_coeffs.velocity = V
        self.plane.aero_coeffs.flap_angle = FLAP
        
        if ALPHA != None:
            self.plane.aero_coeffs.angle_of_attack = ALPHA
            self.AVL.run_avl(angle_of_attack=ALPHA, flap_angle=FLAP)
        else:
            self.AVL.run_avl(lift_coefficient=CL, flap_angle=FLAP)
            
        self.AVL.read_avl_output()
        self.XFOIL.evaluate()
        
        for fuselage in self.plane.fuselages.values():
            CD_fuse = fuselage.get_drag_coefficient(V, self.plane.avl.outputs.s_ref)
            self.plane.aero_coeffs.drag_coeff.cd_fuse += CD_fuse
            self.plane.aero_coeffs.drag_coeff.cd_tot += CD_fuse
        
        for wheel in self.plane.landing_gear.wheels:
            CD_wheel = wheel.get_drag_coefficient(V, self.plane.avl.outputs.s_ref)
            self.plane.aero_coeffs.drag_coeff.cd_wheels += CD_wheel
            self.plane.aero_coeffs.drag_coeff.cd_tot += CD_wheel