import time
import glfw
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pymunk
import pybullet as p
import pybullet_data
from electron import Electron
from gluon import Gluon
from kaon import Kaon
from muon import Muon
from photon import Photon
from pion import Pion
from positron import Positron
from flash import Flash
from quark import Quark
from tau import Tau
from enum import Enum

import imgui
from imgui.integrations.glfw import GlfwRenderer



#Notes to take

"""

Make it so you can enter different kinetic enrgies, maybe with a scale?
add a noise - Kaboom, 
if you make the mass high enough maybe black hole
Make sure that energy is conserved
Make the reaction actually occur in a reaction chamber
Make the reactions have a cloud of energy intially so the weird gap of collision doesn't exist.
Different time controls - So make it go at 3x slower 

Make timestop t and ensure that restart is just space and not space and m
Add a background

make it circle around

Next addons - Make a summarisation at the end - displaying the amount of kinetic energy, number of particles created and the distribution


Next next step - create an actual simulation of derived ATLAS data and actually understand ROOT


    RULES speed is between 0-1 and represents 0 to c
        - make em able to make it 2 and increase radius to 1 for that case and explode the earth

        


"""

class Mode(Enum):
    Educational  = True
    Fun = False




"""
    3D Simulation of a particle accelerator with different modes for fun or education 

"""

