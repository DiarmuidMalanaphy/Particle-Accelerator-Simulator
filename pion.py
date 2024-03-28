from particle import Particle
import numpy as np

class Pion(Particle):
    def __init__(self,energy,colour = (0.0, 1.0, 0.0, 1.0), size = 0.05):
        angle_xy = np.random.uniform(0, 2 * np.pi)
        angle_z = np.random.uniform(0, np.pi)
        speed = 1
        
        

        particle_x = np.cos(angle_xy) * np.sin(angle_z) * speed
        particle_y = np.sin(angle_xy) * np.sin(angle_z) * speed
        particle_z = np.cos(angle_z) * speed
        super().__init__(particle_x, particle_y, particle_z,  colour, size,speed) 