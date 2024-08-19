from Particles.particle import Particle
#Lime: (0.75, 1.0, 0.0, 1.0)
#The muon, on the other hand, has a mass 208 times that of an electron so its mass is approximately 1/9 of the mass of a proto
class Gluon(Particle):
    def __init__(self, x, y, z,speed,colour = (0.75, 1.0, 0.0, 1.0), size = 0.2, charge = 1/2,time_speed = 1):
        super().__init__(x, y, z, colour,size,speed,isParticle=False,time_speed = time_speed)
