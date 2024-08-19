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


    @staticmethod
    def get_np_type(trail_length: int):
        np_trail_length = np.int64(int(trail_length))
        np_type = np.dtype([
            ('pos', float, (3, )),
            ('speed', float),
            ('colour', float, (3, )),
            ('radius', float),  # Assuming radius is a single float
            ('trail', float, (np_trail_length, 3)),  # trail is an array of shape (trail_length, 3)
            ('trail_length', int),
            ('isParticle', bool),
            ('istrail', bool),
            ('time_speed', float),
            ('last_update_time', float),
            ('particleID', int)
        ])
        return np_type

    def __init__(self,x,y,z,colour,radius,speed,weight = 1, trail_length = 100, istrail = True,isParticle = True,charge = 0,time_speed = 1):
        self.pos = np.array([x, y, z])
        self.speed = speed
        
        self.colour = colour
        self.radius = radius
        self.trail = []
        self.trail_length = trail_length * time_speed
        self.isParticle = isParticle
        self.istrail = istrail
        self.time_speed = time_speed
        self.last_update_time = time.time()

        self.particleID = None

    @staticmethod
    def update_particles(particles):
        current_time = time.time()
        delta_time = current_time - particles['last_update_time']
        
        particles['pos'] += particles['pos'] * 3 * particles['speed'] / particles['time_speed'][:, np.newaxis] * delta_time[:, np.newaxis]
        
        particles['last_update_time'] = current_time

        mask = particles['istrail']

        particles['trail_index'][mask] = (particles['trail_index'][mask] + 1) % particles['trail_length'][mask]

        trail_indices = particles['trail_index'][mask]
        particles['trail'][mask, trail_indices] = particles['pos'][mask]
        
        

    def update(self,new_pos = None):
        if new_pos is None:
            current_time = time.time()
            delta_time = current_time - self.last_update_time
            self.last_update_time = current_time 
            self.pos += self.pos * 3 * self.speed/self.time_speed * delta_time
        else:
            
            self.pos = new_pos

        if self.istrail:
            self.trail.append(self.pos.copy())
            if len(self.trail) > self.trail_length:
                self.trail.pop(0)

        
    def updateID(self,newID):
        self.particleID = newID
        

    def draw(self):
        self.last_update_time = time.time() 
        
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
        gluSphere(quadric, self.radius, 32, 32)
        glPopMatrix()


    def draw_trail(self):
        glDisable(GL_LIGHTING)
        glColor4f(0.0, 1.0, 0.0, 0.3)  # Translucent green color for trail
        glBegin(GL_LINE_STRIP)
        for pos in self.trail:
            glVertex3f(pos[0], pos[1], pos[2])
        glEnd()
        glEnable(GL_LIGHTING)

    

