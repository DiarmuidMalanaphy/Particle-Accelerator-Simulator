import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import time
class Particle:

    """
        Base class for a series of particles namely : Proton, Electron, Neutron.

        The position defines its position within a 3d plane (x,y,z)
    
        The colour defines the default colour of the object, if undefined it will be a grey object.

        The size defines the radius of the particle, as all particles are represented as 3D spheres.

        The trail length is defaulted to 100, I would recommend leaving it as that but it modifies how long of a line is left behind the object - a larger line uses more system resources and could look uglier.

        If you don't want a trail you can either set trail_length to be 0 or set istrail to be False - setting trail to false is more efficient.

    """ 
    def __init__(self,x,y,z,colour,size,speed,weight = 1, trail_length = 100, istrail = True,isParticle = True,charge = 0):
        self.pos = np.array([x, y, z])
        self.speed = speed
        
        self.colour = colour
        self.size = size
        self.trail = []
        self.trail_length = trail_length
        self.isParticle = isParticle
        self.istrail = istrail
        self.last_update_time = time.time()

    

    def update(self,new_pos = None):
        if new_pos is None:
            current_time = time.time()
            delta_time = current_time - self.last_update_time
            self.last_update_time = current_time 
            self.pos += self.pos * self.speed * delta_time
        else:
            
            self.pos = new_pos

        if self.istrail:
            self.trail.append(self.pos.copy())
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)

        

        

    def draw(self):
        if self.isParticle:

            self.draw_particle()
        if self.istrail:
            self.draw_trail()    


    def draw_particle(self):
        glPushMatrix()
        glColor3f(self.colour[0],self.colour[1],self.colour[2])
        glTranslate(self.pos[0], self.pos[1], self.pos[2])
        glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, self.colour)
        quadric = gluNewQuadric()
        gluSphere(quadric, self.size, 32, 32)
        glPopMatrix()


    def draw_trail(self):
        glDisable(GL_LIGHTING)
        glColor4f(0.0, 1.0, 0.0, 0.3)  # Translucent green color for trail
        glBegin(GL_LINE_STRIP)
        for pos in self.trail:
            glVertex3f(pos[0], pos[1], pos[2])
        glEnd()
        glEnable(GL_LIGHTING)

    