class Simulation():
    def __init__(self,mode = Mode.Educational):
        self.mode = mode
        self.start_simulating()
        




    def initialize_glfw(self):
    
        if not glfw.init():
            raise Exception("glfw can not be initialized!")

        window = glfw.create_window(1080, 900, "Proton-Proton Collision Simulation", None, None)

        if not window:
            glfw.terminate()
            raise Exception("glfw window can not be created!")

        glfw.set_window_pos(window, 300, 150)
        glfw.make_context_current(window)

        return window

       



    def logarithmic_slider(self,label, value, max_nines):
        # Directly map the value to a "number of nines" representation
        if value >= 1.0:
            slider_pos = max_nines
        else:
            slider_pos = max(0, min(max_nines, int(np.floor(-np.log10(1 - value)))))

        # Adjust the slider
        if value == 1:
            
            changed, new_slider_pos = imgui.slider_int(label, slider_pos, 0, max_nines, f"c")
        else:
            changed, new_slider_pos = imgui.slider_int(label, slider_pos, 0, max_nines, f"{value}c")
        

        if changed:
            # Convert back to the float value
            if new_slider_pos == max_nines:
                new_value = 1
            else:
                new_value = 1 - 10 ** (-new_slider_pos - 1)

        return changed, new_value if changed else value




    def handle_keyboard_input(self):
        # Update camera position with arrow keys
        if glfw.get_key(self.window, glfw.KEY_UP) == glfw.PRESS:
            self.camera_pos += self.camera_front * self.camera_position_speed
        if glfw.get_key(self.window, glfw.KEY_DOWN) == glfw.PRESS:
            self.camera_pos -= self.camera_front * self.camera_position_speed
        if glfw.get_key(self.window, glfw.KEY_LEFT) == glfw.PRESS:
            self.camera_pos -= np.cross(self.camera_front, self.camera_up) * self.camera_position_speed
        if glfw.get_key(self.window, glfw.KEY_RIGHT) == glfw.PRESS:
            self.camera_pos += np.cross(self.camera_front, self.camera_up) * self.camera_position_speed
        #if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
        #    camera_pos += camera_up * position_speed
        if glfw.get_key(self.window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS:
            self.camera_pos -= self.camera_up * self.camera_position_speed

        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            pitch = np.radians(self.camera_angle_speed)
            self.camera_front = self.rotate_vector(self.camera_front, pitch, np.cross(self.camera_front, self.camera_up))
            self.camera_up = np.cross(np.cross(self.camera_front, self.camera_up), self.camera_front)
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            pitch = np.radians(-self.camera_angle_speed)
            self.camera_front = self.rotate_vector(self.camera_front, pitch, np.cross(self.camera_front, self.camera_up))
            self.camera_up = np.cross(np.cross(self.camera_front, self.camera_up), self.camera_front)
        
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            yaw = np.radians(self.camera_angle_speed)
            self.camera_front = self.rotate_vector(self.camera_front, yaw, self.camera_up)
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            yaw = np.radians(-self.camera_angle_speed)
            self.camera_front = self.rotate_vector(self.camera_front, yaw, self.camera_up)
        
        
        angle_range = 1.0 #There's more viewing range but it hates you using it
        self.camera_front[0] = (self.camera_front[0] + angle_range) % (2 * angle_range) - angle_range
        self.camera_front[1] = max(-angle_range, min(angle_range, self.camera_front[1]))

        self.camera_front = self.camera_front / np.linalg.norm(self.camera_front)

        #TimeStop and restarting experiment 


        #Starts the experiment
        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS:
            self.simulating = True
            self.time_stop = False

        #Stops the experiment

        if glfw.get_key(self.window,glfw.KEY_M) == glfw.PRESS:
            self.simulating = False

        #Stops time
        if glfw.get_key(self.window, glfw.KEY_T) == glfw.PRESS:
            self.time_stop = True
        #Starts time
        if glfw.get_key(self.window, glfw.KEY_Y) == glfw.PRESS:
            self.time_stop = False

    def rotate_vector(self, vector, angle, axis):
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        return vector * cos_angle + np.cross(axis, vector) * sin_angle + axis * np.dot(axis, vector) * (1 - cos_angle)


    def initialise_collision_boxes(self,cylinder_radius,cylinder_height):


        positron_collision = p.createCollisionShape(p.GEOM_SPHERE, radius=0.2)
        positron_visual = p.createVisualShape(p.GEOM_SPHERE, radius=0.2, rgbaColor=[1, 0, 0, 1])
        positron_id = p.createMultiBody(baseMass=1,
                                        baseCollisionShapeIndex=positron_collision,
                                        baseVisualShapeIndex=positron_visual,
                                        basePosition=self.positron_pos)
        
        
        
        electron_collision = p.createCollisionShape(p.GEOM_SPHERE, radius=0.2)
        electron_visual = p.createVisualShape(p.GEOM_SPHERE, radius=0.2, rgbaColor=[0, 0, 1, 1])
        electron_id = p.createMultiBody(baseMass=1, 
                                    baseCollisionShapeIndex=electron_collision,
                                    baseVisualShapeIndex=electron_visual,
                                    basePosition=self.electron_pos)
        
        cylinder_collision_shape = p.createCollisionShape(
            shapeType=p.GEOM_CYLINDER,
            radius=cylinder_radius,  # This should match the OpenGL cylinder radius
            height=cylinder_height,  # This should match the OpenGL cylinder height
            collisionFramePosition=[0,0,0]
        
        )

        cylinder_visual_shape = p.createVisualShape(
            shapeType=p.GEOM_CYLINDER,
            radius=cylinder_radius,  # Match the radius used in OpenGL
            length=cylinder_height,  # Use 'length' for height here, to match OpenGL
            rgbaColor=[0.6, 0.6, 0.6, 1],
            visualFramePosition=[0,0,0]
        )

        cylinder_id = p.createMultiBody(
            baseMass=0,  # Static body if mass is 0
            baseCollisionShapeIndex=cylinder_collision_shape,
            baseVisualShapeIndex=cylinder_visual_shape,
            basePosition=[0, 0, 0]  # Centered at the origin, as in your OpenGL code
        )


        return positron_id, electron_id, cylinder_id
    


    def __calculate_total_energy(self):
        #m of electron/positron  is 9.1093837 × 10-31 kilograms - for computational efficiency  9.1*10*31
        def particle_kinetic_energy(v, m):
            """
            Calculate the relativistic kinetic energy given a velocity and mass.
            - v is the velocity of the particle.
            - m is the mass of the particle.
            Returns kinetic energy in eV.
            """
            c = 299792458  # Speed of light in m/s

            # Calculate the Lorentz factor
            gamma = 1 / np.sqrt(1 - (v**2 / c**2))

            # Calculate the relativistic kinetic energy in joules
            KE_joules = (gamma - 1) * m * c**2

            # Convert kinetic energy to eV
            KE_eV = KE_joules / (1.602176634e-19)
            return KE_eV

        # Assuming positron_speed and electron_speed are defined and are fractions of the speed of light (e.g., 0.99 for 99% of the speed of light)
        m = 9.1e-31  # Mass of electron/positron in kg
        c = 299792458
        #positron_speed = self.relative_particle_speed * c  # relative% speed of light
        #electron_speed = self.relative_particle_speed * c  # relative% speed of light
        unified_speed = self.relative_particle_speed * c # Unify them for efficiency

        # Calculate kinetic energy for both particles
        #positron_kinetic_energy = particle_kinetic_energy(positron_speed, m)
        total_kinetic_energy_eV = 2 * particle_kinetic_energy(unified_speed, m)

        # Sum of kinetic energies in eV
        #total_kinetic_energy_eV = positron_kinetic_energy + electron_kinetic_energy

        # Convert total kinetic energy to GeV
        total_kinetic_energy_GeV = total_kinetic_energy_eV / 10**9
        total_kinetic_energy_MeV = total_kinetic_energy_eV / 10**6

        print(f"Total Kinetic Energy: {total_kinetic_energy_MeV} MeV, or {total_kinetic_energy_GeV} GeV")
        
        #https://public-archive.web.cern.ch/en/lhc/Facts-en.html
        rest_energy_eV =  2 * m * (c**2) / (1.602176634e-19)

        total_energy_eV = total_kinetic_energy_eV + rest_energy_eV 

        total_energy_MeV = total_energy_eV / 10**6

        total_energy_GeV = total_energy_eV / 10**9


        

        print(f"Total Kinetic Energy: {total_energy_MeV} MeV, or {total_energy_GeV} GeV")

        return(total_energy_eV,total_energy_MeV,total_energy_GeV)
        

    def generate_particles(self):

        total_energy_eV, total_energy_MeV, total_energy_GeV = self.__calculate_total_energy()





        if self.mode.value: # Educational
            return self.generate_educational_particles(total_energy_eV,total_energy_MeV,total_energy_GeV)
        
        else:
            return self.generate_fun_particles(total_energy_eV,total_energy_MeV,total_energy_GeV)


    def generate_fun_particles(self, total_energy_eV, total_energy_MeV, total_energy_GeV):
        particles = []
        remaining_energy_eV = total_energy_eV
        max_particles = 100
        energy_factor = (1-self.relative_particle_speed)*12800
        print(energy_factor)
         
        

        while remaining_energy_eV > 0 and len(particles) < max_particles:
            if np.random.rand() < 0.7:
                particle_type = np.random.choice(["Photon","Pion", "Muon"])
            else:
                particle_type = np.random.choice(["Tau", "Gluon", "Quark"])

            angle_xy = np.random.uniform(0, 2 * np.pi)
            angle_z = np.random.uniform(0, np.pi)
            speed = np.random.uniform(0.2, 1)

            particle_x = np.cos(angle_xy) * np.sin(angle_z) * speed
            particle_y = np.sin(angle_xy) * np.sin(angle_z) * speed
            particle_z = np.cos(angle_z) * speed

            if particle_type == "Photon":
                particle = Photon(particle_x, particle_y, particle_z, speed,time_speed = self.time_speed)
                particle_radius = 0.05
                particle_energy = 0.01 * total_energy_eV * energy_factor
            
            elif particle_type == "Muon":
                particle = Muon(particle_x, particle_y, particle_z, speed,time_speed = self.time_speed)
                particle_radius = 0.2
                particle_energy = 0.04 * total_energy_eV * energy_factor
            elif particle_type == "Tau":
                particle = Tau(particle_x, particle_y, particle_z, speed,time_speed = self.time_speed)
                particle_radius = 0.25
                particle_energy = 0.05 * total_energy_eV * energy_factor
            elif particle_type == "Gluon":
                particle = Gluon(particle_x, particle_y, particle_z, speed,time_speed = self.time_speed)
                particle_radius = 0.3
                particle_energy = 0.06 * total_energy_eV * energy_factor
            
            elif particle_type == "Pion":
                particle = Pion(particle_x, particle_y, particle_z, speed,time_speed = self.time_speed)
                particle_energy = 0.03 * total_energy_eV * energy_factor

            else:  # Quark
                particle = Quark(particle_x, particle_y, particle_z, speed,time_speed = self.time_speed)
                particle_radius = 0.35
                particle_energy = 0.07 * total_energy_eV * energy_factor
            remaining_energy_eV -= particle_energy
            
            particles.append(particle)
                

        self.flash_manager.add_flash(
            position=[(self.positron_pos[0] + self.electron_pos[0]) / 2,
                    (self.positron_pos[1] + self.electron_pos[1]) / 2,
                    (self.positron_pos[2] + self.electron_pos[2]) / 2],
            size=2,
            brightness=10,
            duration=3
        )

        return particles
        


    def generate_educational_particles(self,total_energy_eV, total_energy_MeV, total_energy_GeV):
        c = 299792458
        
        
        
        
        

        particles = []

        def generate_directions(num_particles):
            self.flash_manager.add_flash(position=[(self.positron_pos[0] + self.electron_pos[0]) / 2, (self.positron_pos[1] + self.electron_pos[1]) / 2, (self.positron_pos[2] + self.electron_pos[2]) / 2], size=0.2, brightness=1.0, duration=2)
            directions = []
            total_vector = np.array([0.0, 0.0, 0.0])

            for _ in range(num_particles - 1):
                # Generate a random 3D unit vector
                phi = np.random.uniform(0, 2 * np.pi)*0.5
                theta = np.random.uniform(0,  np.pi)*0.5
                x = np.sin(theta) * np.cos(phi)
                y = np.sin(theta) * np.sin(phi)
                z = np.cos(theta)
                
                direction = np.array([x, y, z])
                directions.append(direction)
                total_vector += direction

            # Calculate the last direction to ensure momentum conservation
            last_direction = -total_vector
            directions.append(last_direction)

            return directions

        if total_energy_MeV<210: # Photons

            
            self.flash_manager.add_flash(position=[(self.positron_pos[0] + self.electron_pos[0]) / 2, (self.positron_pos[1] + self.electron_pos[1]) / 2, (self.positron_pos[2] + self.electron_pos[2]) / 2], size=0.2, brightness=1.0, duration=2)
            # Any number of opposite photons can be created, conserving momentum
            choice = np.random.choice([2, 3, 4, 5], p=[0.53, 0.32, 0.11, 0.04])
            
            #print(choice)

            directions = generate_directions(choice)

            

            for direction in directions:
                speed = 1
                particle_x = direction[0] * speed
                particle_y = direction[1] * speed
                particle_z = direction[2] * speed
                particle = Photon(particle_x,particle_y,particle_z,1,time_speed = self.time_speed)
                particles.append(particle)
                



        elif total_energy_GeV<3.4 and total_energy_MeV>210:#Muons
            directions = generate_directions(2)# <- for the two resulting muons 

            muon_m = 1.883531627e-28
            rest_energy_eV_muon =  muon_m * (c**2) / (1.602176634e-19)
            kinetic_energy_per_muon = (total_energy_eV - 2 * rest_energy_eV_muon) / 2

            
            v = c * np.sqrt(1 - (1 / ((kinetic_energy_per_muon / (rest_energy_eV_muon)) + 1))**2)
            speed = v/c
            self.flash_manager.add_flash(position=[(self.positron_pos[0] + self.electron_pos[0]) / 2, (self.positron_pos[1] + self.electron_pos[1]) / 2, (self.positron_pos[2] + self.electron_pos[2]) / 2], size=0.5, brightness=10*speed, duration=2)
            for direction in directions:
                particle_x = direction[0] * speed
                particle_y = direction[1] * speed
                particle_z = direction[2] * speed
                particle = Muon(particle_x,particle_y,particle_z,speed,time_speed = self.time_speed)
                particles.append(particle)
            


        


        elif total_energy_GeV>=3.4 and total_energy_GeV<9.4: #Tau
            directions = generate_directions(2)
            
            tau_m = 3.167e-27
            rest_energy_eV_tau =  tau_m * (c**2) / (1.602176634e-19)
            kinetic_energy_per_tau = (total_energy_eV - 2 * rest_energy_eV_tau) / 2
            v = c * np.sqrt(1 - (1 / ((kinetic_energy_per_tau / (rest_energy_eV_tau)) + 1))**2)
            speed = v/c
            self.flash_manager.add_flash(position=[(self.positron_pos[0] + self.electron_pos[0]) / 2, (self.positron_pos[1] + self.electron_pos[1]) / 2, (self.positron_pos[2] + self.electron_pos[2]) / 2], size=0.5, brightness=10*speed, duration=2)
            for direction in directions:
                
                particle_x = direction[0] * speed
                particle_y = direction[1] * speed
                particle_z = direction[2] * speed
                particle = Tau(particle_x,particle_y,particle_z,speed,time_speed = self.time_speed)
                particles.append(particle)

        elif total_energy_GeV>=9.4 and total_energy_GeV<30: #gamma gluon gluon
            
            directions = generate_directions(3)
            speed = 1.3 # C -> the gluons are incredibly high powered (I modified it to make it cooler and make it slightly more explosive and fast)
            self.flash_manager.add_flash(position=[(self.positron_pos[0] + self.electron_pos[0]) / 2, (self.positron_pos[1] + self.electron_pos[1]) / 2, (self.positron_pos[2] + self.electron_pos[2]) / 2], size=2, brightness=10*speed, duration=3)
            for direction in directions:
                
                particle_x = direction[0] * speed
                particle_y = direction[1] * speed
                particle_z = direction[2] * speed
                particle = Gluon(particle_x,particle_y,particle_z,speed,time_speed = self.time_speed)
                particles.append(particle)
            

        elif total_energy_GeV>=30 and total_energy_GeV<80: #quark quark gluon
            directions = generate_directions(3)

            particle_x = directions[2][0] * 1
            particle_y = directions[2][1] * 1
            particle_z = directions[2][2] * 1
            particle = Gluon(particle_x,particle_y,particle_z,1,time_speed = self.time_speed)
            particles.append(particle)


            quark_masses = {
                'D': 4.9e6,  # Down quark mass in eV/c^2 (using the average of the range)
                'C': 1.270e9,  # Charm quark mass in eV/c^2
                'S': 1.01e8,  # Strange quark mass in eV/c^2
                #'T': 1.72e11  # Top quark mass in eV/c^2  WE EXCLUDE THIS ONE BECAUSE THE MASS IS TOO HIGH
            }

            quark_types = ['D', 'C', 'S']
            quark_weights = [quark_masses[q] for q in quark_types]
            total_weight = sum(quark_weights)
            quark_probs = [w / total_weight for w in quark_weights]

            chosen_quarks = np.random.choice(quark_types, size=2, replace=False, p=quark_probs)



            for i, quark_type in enumerate(chosen_quarks):
                quark_mass = quark_masses[quark_type]
                rest_energy_eV_quark = quark_mass

                quark_total_energy_eV = total_energy_eV - 2 * rest_energy_eV_quark
                kinetic_energy_per_quark = quark_total_energy_eV / 2
                #v = c * np.sqrt(1 - (1 / ((kinetic_energy_per_tau / (rest_energy_eV_tau)) + 1))**2)
                v = c * np.sqrt(1 - (1 / ((kinetic_energy_per_quark / (rest_energy_eV_quark)) + 1))**2)
                speed = v / c

                

                particle_x = directions[i][0] * speed
                particle_y = directions[i][1] * speed
                particle_z = directions[i][2] * speed

                particle = Quark(particle_x, particle_y, particle_z, speed,time_speed = self.time_speed)
                particles.append(particle)

            
            

                self.flash_manager.add_flash(
                    position=[(self.positron_pos[0] + self.electron_pos[0]) / 2,
                            (self.positron_pos[1] + self.electron_pos[1]) / 2,
                            (self.positron_pos[2] + self.electron_pos[2]) / 2],
                    size=0.5,
                    brightness=5,
                    duration=2
                )
    

        #http://www.quantumdiaries.org/2010/05/10/the-z-boson-and-resonances/
        elif total_energy_GeV>=80 and total_energy_GeV<124: #Z Boson -> produces two muons

            directions = generate_directions(2)# <- for the two resulting muons 

            muon_m = 1.883531627e-28
            rest_energy_eV_muon =  muon_m * (c**2) / (1.602176634e-19)
            kinetic_energy_per_muon = (total_energy_eV - 2 * rest_energy_eV_muon) / 2

            
            v = c * np.sqrt(1 - (1 / ((kinetic_energy_per_muon / (rest_energy_eV_muon)) + 1))**2)
            speed = v/c
            self.flash_manager.add_flash(position=[(self.positron_pos[0] + self.electron_pos[0]) / 2, (self.positron_pos[1] + self.electron_pos[1]) / 2, (self.positron_pos[2] + self.electron_pos[2]) / 2], size=0.5, brightness=10*speed, duration=2)
            for direction in directions:
                particle_x = direction[0] * speed
                particle_y = direction[1] * speed
                particle_z = direction[2] * speed
                particle = Muon(particle_x,particle_y,particle_z,speed,time_speed = self.time_speed)
                particles.append(particle)
            pass

        elif total_energy_GeV>=124 and total_energy_GeV< 160: # Higgs Boson
            pass

        elif total_energy_GeV>=160 and total_energy_GeV< 200: #W+ Boson
            pass

        else:#Who knows
            pass
        return(particles)
    
    

    def start_simulating(self):
        self.window = self.initialize_glfw()
        imgui.create_context()
        impl = GlfwRenderer(self.window)


        glEnable(GL_DEPTH_TEST)  # Enable depth testing for 3D rendering
        glEnable(GL_BLEND)  # Enable blending for transparency
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)  # Set blending function
        glEnable(GL_LIGHTING)  # Enable lighting
        glEnable(GL_LIGHT0)  # Enable a light source
        glLight(GL_LIGHT0, GL_POSITION, (0.0, 0.0, 1.0, 0.0))  # Set light position
        glEnable(GL_COLOR_MATERIAL)  # Enable color material mode
        glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)  # Set color material properties

        # Set up a perspective projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(60, (720 / 600), 0.1, 100.0)  # Increase the far clipping plane distance
        glMatrixMode(GL_MODELVIEW)


        # Set camera position and orientation (inside the cylinder, looking towards the center)
        self.eye_x, self.eye_y, self.eye_z = 3.0, 3.0, 25.0  # Position the camera slightly off-center and tilted
        self.center_x, self.center_y, self.center_z = 0.0, 0.0, 0.0  # Look towards the center of the cylinder
        self.up_x, self.up_y, self.up_z = 0.0, 1.0, 0.0  # Set the up direction
        gluLookAt(self.eye_x, self.eye_y, self.eye_z, self.center_x, self.center_y, self.center_z, self.up_x, self.up_y, self.up_z)


        self.camera_pos = np.array([self.eye_x, self.eye_y, self.eye_z], dtype=np.float32)
        self.camera_front = np.array([self.center_x - self.eye_x, self.center_y - self.eye_y, self.center_z - self.eye_z], dtype=np.float32)
        self.camera_front = self.camera_front / np.linalg.norm(self.camera_front)
        self.camera_up = np.array([self.up_x, self.up_y, self.up_z], dtype=np.float32)
        self.camera_position_speed = 0.3
        self.camera_angle_speed = 1


        self.flash_manager = Flash()


        physicsClient = p.connect(p.DIRECT)
        # physicsClient = p.connect(p.GUI)
        cylinder_radius = 5
        cylinder_height = 100


        self.positron_pos = [0, 0, np.round((-cylinder_height / 2 + 1.5))]  # Adjust start position
        self.electron_pos = [0, 0, np.round(cylinder_height / 2 - 1.5)]  # Adjust start position
    
        

        
        
        positron_id, electron_id, cylinder_id = self.initialise_collision_boxes(cylinder_radius,cylinder_radius)
        


        

        self.relative_particle_speed = 0.9

        particles = []
        
        self.collided = False
        particles_created = False
        self.simulating = False
        self.time_stop = False
        positron = Positron(self.positron_pos[0], self.positron_pos[1], self.positron_pos[2], 0.2)
        electron = Electron(self.electron_pos[0], self.electron_pos[1], self.electron_pos[2], 0.2)
        self.time_speed = 3
        count = 0
        enable_fun_mode,FCC_speed,LHC_speed,synchotron_speed = False,False, False, False
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            

            # Handle keyboard input
             
            
            glClearColor(0.0, 0.0, 0.0, 1.0)  # Set the background color to black
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            

            glLoadIdentity()
            
            gluLookAt(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2],
                    self.camera_pos[0] + self.camera_front[0], self.camera_pos[1] + self.camera_front[1], self.camera_pos[2] + self.camera_front[2],
                    self.camera_up[0], self.camera_up[1], self.camera_up[2])
            




            # Draw the grid lines on the cylinder
            glColor3f(0.0, 1.0, 0.0)  # Set the color of the grid lines to green
            glLineWidth(0.5)  # Set the width of the grid lines
            glBegin(GL_LINES)
            for i in range(128):
                angle = i * (2 * np.pi / 128)
                x = cylinder_radius * np.cos(angle)
                y = cylinder_radius * np.sin(angle)
                glVertex3f(x, y, -cylinder_height / 2)  # Start from the negative end of the cylinder
                glVertex3f(x, y, cylinder_height / 2)
            glEnd()

                # Animate protons moving towards each other in 3D space until they collide

            if not self.simulating:
                self.handle_keyboard_input()
                impl.process_inputs()
                imgui.new_frame()
                
                imgui.begin("Particle Accelerator Control")
                
            
                changed, self.relative_particle_speed = self.logarithmic_slider(
                    "Particle Speed",
                    self.relative_particle_speed,
                    15  # Max number of nines
                )
                if changed:
                    LHC_speed, synchotron_speed = False, False
                
                changed, self.time_speed = imgui.slider_int("Time Speed", self.time_speed, 1, 10)


                clicked, LHC_speed = imgui.checkbox("Velocity of LHC", LHC_speed)

                if clicked:
                    synchotron_speed = False
                    # https://public-archive.web.cern.ch/en/lhc/Facts-en.html
                    self.relative_particle_speed = 0.999999991

                

                clicked, synchotron_speed = imgui.checkbox("Velocity of Synchotron", synchotron_speed)
                if clicked:
                    #https://cds.cern.ch/record/1479637/files/1959_E_p29.pdf
                    LHC_speed = False
                    self.relative_particle_speed = 0.9993

                
                    

                

                clicked, enable_fun_mode = imgui.checkbox("Fun Mode", enable_fun_mode)
                
                if clicked:
                    if enable_fun_mode:
                        self.mode = Mode.Fun
                    else:
                        self.mode = Mode.Educational

                if imgui.button("Start Simulation "):
                    self.simulating = True

                
                


                imgui.end()
                if self.simulating:
                    self.positron_pos = [0, 0, np.round((-cylinder_height / 2 + 1.5))]  # Adjust start position
                    self.electron_pos = [0, 0, np.round(cylinder_height / 2 - 1.5)]
                    particles_created = False
                    particles = []
                    
                    self.collided = False
                    positron = Positron(self.positron_pos[0], self.positron_pos[1], self.positron_pos[2], 0.2)
                    electron = Electron(self.electron_pos[0], self.electron_pos[1], self.electron_pos[2], 0.2)
                if not self.collided:
                    positron.draw()
                    electron.draw()
                else:
                    for particle in particles:
                        particle.draw()

                
                imgui.render()
                impl.render(imgui.get_draw_data()) 

            #If the experiment has begun
            if self.simulating:
                if not self.collided:
                    if not self.time_stop:
                        positron.update(self.positron_pos)
                        electron.update(self.electron_pos)
                        self.positron_pos[2] += self.relative_particle_speed * 2/self.time_speed#relative_positron_speed  # Move proton1 along the positive z-axis (towards the center)
                        self.electron_pos[2] -= self.relative_particle_speed * 2/self.time_speed#relative_electron_speed # Move proton2 along the negative z-axis
                        
                        p.resetBasePositionAndOrientation(positron_id, self.positron_pos, [0, 0, 0, 1])
                        p.resetBasePositionAndOrientation(electron_id, self.electron_pos, [0, 0, 0, 1])
                        p.stepSimulation()
                        contacts = p.getContactPoints(positron_id, electron_id)
                        if contacts or self.positron_pos[2]>self.electron_pos[2]:
                            self.collided = True

                        
                    
                    positron.draw()
                    electron.draw()
                    
                else: # If the positron and electron have not collided yetc
                    if not particles_created:
                        positron = None
                        electron = None
                        particles = self.generate_particles()
                        for particle in particles:

                            
                            particle_collision = p.createCollisionShape(p.GEOM_SPHERE, radius=0.05)
                            particle_visual = p.createVisualShape(p.GEOM_SPHERE, radius=particle.radius, rgbaColor=[1, 1, 0, 1])
                            particle_id = p.createMultiBody(baseMass=0.1,
                                                            baseCollisionShapeIndex=particle_collision,
                                                            baseVisualShapeIndex=particle_visual,
                                                            basePosition=particle.pos)
                            particle.updateID(particle_id)
        
                        particles_created = True

                    else:
                        
                        for particle in particles:
                            
                            if not self.time_stop:
                                particle.update()
                                

                                
                                p.resetBasePositionAndOrientation(particle.particleID, particle.pos, [0, 0, 0, 1])
                                p.stepSimulation()

                                particle_pos = particle.pos

                                # Calculate the distance between the particle and the cylinder's center
                                distance = np.sqrt(particle_pos[0]**2 + particle_pos[1]**2)

                                # Check if the particle is outside the cylinder's radius and within the cylinder's height range
                                if distance > cylinder_radius and -cylinder_height/2 <= particle_pos[2] <= cylinder_height/2:
                                    # Collision detected
                                    p.removeBody(particle.particleID)
                                    particles.remove(particle)
                                    self.flash_manager.add_flash(position=particle.pos, size=0.3, brightness=1, duration=2)
                            particle.draw()
                            
                        self.flash_manager.update_and_draw()
                        
                        if len(particles) == 0 and self.collided:
                            self.simulating = False
                            self.positron_pos = [0, 0, np.round((-cylinder_height / 2 + 1.5))]  # Adjust start position
                            self.electron_pos = [0, 0, np.round(cylinder_height / 2 - 1.5)]
                            particles_created = False
                            particles = []
                            particle_ids = []
                            self.collided = False
                            positron = Positron(self.positron_pos[0], self.positron_pos[1], self.positron_pos[2], 0.2)
                            electron = Electron(self.electron_pos[0], self.electron_pos[1], self.electron_pos[2], 0.2)
                        count = count + 1
                self.handle_keyboard_input()
                time.sleep(1./240.)
            glfw.swap_buffers(self.window)
            

        glfw.terminate()


                

        

            


                
                    

                

                

            
            
            
            

        
if __name__ == "__main__":
    sim = Simulation()