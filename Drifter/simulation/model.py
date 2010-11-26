from math import *

from landmass.layer import Layer
from landmass.object import LayeredObject

class Model(object):
    def __init__(self):
        self.objects = [LayeredObject((128,128,128),(1,0,0),(0.99,0.01,0))]
        self.objects[0].add_layer(Layer([(1.1, i*pi/8) for i in range(16)]))
        self.objects[0].add_layer(Layer([(0.2,pi/4),
                            (0.1,pi/2),
                            (0.2,5*pi/8),
                            (0.25,7*pi/8),
                            (0.25,pi),
                            (0.15,3*pi/4),
                            (0.1,5*pi/4),
                            (0.3,5*pi/4),
                            (0.2,3*pi/2),
                            (0.15,7*pi/4)]))
