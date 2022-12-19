from ..domain.default_params import params
from ..domain.plane import *


def estimate_weight(flugzeug:Flugzeug, parameters = params):
    for segment in flugzeug.fluegel.fluegelsegment:
        flugzeug.mass.totalMass += getWeightSegment(segment,parameters)  
    
    return flugzeug



def getWeightSegment(segment,parameter):
    volume = getVolume(segment)
    area = getArea(segment)
    return volume*parameter.styro + area*parameter.kohle


#Implement @Cache
def getVolume(segment):
    return 0


#Implement @Cache
def getArea(segment):
    return 0