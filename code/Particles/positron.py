from Particles.particle import Particle

class Positron(Particle):
    def __init__(self, coordinate,speed,colour = (1.0, 0.0, 0.0, 1.0), size = 0.1, charge = 1,time_speed = 1):
        super().__init__(coordinate, colour,size,speed,time_speed = time_speed)  # Red color, size 0.2
