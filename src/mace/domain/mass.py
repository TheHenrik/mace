from dataclasses import dataclass


@dataclass
class MassTable:
    totalMass: int = None
    masses: dict = None

    def output_to_cmd(self):
        print(f"Weights of the Aircraft: {self.totalMass}")
