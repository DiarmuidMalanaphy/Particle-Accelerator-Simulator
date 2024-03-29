from particle import Particle

#Anti - particle of positron - same mass however opposite charge
class Electron(Particle):
    def __init__(self, x, y, z,speed,colour = (1.0, 0.0, 0.0, 1.0), size = 0.1,charge = -1,time_speed = 1):
        super().__init__(x, y, z, colour, size,speed,charge = -1,time_speed = time_speed)  # Blue color, size 0.05, half transparent