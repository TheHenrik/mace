from dataclasses import dataclass
from typing import List


class MassTable():
    totalMass: int = None
    masses: dict = None


    def output_to_cmd():
        print(f'Weights of the Aircraft:')
