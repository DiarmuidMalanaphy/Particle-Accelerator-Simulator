from Particles.particle import Particle

#Teal: (0.0, 0.5, 0.5, 1.0)
class Quark(Particle):
    def __init__(self, x, y, z,speed,colour = (0.0, 0.5, 0.5, 1.0), quark_type = 'D', charge = 1/2,time_speed = 1):
        quark_sizes = {
                'D': 0.04,
                'C': 0.08,
                'S': 0.15,
            }
        
        super().__init__(x, y, z, colour,quark_sizes[quark_type],speed,time_speed = time_speed)


#make it have a random mass and colour <- make it change the speed based on this