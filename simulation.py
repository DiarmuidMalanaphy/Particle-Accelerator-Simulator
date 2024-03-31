import time
import glfw
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np

import pybullet as p
import pybullet_data
from electron import Electron
from gluon import Gluon
from squi import Squi
from kaon import Kaon
from muon import Muon
from photon import Photon
from pion import Pion
from wboson import WBoson
from higgs import HiggsBoson
#from BlackHoleAnimation import BlackHoleAnimation
from positron import Positron
from flash import Flash
from quark import Quark
from tau import Tau
from blackhole import Blackhole
from enum import Enum

import imgui
from imgui.integrations.glfw import GlfwRenderer



#Notes to take

"""


add a noise - Kaboom, 
Make the reaction actually occur in a reaction chamber

Add a background
Add the final few particles

Next addons - Make a summarisation at the end - displaying the amount of kinetic energy, number of particles created and the distribution


Next next step - create an actual simulation of derived ATLAS data and actually understand ROOT


    RULES speed is between 0-1 and represents 0 to c
        - make em able to make it 2 and increase radius to 1 for that case and explode the earth

        


"""

class Mode(Enum):
    Educational  = True
    Fun = False

class Constants(Enum):
    c = 299792458

class Toggle(Enum):
    LHCVelocity = 1
    SynchotronVelocity = 2
    FunMode = 3
    Fill = 4
    LightVelocity = 5
    MuonVelocity = 6
    TauVelocity = 7
    GammaVelocity = 8
    QuarkVelocity = 9
    ZBosonVelocity = 10
    HiggsBosonVelocity = 11
    WPlusVelocity = 12





"""
    3D Simulation of a particle accelerator with different modes for fun or education 

"""

