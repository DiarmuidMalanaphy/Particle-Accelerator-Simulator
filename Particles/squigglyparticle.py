from Particles.particle import Particle
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import time

class SquigglyParticle(Particle):
    def __init__(self, x, y, z, colour, radius, speed, weight=1, trail_length=100, istrail=True, isParticle=True, charge=0, time_speed=1):
        super().__init__(x, y, z, colour, radius, speed, weight, trail_length, istrail, isParticle, charge, time_speed)
        self.squiggle_amplitude = 0.1
        self.squiggle_frequency = 5.0
        self.squiggle_phase = 0.0

    def update(self, new_pos=None):
        super().update(new_pos)
        self.squiggle_phase += 0.1

    def draw_particle(self):
        glPushMatrix()
        glColor3f(self.colour[0], self.colour[1], self.colour[2])
        glTranslate(self.pos[0], self.pos[1], self.pos[2])
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.colour)

        quadric = gluNewQuadric()
        glPushMatrix()
        glScalef(1.0, 0.5, 1.0)  # Flatten the sphere vertically
        gluSphere(quadric, self.radius, 32, 32)
        glPopMatrix()

        glPushMatrix()
        glTranslatef(0.0, self.radius * 0.5, 0.0)  # Move the squiggly part above the flattened sphere
        self.draw_squiggly_part()
        glPopMatrix()

        glPopMatrix()

    def draw_squiggly_part(self):
        glBegin(GL_LINE_STRIP)
        for i in range(100):
            t = i / 100.0
            x = t * self.radius * 0.5
            y = self.squiggle_amplitude * np.sin(self.squiggle_frequency * t + self.squiggle_phase)
            z = 0.0
            glVertex3f(x, y, z)
        glEnd()