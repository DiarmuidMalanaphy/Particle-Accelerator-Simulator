from Particles.particle import Particle

class WBoson(Particle):
    def __init__(self, coordinates, speed, time_speed=1):
        super().__init__(coordinates, (0.0, 0.0, 1.0, 1.0), 0.6, speed, time_speed=time_speed)