class Simulation():
    def __init__(self,mode = Mode.Educational):
        self.mode = mode
        self.window_size = (1080, 900)
        self.Fkey_pressed = False
        self.start_simulating()
        




    def initialize_glfw(self):
    
        if not glfw.init():
            raise Exception("glfw can not be initialized!")
        
        window = glfw.create_window(self.window_size[0], self.window_size[1], "Proton-Proton Collision Simulation", None, None)

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
            if self.mode.value == Mode.Educational:
                value = 0.999999999999999
                changed, new_slider_pos = imgui.slider_int(label, slider_pos, 0, max_nines, f"{value}c")
                
                
            else:
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
        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS and not self.space_key_pressed:
            self.simulating = not self.simulating
            self.space_key_pressed = True
        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.RELEASE:
            self.space_key_pressed = False

        #Stops time
        if glfw.get_key(self.window, glfw.KEY_T) == glfw.PRESS and not self.t_key_pressed:
            self.time_stop = not self.time_stop
            self.t_key_pressed = True
        #Starts time
        if glfw.get_key(self.window, glfw.KEY_T) == glfw.RELEASE:
            self.t_key_pressed = False




        #Unfills
        if glfw.get_key(self.window, glfw.KEY_F) == glfw.PRESS and not self.Fkey_pressed:
            self.filled = not self.filled
            self.F_key_pressed = True
        if glfw.get_key(self.window, glfw.KEY_F) == glfw.RELEASE:
            self.F_key_pressed = False

    def draw_cylinder(self,cylinder_radius,cylinder_height,segments = 128):
        
        if self.filled:
            thickness = 0.1

            # Draw the outer cylinder body
            glBegin(GL_QUAD_STRIP)
            for i in range(segments + 1):
                angle = i * (2 * np.pi / segments)
                x = cylinder_radius * np.cos(angle)
                y = cylinder_radius * np.sin(angle)
                glVertex3f(x, y, -cylinder_height / 2)
                glVertex3f(x, y, cylinder_height / 2)
            glEnd()

            # Draw the inner cylinder body
            for i in range(segments):
                angle_start = i * (2 * np.pi / segments)
                angle_end = (i + 1) * (2 * np.pi / segments)
                
                x_start_inner = (cylinder_radius - thickness) * np.cos(angle_start)
                y_start_inner = (cylinder_radius - thickness) * np.sin(angle_start)
                x_end_inner = (cylinder_radius - thickness) * np.cos(angle_end)
                y_end_inner = (cylinder_radius - thickness) * np.sin(angle_end)
                
                glBegin(GL_TRIANGLE_STRIP)
                glVertex3f(x_start_inner, y_start_inner, -cylinder_height / 2)
                glVertex3f(x_start_inner, y_start_inner, cylinder_height / 2)
                glVertex3f(x_end_inner, y_end_inner, -cylinder_height / 2)
                glVertex3f(x_end_inner, y_end_inner, cylinder_height / 2)
                glEnd()

            

        else:
            glBegin(GL_LINES)
            for i in range(segments):
                angle = i * (2 * np.pi / segments)
                x = cylinder_radius * np.cos(angle)
                y = cylinder_radius * np.sin(angle)
                glVertex3f(x, y, -cylinder_height / 2)  # Start from the negative end of the cylinder
                glVertex3f(x, y, cylinder_height / 2)
            glEnd()


        

    def rotate_vector(self, vector, angle, axis):
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        return vector * cos_angle + np.cross(axis, vector) * sin_angle + axis * np.dot(axis, vector) * (1 - cos_angle)


    


    def __calculate_total_energy(self):
        #m of electron/positron  is 9.1093837 × 10-31 kilograms - for computational efficiency  9.1*10*31
        def particle_kinetic_energy(v, m):
            """
            Calculate the relativistic kinetic energy given a velocity and mass.
            - v is the velocity of the particle.
            - m is the mass of the particle.
            Returns kinetic energy in eV.
            """
            
            # Calculate the Lorentz factor
            gamma = 1 / np.sqrt(1 - (v**2 / Constants.c.value**2))

            # Calculate the relativistic kinetic energy in joules
            KE_joules = (gamma - 1) * m * Constants.c.value**2

            # Convert kinetic energy to eV
            KE_eV = KE_joules / (1.602176634e-19)
            return KE_eV

        # Assuming positron_speed and electron_speed are defined and are fractions of the speed of light (e.g., 0.99 for 99% of the speed of light)
        m = 9.1e-31  # Mass of electron/positron in kg
        
        #positron_speed = self.relative_particle_speed * c  # relative% speed of light
        #electron_speed = self.relative_particle_speed * c  # relative% speed of light
        unified_speed = self.relative_particle_speed * Constants.c.value # Unify them for efficiency

        # Calculate kinetic energy for both particles
        #positron_kinetic_energy = particle_kinetic_energy(positron_speed, m)
        total_kinetic_energy_eV = 2 * particle_kinetic_energy(unified_speed, m)

        # Sum of kinetic energies in eV
        #total_kinetic_energy_eV = positron_kinetic_energy + electron_kinetic_energy

        # Convert total kinetic energy to GeV
        
        #total_kinetic_energy_GeV = total_kinetic_energy_eV / 10**9
        #total_kinetic_energy_MeV = total_kinetic_energy_eV / 10**6

        #print(f"Total Kinetic Energy: {total_kinetic_energy_MeV} MeV, or {total_kinetic_energy_GeV} GeV")
        
        #https://public-archive.web.cern.ch/en/lhc/Facts-en.html
        rest_energy_eV =  2 * m * (Constants.c.value**2) / (1.602176634e-19)

        total_energy_eV = total_kinetic_energy_eV + rest_energy_eV 

        total_energy_MeV = total_energy_eV / 10**6

        total_energy_GeV = total_energy_eV / 10**9


        

        #print(f"Total Kinetic Energy: {total_energy_MeV} MeV, or {total_energy_GeV} GeV")

        return(total_energy_eV,total_energy_MeV,total_energy_GeV)
        

    def generate_particles(self,mode):

        total_energy_eV, total_energy_MeV, total_energy_GeV = self.__calculate_total_energy()

        if self.mode.value == Mode.Educational.value: # Educational
            return self.generate_educational_particles(total_energy_eV,total_energy_MeV,total_energy_GeV)
        
        else:
            return self.generate_fun_particles(total_energy_eV,total_energy_MeV,total_energy_GeV)


    def generate_fun_particles(self, total_energy_eV, total_energy_MeV, total_energy_GeV):
        particles = []
        remaining_energy_eV = total_energy_eV
        max_particles = 100
        energy_factor = (1-self.relative_particle_speed)*12800
        #print(energy_factor)

        if self.relative_particle_speed == 1.0:
            # Create a black hole instead of particles
            pos = self.calculate_mid_point_positron_electron()
            black_hole = Blackhole(pos[0],pos[1],pos[2] ,1, time_speed = self.time_speed)
            #self.flash_manager.add_flash(position=[0, 0, 0], size=3, brightness=1, duration=120)
            return [black_hole]
         
        

        while remaining_energy_eV > 0 and len(particles) < max_particles:
            if np.random.rand() < 0.7:
                particle_type = np.random.choice(["Photon","Pion", "Muon", "Squi"])
            else:
                particle_type = np.random.choice(["Tau", "Gluon", "Quark", "HiggsBoson", "WBoson"], p=[0.3, 0.3, 0.3, 0.05, 0.05])

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
            
            elif particle_type == "Squi":  # Create Squi particle
                particle = Squi(particle_x, particle_y, particle_z, speed, time_speed=self.time_speed)
                particle_energy = 0.02 * total_energy_eV * energy_factor
            elif particle_type == "HiggsBoson":
                particle = HiggsBoson(particle_x, particle_y, particle_z, speed, time_speed=self.time_speed)
                particle_energy = 0.1 * total_energy_eV * energy_factor
            elif particle_type == "WBoson":
                particle = WBoson(particle_x, particle_y, particle_z, speed, time_speed=self.time_speed)
                particle_energy = 0.08 * total_energy_eV * energy_factor

            else:  # Quark

                quark_masses = {
                'D': 4.9e6,  # Down quark mass in eV/c^2 (using the average of the range)
                'C': 1.270e9,  # Charm quark mass in eV/c^2
                'S': 1.01e8,  # Strange quark mass in eV/c^2
                }

                quark_types = ['D', 'C', 'S']
                quark_weights = [quark_masses[q] for q in quark_types]
                total_weight = sum(quark_weights)
                quark_probs = [w / total_weight for w in quark_weights]

                quark_type = np.random.choice(quark_types, p=quark_probs)
                particle = Quark(particle_x, particle_y, particle_z, speed, quark_type=quark_type, time_speed=self.time_speed)
                particle_energy = 0.07 * total_energy_eV * energy_factor
            remaining_energy_eV -= particle_energy
            
            particles.append(particle)
                

        self.flash_manager.add_flash(
            position= self.calculate_mid_point_positron_electron(),
            size=2,
            brightness=10,
            duration=3
        )

        return particles
        


    def generate_educational_particles(self,total_energy_eV, total_energy_MeV, total_energy_GeV):
        

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
            
            
            self.result_text = f"The resultant energy wasn't enough to create a new particle\nand {choice} photons were emitted."
            directions = generate_directions(choice)

            

            for direction in directions:
                speed = 1
                particle_x = direction[0] * speed
                particle_y = direction[1] * speed
                particle_z = direction[2] * speed
                particle = Photon(particle_x,particle_y,particle_z,1,time_speed = self.time_speed)
                particles.append(particle)
                



        elif total_energy_GeV<3.4 and total_energy_MeV>210:#Muons

            self.result_text = "The rest and kinetic energy of the particle was enough to\nproduce two Muons"
            directions = generate_directions(2)# <- for the two resulting muons 

            muon_m = 1.883531627e-28
            rest_energy_eV_muon =  muon_m * (Constants.c.value**2) / (1.602176634e-19)
            kinetic_energy_per_muon = (total_energy_eV - 2 * rest_energy_eV_muon) / 2

            
            v = Constants.c.value * np.sqrt(1 - (1 / ((kinetic_energy_per_muon / (rest_energy_eV_muon)) + 1))**2)
            speed = v/Constants.c.value
            self.flash_manager.add_flash(position = self.calculate_mid_point_positron_electron(), size=0.5, brightness=10*speed, duration=2)
            for direction in directions:
                particle_x = direction[0] * speed
                particle_y = direction[1] * speed
                particle_z = direction[2] * speed
                particle = Muon(particle_x,particle_y,particle_z,speed,time_speed = self.time_speed)
                particles.append(particle)
            


        


        elif total_energy_GeV>=3.4 and total_energy_GeV<9.4: #Tau
            self.result_text = "The rest and kinetic energy of the particle resulted in\ntwo Tau particles"
            directions = generate_directions(2)
            
            tau_m = 3.167e-27
            rest_energy_eV_tau =  tau_m * (Constants.c.value**2) / (1.602176634e-19)
            kinetic_energy_per_tau = (total_energy_eV - 2 * rest_energy_eV_tau) / 2
            v = Constants.c.value * np.sqrt(1 - (1 / ((kinetic_energy_per_tau / (rest_energy_eV_tau)) + 1))**2)
            speed = v/Constants.c.value
            self.flash_manager.add_flash(position=self.calculate_mid_point_positron_electron(), size=0.5, brightness=10*speed, duration=2)
            for direction in directions:
                
                particle_x = direction[0] * speed
                particle_y = direction[1] * speed
                particle_z = direction[2] * speed
                particle = Tau(particle_x,particle_y,particle_z,speed,time_speed = self.time_speed)
                particles.append(particle)

        elif total_energy_GeV>=9.4 and total_energy_GeV<30: #gamma gluon gluon
            self.result_text = "The rest and kinetic energy of the particle produced\na quantum gamma particle, decaying into three\nhigh energy gluons"
            directions = generate_directions(3)
            speed = 1.3 # C -> the gluons are incredibly high powered (I modified it to make it cooler and make it slightly more explosive and fast)
            self.flash_manager.add_flash(position=[(self.positron_pos[0] + self.electron_pos[0]) / 2, (self.positron_pos[1] + self.electron_pos[1]) / 2, (self.positron_pos[2] + self.electron_pos[2]) / 2], size=2, brightness=10*speed, duration=3)
            for direction in directions:
                
                particle_x = direction[0] * speed
                particle_y = direction[1] * speed
                particle_z = direction[2] * speed
                particle = Gluon(particle_x,particle_y,particle_z,speed,time_speed = self.time_speed)
                particles.append(particle)
            

        elif total_energy_GeV >= 30 and total_energy_GeV < 80:  # quark quark gluon
            directions = generate_directions(3)
            particle_x = directions[2][0] * 1
            particle_y = directions[2][1] * 1
            particle_z = directions[2][2] * 1
            particle = Gluon(particle_x, particle_y, particle_z, 1, time_speed=self.time_speed)
            particles.append(particle)

            quark_masses = {
                'D': 4.9e6,  # Down quark mass in eV/c^2 (using the average of the range)
                'C': 1.270e9,  # Charm quark mass in eV/c^2
                'S': 1.01e8,  # Strange quark mass in eV/c^2
                # 'T': 1.72e11  # Top quark mass in eV/c^2  WE EXCLUDE THIS ONE BECAUSE THE MASS IS TOO HIGH
            }

            quark_names = {
                'D': "Down",
                'C': "Charm",
                'S': "Strange",
            }

            quark_types = ['D', 'C', 'S']

            chosen_quarks = np.random.choice(quark_types, size=2, replace=False)

            if chosen_quarks[0] != chosen_quarks[1]:
                self.result_text = f"The rest and kinetic energy of the particle was enough\nto produce a gluon and two Quarks, {quark_names[chosen_quarks[0]]} and {quark_names[chosen_quarks[1]]}"
            else:
                self.result_text = f"The rest and kinetic energy of the particle was enough\nto produce two {quark_names[chosen_quarks[0]]} Quarks and a gluon"

            total_quarks_energy_eV = total_energy_eV * 0.9  # Allocate 90% of the total energy to the quarks
            gluon_energy_eV = total_energy_eV - total_quarks_energy_eV  # Allocate the remaining energy to the gluon

            for i, quark_type in enumerate(chosen_quarks):
                quark_mass = quark_masses[quark_type]
                rest_energy_eV_quark = quark_mass

                quark_total_energy_eV = total_quarks_energy_eV / 2

                kinetic_energy_per_quark = quark_total_energy_eV - rest_energy_eV_quark

                v = Constants.c.value * np.sqrt(1 - (1 / ((kinetic_energy_per_quark / (rest_energy_eV_quark)) + 1))**2)
                speed = v / Constants.c.value

                particle_x = directions[i][0] * speed
                particle_y = directions[i][1] * speed
                particle_z = directions[i][2] * speed

                particle = Quark(particle_x, particle_y, particle_z, speed, quark_type=quark_type, time_speed=self.time_speed)
                particles.append(particle)

            self.flash_manager.add_flash(
                position=self.calculate_mid_point_positron_electron(),
                size=0.5,
                brightness=5,
                duration=2
            )
    

        #http://www.quantumdiaries.org/2010/05/10/the-z-boson-and-resonances/
        elif total_energy_GeV>=80 and total_energy_GeV<124: #Z Boson -> produces two muons

            directions = generate_directions(2)# <- for the two resulting muons 
            self.result_text = f"The rest and kinetic energy of the particle was enough\nto produce the Z Boson however, due to its quantum\nnature it decayed instantly into 2 Muons"
            muon_m = 1.883531627e-28
            rest_energy_eV_muon =  muon_m * (Constants.c.value**2) / (1.602176634e-19)
            kinetic_energy_per_muon = (total_energy_eV - 2 * rest_energy_eV_muon) / 2

            
            v = Constants.c.value * np.sqrt(1 - (1 / ((kinetic_energy_per_muon / (rest_energy_eV_muon)) + 1))**2)
            speed = v/Constants.c.value
            self.flash_manager.add_flash(position=self.calculate_mid_point_positron_electron(), size=0.5, brightness=10*speed, duration=2)
            for direction in directions:
                particle_x = direction[0] * speed
                particle_y = direction[1] * speed
                particle_z = direction[2] * speed
                particle = Muon(particle_x,particle_y,particle_z,speed,time_speed = self.time_speed)
                particles.append(particle)
            pass

        elif total_energy_GeV>=124 and total_energy_GeV< 160: # Higgs Boson
            
            

            
            choice = np.random.choice([2, 3, 4, 5, 6], p=[0.4, 0.3, 0.15, 0.1,0.05])
            self.result_text = f"The rest and kinetic energy of the particle was enough\nto produce the Higgs Boson however, due to its quantum\nnature it decayed instantly into {choice} photons "
            directions = generate_directions(choice)
            for direction in directions:
                speed = 1
                particle_x = direction[0] * speed
                particle_y = direction[1] * speed
                particle_z = direction[2] * speed
                particle = Photon(particle_x,particle_y,particle_z,1,time_speed = self.time_speed)
                particles.append(particle)
                
            
            self.flash_manager.add_flash(position=self.calculate_mid_point_positron_electron(), size=0.5, brightness=10*speed, duration=3)

        elif total_energy_GeV>=160 and total_energy_GeV< 200: #W+ Boson
            directions = generate_directions(choice)
            wmass = 1e-25
            rest_energy_eV_w =  wmass * (Constants.c.value**2) / (1.602176634e-19)

            kinetic_energy_per_muon = (total_energy_eV - 2 * rest_energy_eV_muon) / 2

            
            v = Constants.c.value * np.sqrt(1 - (1 / ((kinetic_energy_per_muon / (rest_energy_eV_muon)) + 1))**2)
            speed = v/Constants.c.value
            self.flash_manager.add_flash(position = self.calculate_mid_point_positron_electron(), size=0.5, brightness=10*speed, duration=2)
            for direction in directions:
                particle_x = direction[0] * speed
                particle_y = direction[1] * speed
                particle_z = direction[2] * speed
                particle = WBoson(particle_x,particle_y,particle_z,speed,time_speed = self.time_speed)
                particles.append(particle)
            pass

        else:#Who knows

            self.flash_manager.add_flash(position=self.calculate_mid_point_positron_electron(), size=10, brightness=10, duration=4)
            self.result_text = "The rest and kinetic energy of the particle is\nmore than the standard model predicts."
            
            return[]
            
        return(particles)
    
    
    def calculate_mid_point_positron_electron(self):
        position=[(self.positron_pos[0] + self.electron_pos[0]) / 2,
                    (self.positron_pos[1] + self.electron_pos[1]) / 2,
                    (self.positron_pos[2] + self.electron_pos[2]) / 2]
        return(position)
        

    def handle_intro_keys(self):
        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS:
            self.intro_page = False
            self.space_key_pressed = True

    def reset_checkboxes(self,ticked = None):
        
        
        
        self.LHC_velocity_toggle, self.synchotron_velocity_toggle,self.infinite_energy_toggle, self.muon_velocity_toggle, self.muon_velocity_toggle, self.tau_velocity_toggle, self.gamma_gluon_toggle, self.quark_toggle, self.ZBoson_toggle, self.higgs_toggle, self.WPlus_toggle = False,False,False,False,False,False,False,False,False,False,False
        
        
        if ticked is None:
            return
        if ticked.value == Toggle.LHCVelocity.value:
            self.LHC_velocity_toggle = True

        if ticked.value == Toggle.SynchotronVelocity.value:
            self.synchotron_velocity_toggle = True
        
        if ticked.value == Toggle.MuonVelocity.value:
            self.muon_velocity_toggle = True

        if ticked.value == Toggle.TauVelocity.value:
            self.tau_velocity_toggle = True
        
        if ticked.value == Toggle.GammaVelocity.value:
            self.gamma_gluon_toggle = True
        
        if ticked.value == Toggle.QuarkVelocity.value:
            self.quark_toggle = True

        if ticked.value == Toggle.ZBosonVelocity.value:
            self.ZBoson_toggle = True

        if ticked.value == Toggle.HiggsBosonVelocity.value:
            self.higgs_toggle = True

        if ticked.value == Toggle.WPlusVelocity.value:
            self.WPlus_toggle = True

        if ticked.value == Toggle.LightVelocity.value:
            self.infinite_energy_toggle = True


        



    def introduction_page(self,img_impl):
        self.intro_page = True


        while self.intro_page:
            
            glfw.poll_events()
            img_impl.process_inputs()
            imgui.new_frame()

            # Set the next window's size and position before creating it
            imgui.set_next_window_position(int(1080 / 2 - 250), int(900 / 2 - 150))
            imgui.set_next_window_size(500, 300)

            # Now when you begin the window, it will use the size and position set above
            _, self.intro_page = imgui.begin("Particle Accelerator Simulation", self.intro_page, flags=imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_MOVE)

            
            
            imgui.spacing()
            imgui.text("Welcome to the Particle Accelerator Simulation!")
            imgui.spacing()
            imgui.text("In this simulation, you can explore the collision of particles")
            imgui.text("and observe the resulting particle interactions.")
            imgui.spacing()

            imgui.text("For simplicity we will be focusing on the interaction between ")
            imgui.text("electrons and positrons at near light speed.")

            imgui.spacing()
            imgui.text("Press the 'Start Simulation' button or space to begin.")
            imgui.spacing()

            # Use dummy items and set_item_width to center the button
            imgui.dummy(1, 20)  # Add some space before the button (vertical padding)
            imgui.columns(3, "button_col", False)  # Create 3 columns; the button will be in the middle
            imgui.set_column_width(0, 150)  # Adjust the width of the left column
            imgui.next_column()  # Move to the middle column
            imgui.set_column_width(1, 200)  # Adjust the middle column where the button will be

            # Set the button size
            imgui.push_button_repeat(True)
            if imgui.button("Start Simulation", width=200, height=40):  # Adjust width and height as needed
                self.intro_page = False
            imgui.pop_button_repeat()

            imgui.columns(1)  # Revert back to 1 column to normalize layout
            imgui.end()

            self.handle_intro_keys()
            imgui.render()
            img_impl.render(imgui.get_draw_data())
            glfw.swap_buffers(self.window)


    


    def generate_stars(self, num_stars):
        stars = []
        for _ in range(num_stars):
            x = np.random.uniform(-1.0, 1.0)
            y = np.random.uniform(-1.0, 1.0)
            z = np.random.uniform(-1.0, 1.0)
            stars.append((x, y, z))
        return stars


    def draw_stars(self):
        glPointSize(2.0)  # Set the size of the star points
        glColor3f(1.0, 1.0, 1.0)  # Set the color of the stars to white
        glBegin(GL_POINTS)
        for star in self.stars:
            glVertex3f(star[0]*100, star[1]*100, star[2] * 100)  # Scale down the z-coordinate
        glEnd()
   

    def start_simulating(self):
        self.window = self.initialize_glfw()
        #self.black_hole_animation = BlackHoleAnimation("blackhole.glb")
        
        imgui.create_context()
        impl = GlfwRenderer(self.window)

        self.introduction_page(impl)
        

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
        


        

        self.relative_particle_speed = 0.9

        particles = []
        
        self.collided = False
        particles_created = False
        self.simulating = False
        self.time_stop = False
        enable_fun_mode = False
        self.filled = False
        
        self.reset_checkboxes()
        positron = Positron(self.positron_pos[0], self.positron_pos[1], self.positron_pos[2], 0.2)
        electron = Electron(self.electron_pos[0], self.electron_pos[1], self.electron_pos[2], 0.2)
        self.time_speed = 5
        black_hole = False
        collision_results_window = False
        self.stars = self.generate_stars(1000)
        
        while not glfw.window_should_close(self.window):
            glfw.poll_events()
            

            # Handle keyboard input
             
            
            glClearColor(0, 0, 0, 1.0)  # Set the background color to black
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            

            glLoadIdentity()
            
            gluLookAt(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2],
                    self.camera_pos[0] + self.camera_front[0], self.camera_pos[1] + self.camera_front[1], self.camera_pos[2] + self.camera_front[2],
                    self.camera_up[0], self.camera_up[1], self.camera_up[2])
            

            self.draw_stars()


            # # Draw the grid lines on the cylinder
            glColor3f(0.75, 0.75, 0.75)  # Set the color of the grid lines to green
            glLineWidth(0.5)  # Set the width of the grid lines

            
            self.draw_cylinder(cylinder_radius,cylinder_height)
            
            
            

            
                # Animate protons moving towards each other in 3D space until they collide
            imgui.new_frame()
            if not self.simulating:
                self.handle_keyboard_input()
                impl.process_inputs()
                
                window_width, window_height = self.window_size[0]/2.5, self.window_size[1]/4
                
                window_x = (self.window_size[0]) * 0.3  // 5
                window_y = (glfw.get_window_size(self.window)[1] - window_height) // 4
                imgui.set_next_window_position(window_x, window_y)
                imgui.set_next_window_size(window_width, window_height)

                imgui.begin("Particle Accelerator Control", flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE)
                
            
                ##########SLIDERS###########

                ### DEFINING PARTICLE VELOCITY
                changed, self.relative_particle_speed = self.logarithmic_slider(
                    "Particle Speed",
                    self.relative_particle_speed,
                    15  # Max number of nines
                )
                if changed:
                    self.reset_checkboxes()

                ### DEFINING THE TIME SPEED (HOW SLOW/FAST THE SIMULATION GOES)
                
                formatted_time_speed = f"Time Modifier {np.round(((self.time_speed/10)-0.5)*100)}%"
                changed, self.time_speed = imgui.slider_int(formatted_time_speed, self.time_speed, 1, 10)
                
                
                
                
                imgui.columns(2, 'checkboxes', False)


                ##########TICKBOXES##################

                clicked, self.LHC_velocity_toggle = imgui.checkbox("Velocity of LHC", self.LHC_velocity_toggle)
                if clicked:
                    if self.LHC_velocity_toggle:
                        self.reset_checkboxes(ticked = Toggle.LHCVelocity)
                        # https://public-archive.web.cern.ch/en/lhc/Facts-en.html
                        self.relative_particle_speed = 0.999999991
                    else:
                        self.relative_particle_speed = 0.9

                

                clicked, self.synchotron_velocity_toggle = imgui.checkbox("Velocity of Synchotron", self.synchotron_velocity_toggle)
                if clicked:
                    if self.synchotron_velocity_toggle:
                        self.reset_checkboxes(ticked = Toggle.SynchotronVelocity)
                        #https://cds.cern.ch/record/1479637/files/1959_E_p29.pdf
                        
                        self.relative_particle_speed = 0.9993
                    else:
                        self.relative_particle_speed = 0.9


                clicked, enable_fun_mode = imgui.checkbox("Fun Mode", enable_fun_mode)
                if clicked:
                    if enable_fun_mode:
                        self.mode = Mode.Fun
                        #self.relative_particle_speed = 0.9
                    else:
                        self.mode = Mode.Educational
                        
                        #self.relative_particle_speed = 0.9

                ###SPEED OF LIGHT TOGGLEBOX <- behaves strangely because I've only allowed it in fun mode.
                
                clicked, self.infinite_energy_toggle = imgui.checkbox("Speed of Light", self.infinite_energy_toggle)
                if clicked:
                    if self.infinite_energy_toggle:
                        self.reset_checkboxes(ticked = Toggle.LightVelocity)
                        self.relative_particle_speed = 1.0
                    else:
                        self.relative_particle_speed = 0.9

                ### Filled in cylinder togglebox
                clicked, self.filled = imgui.checkbox("Fill in Cylinder", self.filled)

                ### MUON VELOCITY TOGGLEBOX
                
                clicked, self.muon_velocity_toggle = imgui.checkbox("Muon Velocity", self.muon_velocity_toggle)

                if clicked:
                    if self.muon_velocity_toggle:
                        self.reset_checkboxes(ticked = Toggle.MuonVelocity)
                        self.relative_particle_speed = 0.9999999
                    else:
                        self.relative_particle_speed = 0.9
                        

                
                imgui.next_column()

                ### TAU VELOCITY TOGGLEBOX
                
                clicked, self.tau_velocity_toggle = imgui.checkbox("Tau Velocity", self.tau_velocity_toggle)
                
                if clicked:
                    if self.tau_velocity_toggle:
                        self.reset_checkboxes(ticked = Toggle.TauVelocity)
                        self.relative_particle_speed = 0.99999997
                    else:
                        self.relative_particle_speed = 0.9
                        
                
                clicked, self.gamma_gluon_toggle = imgui.checkbox("Gamma-Gluon-Gluon Velocity", self.gamma_gluon_toggle)

                if clicked:
                    if self.gamma_gluon_toggle:
                        self.reset_checkboxes(ticked = Toggle.GammaVelocity)
                        self.relative_particle_speed = 0.999999997
                    else:
                        self.relative_particle_speed = 0.9
                
                clicked, self.quark_toggle = imgui.checkbox("Quark Velocity", self.quark_toggle)

                if clicked:
                    if self.quark_toggle:
                        self.reset_checkboxes(ticked = Toggle.QuarkVelocity)
                        self.relative_particle_speed = 0.9999999997
                    else:
                        self.relative_particle_speed = 0.9
                
                clicked, self.ZBoson_toggle = imgui.checkbox("Z-Boson Velocity", self.ZBoson_toggle)

                if clicked:
                    if self.ZBoson_toggle:
                        self.reset_checkboxes(ticked = Toggle.ZBosonVelocity)
                        self.relative_particle_speed = 0.99999999994
                    else:
                        self.relative_particle_speed = 0.9
                
                
                clicked, self.higgs_toggle = imgui.checkbox("Higgs Boson Velocity", self.higgs_toggle)

                if clicked:
                    if self.higgs_toggle:
                        self.reset_checkboxes(ticked = Toggle.HiggsBosonVelocity)
                        self.relative_particle_speed = 0.99999999997
                    else:
                        self.relative_particle_speed = 0.9

                clicked, self.WPlus_toggle = imgui.checkbox("WPlus Velocity", self.WPlus_toggle)
                if clicked:
                    if self.WPlus_toggle:
                        self.reset_checkboxes(ticked = Toggle.WPlusVelocity)
                        self.relative_particle_speed = 0.999999999992
                    else:
                        self.relative_particle_speed = 0.9
                
                imgui.columns(1)

                
                    
                
                

                


                if imgui.button("Start Simulation "):
                    self.simulating = True

                
                


                imgui.end()
                if self.simulating:
                    self.positron_pos = [0, 0, np.round((-cylinder_height / 2 + 1.5))]  # Adjust start position
                    self.electron_pos = [0, 0, np.round(cylinder_height / 2 - 1.5)]
                    particles_created = False
                    particles = []
                    collision_results_window = False

                    
                    self.collided = False
                    positron = Positron(self.positron_pos[0], self.positron_pos[1], self.positron_pos[2], 0.2)
                    electron = Electron(self.electron_pos[0], self.electron_pos[1], self.electron_pos[2], 0.2)
                if not self.collided:
                    positron.draw()
                    electron.draw()
                else:
                    for particle in particles:
                        particle.draw()

                
                
            #If the experiment has begun
            if self.simulating:
                if not self.collided:
                    if not self.time_stop:
                        positron.update(self.positron_pos)
                        electron.update(self.electron_pos)
                        self.positron_pos[2] += self.relative_particle_speed * 2/self.time_speed#relative_positron_speed  # Move proton1 along the positive z-axis (towards the center)
                        self.electron_pos[2] -= self.relative_particle_speed * 2/self.time_speed#relative_electron_speed # Move proton2 along the negative z-axis
                        
                        if self.positron_pos[2]>self.electron_pos[2]:
                            self.collided = True

                        
                    
                    positron.draw()
                    electron.draw()
                    
                else: # If the positron and electron have not collided yetc
                    if not particles_created:
                        positron = None
                        electron = None
                        particles = self.generate_particles()

                        if len(particles)>0 and isinstance(particles[0], Blackhole):
                            black_hole = True

        
                        particles_created = True

                    else:
                        
                        for particle in particles:
                            
                            if not self.time_stop:
                                particle.update()
                                
                                

                                
                                #p.resetBasePositionAndOrientation(particle.particleID, particle.pos, [0, 0, 0, 1])
                                #p.stepSimulation()

                                particle_pos = particle.pos

                                # Calculate the distance between the particle and the cylinder's center
                                distance = np.sqrt(particle_pos[0]**2 + particle_pos[1]**2)

                                # Check if the particle is outside the cylinder's radius and within the cylinder's height range
                                if (distance > cylinder_radius and -cylinder_height/2 <= particle_pos[2] <= cylinder_height/2):
                                    # Collision detected
                                    #p.removeBody(particle.particleID)
                                    particles.remove(particle)
                                    self.flash_manager.add_flash(position=particle.pos, size=0.3, brightness=1, duration=2)
                                
                                elif (particle_pos[2]>np.round(cylinder_height / 2 - 1.5) or particle_pos[2]<np.round(-cylinder_height / 2 + 1.5)):
                                    #p.removeBody(particle.particleID)
                                    particles.remove(particle)
                            particle.draw()
                            
                        self.flash_manager.update_and_draw()



                        if black_hole and particle.check_collision(self.camera_pos):
                            #print("Camera consumed by the black hole!")
                            particles = []
                            black_hole = False
                            #black_hole.play_animation(self.window)


                        
                        if len(particles) == 0 and self.collided: # Automatically reset the chamber
                            if self.mode.value == Mode.Educational.value:
                                total_energy_eV, total_energy_MeV, total_energy_GeV = self.__calculate_total_energy()
                                
                                if total_energy_GeV < 1:
                                    energy_text = f"{total_energy_MeV:.2f} MeV"
                                else:
                                    energy_text = f"{total_energy_GeV:.2f} GeV"
                                
                                collision_results = {
                                    "energy_text": energy_text,
                                    "result_text": self.result_text
                                }
                                collision_results_window = True
                            self.simulating = False
                            self.positron_pos = [0, 0, np.round((-cylinder_height / 2 + 1.5))]  # Adjust start position
                            self.electron_pos = [0, 0, np.round(cylinder_height / 2 - 1.5)]
                            particles_created = False
                            particles = []
                            particle_ids = []
                            self.collided = False
                            positron = Positron(self.positron_pos[0], self.positron_pos[1], self.positron_pos[2], 0.2)
                            electron = Electron(self.electron_pos[0], self.electron_pos[1], self.electron_pos[2], 0.2)
                            
                       
                self.handle_keyboard_input()
                time.sleep(1./240.)
            
            if collision_results_window:
                

                # Set the initial position and size of the collision results window
                window_width, window_height = self.window_size[0]/2.5, self.window_size[1]/4
                window_x = (self.window_size[0] ) * 2.5  // 5
                window_y = (glfw.get_window_size(self.window)[1] - window_height) // 4
                imgui.set_next_window_position(window_x, window_y)
                imgui.set_next_window_size(window_width, window_height)

                imgui.begin("Collision Results", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE)

                # Add padding and spacing for better visual layout
                imgui.push_style_var(imgui.STYLE_FRAME_PADDING, (10, 10))
                imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (10, 10))

                # Display the collision results in a structured format
                imgui.text("Collision Results")
                imgui.separator()

                # Display the total kinetic energy with a colored background
                imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0.2, 0.2, 0.2, 1.0)  # Set background color to dark gray
                energy_text_formatted = f"Total Kinetic Energy: {collision_results['energy_text']}"
                imgui.text_colored(energy_text_formatted, 1.0, 1.0, 1.0 )  # Set text color to white
                imgui.pop_style_color()

                imgui.spacing()

                # Display the resultant particles with a colored background
                imgui.text("Resultant Particles:")
                imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, 0.3, 0.3, 0.3, 1.0)  # Set background color to a slightly lighter gray
                imgui.text_colored(collision_results['result_text'], 1.0, 0.0, 1.0 )  # Set text color to yellow
                imgui.pop_style_color()

                imgui.spacing()

                if imgui.button("Close"):
                    collision_results_window = False

                imgui.pop_style_var(2)  # Pop the style variables for padding and spacing

                imgui.end()
            imgui.render()
            impl.render(imgui.get_draw_data())
            glfw.swap_buffers(self.window)
            

        glfw.terminate()


                

        

            


                
                    

                

                

            
            
            
            

        
if __name__ == "__main__":
    sim = Simulation()