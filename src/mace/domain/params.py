from dataclasses import dataclass

@dataclass
class Constants:
    g:float = 9.81


@dataclass
class material:
     name: str
     use: str
     count: int



class Parameter:
    constants = Constants

