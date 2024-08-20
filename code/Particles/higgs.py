from Particles.particle import Particle

class HiggsBoson(Particle):
    def __init__(self, coordinate, speed, time_speed=1):
        super().__init__(coordinate, (1.0, 0.0, 1.0, 1.0), 0.3, speed, time_speed=time_speed)
