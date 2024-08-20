from Particles.particle import Particle
import numpy as np

class Pion(Particle):
    
    def __init__(self, coordinate,speed,colour = (1.0, 0.5, 0.0, 1.0), size = 0.1, charge = 1/2,time_speed = 1):
        super().__init__(coordinate, colour,size,speed,time_speed = time_speed)
