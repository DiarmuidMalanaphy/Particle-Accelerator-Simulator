from Particles.particle import Particle
import numpy as np

class Photon(Particle):
    def __init__(self, x, y, z,speed,colour = (0.0, 0.0, 1.0, 1.0), size = 0.05,time_speed = 1):
        super().__init__(x, y, z, colour, size,speed,isParticle=False , time_speed = time_speed)  # Blue color, size 0.15