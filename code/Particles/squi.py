from Particles.squigglyparticle import SquigglyParticle

class Squi(SquigglyParticle):
    def __init__(self, coordinate, speed, colour=(0.0, 1.0, 0.0, 1.0), size=0.2, charge=0, time_speed=1):
        super().__init__(coordinate, colour, size, speed, time_speed=time_speed)
        self.squiggle_amplitude = 0.2
        self.squiggle_frequency = 8.0
