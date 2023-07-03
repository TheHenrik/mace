from mace.aero.implementations.avl import athenavortexlattice
from mace.aero.implementations.viscous_drag import ViscousDrag
from mace.domain import Plane

class Aerodynamics:
    def __init__(self, plane: Plane):
        """
        :param plane: Plane object
        
        Initializes the aerodynamic analysis.
        """
        self.plane = plane
        self.AVL = athenavortexlattice.AVL(self.plane)
        self.XFOIL = ViscousDrag(self.plane)
        
    def evaluate(self, CL: float, V: float) -> None:
        """
        :param CL: Lift coefficient
        :param V: Velocity

        Returns the drag coefficient for a given lift coefficient.
        """
        self.plane.aero_coeffs.lift_coefficient = CL
        self.plane.aero_coeffs.velocity = V
        
        self.AVL.run_avl(lift_coefficient=CL)
        self.AVL.read_avl_output()
        self.XFOIL.evaluate()
        