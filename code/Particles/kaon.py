from Particles.particle import Particle


class Kaon(Particle):
    def __init__(self, coordinate,speed,colour = (0.0, 0.0, 1.0, 1.0), size = 0.075,time_speed = 1 ):
        super().__init__(coordinate, colour, size,speed,time_speed = time_speed)  # Blue color, size 0.15
