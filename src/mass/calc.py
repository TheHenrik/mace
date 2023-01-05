from ..domain.default_params import Params
from  ..domain.vector import Vectorcalc



def estimate_weight(flugzeug, parameters = Params):
    for segment in flugzeug.fluegel.fluegelsegment:
        flugzeug.mass.totalMass += getWeightSegment(segment,parameters)  
    
    return flugzeug


def getWeightSegment(segment,parameter):
    #return volume*parameter.styro + area*parameter.kohle
    pass
