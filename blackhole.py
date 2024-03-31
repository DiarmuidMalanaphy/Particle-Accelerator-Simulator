
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np


from particle import Particle



class Blackhole(Particle):
    def __init__(self, x, y, z, speed, colour=(0.0, 0.0, 0.0, 1.0), size=0.2, charge=0, time_speed=1):
        super().__init__(x, y, z, colour, size, speed, weight=1, trail_length=0, istrail=False, isParticle=True, charge=charge, time_speed=time_speed)
        self.max_size = 10.0
        self.growth_rate = 0.01

    def update(self, new_pos=None):
        super().update(new_pos)
        self.radius = self.radius * (1 + (self.growth_rate * self.time_speed))



    def draw_particle(self):
        glPushMatrix()
        glColor3f(self.colour[0], self.colour[1], self.colour[2])
        glTranslate(self.pos[0], self.pos[1], self.pos[2])
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.colour)
        quadric = gluNewQuadric()
        gluSphere(quadric, self.radius, 32, 32)
        glPopMatrix()

    def check_collision(self, position):
        distance = np.sqrt((self.pos[0] - position[0])**2 + (self.pos[1] - position[1])**2 + (self.pos[2] - position[2])**2)
        return distance <= self.radius