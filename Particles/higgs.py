from Particles.particle import Particle

class HiggsBoson(Particle):
    def __init__(self, x, y, z, speed, time_speed=1):
        super().__init__(x, y, z, (1.0, 0.0, 1.0, 1.0), 0.3, speed, time_speed=time_speed)