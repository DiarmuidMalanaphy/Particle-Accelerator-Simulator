import time
from collision_results_page import CollisionResultsPage
from control_instructions import ControlInstructions
from draw_tools import DrawTools
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from introduction_page import IntroductionPage
import numpy as np
from constants import Toggle
import particle_control_panel
from Particles.electron import Electron
from Particles.particle import Particle
from constants import Toggle, Mode
from Particles.particlegenerator import ParticleGenerator
from Particles.positron import Positron
from flash import Flash

from Particles.blackhole import Blackhole


import imgui
from imgui.integrations.glfw import GlfwRenderer
from utility import UtilityFunctions





"""
    3D Simulation of a particle accelerator with different modes for fun or Education


    The simulation is quite simplistic and mostly covers the interaction of an electron and positron colliding at relativistic speeds.

    The educational mode describes the kinetic energy of the input particles and the resultant particle from each speed.

    The fun mode provides a range of particles with interesting colours to observe. 

"""


STARTING_EYE_POSITION = (3.0, 3.0, 25.0)
STARTING_CENTRE_POSITION = (0.0, 0.0, 0.0)
STARTING_UP_DIRECTION = (0.0, 1.0, 0.0)

CYLINDER_RADIUS = 5
CYLINDER_HEIGHT = 100

POSITRON_STARTING_POSITION = [0, 0, np.round((-CYLINDER_HEIGHT / 2 + 1.5))]  # Adjust start position
ELECTRON_STARTING_POSITION = [0, 0, np.round(CYLINDER_HEIGHT / 2 - 1.5)] 

class Simulation():

    """
    The Simulation class represents a 3D simulation of a particle accelerator with different modes for educational or experimental purposes.

    The simulation focuses on the interaction of an electron and positron colliding at relativistic speeds. It provides an educational mode that describes the kinetic energy of the input particles and the resultant particles at different speeds. It also offers an experimental mode that allows for a range of particles with interesting colors and behaviors.

    The simulation is built using OpenGL for 3D rendering and ImGui for the user interface. It utilizes the GLFW library for window management and input handling.


    The Simulation class aims to provide an interactive and educational experience for exploring particle collisions and their resultant particles at different energy levels. It combines realistic physics simulations with visually appealing graphics to engage users and facilitate learning about particle physics concepts.


    On an implementation level, this class just handles the collisions between the particles and the rendering
    particle drawing occurs in the respective particle classes and the physics for deciding what particle to display is handled within the
    particle generator.     
    """
   
    def __init__(self):
        
        
        self.window_size = (1080, 900)
        self.window = self.initialize_glfw()
        
        ## Control panel variables.

        self.control_panel = self.create_control_panel()
        self.get_control_panel_info()
       
        self.space_key_pressed = False
        self.F_key_pressed = False
        self.R_key_pressed = False
        self.E_key_pressed = False
        self.H_key_pressed = False
        self.instructions_shown = True
        self.utility = UtilityFunctions()
        self.particle_generator = ParticleGenerator()
        self.start_simulating()
        
    def initialize_glfw(self):
    
        if not glfw.init():
            raise Exception("glfw can not be initialized!")
        
        window = glfw.create_window(self.window_size[0], self.window_size[1], "Electron-Postriton Collision Simulation", None, None)

        if not window:
            glfw.terminate()
            raise Exception("glfw window can not be created!")

        glfw.set_window_pos(window, 300, 150)
        glfw.make_context_current(window)

        return window

    def create_control_panel(self):
        control_panel = particle_control_panel.ParticleControlPanel(self.window, self.window_size)
        return control_panel


    def reset_control_panel(self):
        self.control_panel = particle_control_panel.ParticleControlPanel(self.window, self.window_size)
        return  

    def get_control_panel_info(self):
        self.relative_particle_speed, self.filled, self.time_speed, self.mode, self.simulating = self.control_panel.get_information()
        print(self.relative_particle_speed)
        return 


    
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
            print("Pi")
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

        
        if glfw.get_key(self.window, glfw.KEY_R) == glfw.PRESS and not self.R_key_pressed:
            self.eye_x, self.eye_y, self.eye_z = STARTING_EYE_POSITION # Position the camera slightly off-center and tilted
            self.center_x, self.center_y, self.center_z = STARTING_CENTRE_POSITION  # Look towards the center of the cylinder
            self.up_x, self.up_y, self.up_z = STARTING_UP_DIRECTION
            self.set_up_camera()
            self.R_key_pressed = True
        if glfw.get_key(self.window, glfw.KEY_R) == glfw.RELEASE:
            self.R_key_pressed = False

        if glfw.get_key(self.window, glfw.KEY_E) == glfw.PRESS and not self.E_key_pressed:
            self.instructions_shown = not self.instructions_shown
            self.E_key_pressed = True
        if glfw.get_key(self.window, glfw.KEY_E) == glfw.RELEASE:
            self.E_key_pressed = False


        
        if glfw.get_key(self.window, glfw.KEY_H) == glfw.PRESS and not self.H_key_pressed:
            self.cylinder_shown = not self.cylinder_shown
            self.H_key_pressed = True

        if glfw.get_key(self.window, glfw.KEY_H) == glfw.RELEASE:
            self.H_key_pressed = False
        

        #Unfills
        if glfw.get_key(self.window, glfw.KEY_F) == glfw.PRESS and not self.F_key_pressed:
            self.filled = not self.filled
            self.F_key_pressed = True
        if glfw.get_key(self.window, glfw.KEY_F) == glfw.RELEASE:
            self.F_key_pressed = False

    def rotate_vector(self, vector, angle, axis):
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        return vector * cos_angle + np.cross(axis, vector) * sin_angle + axis * np.dot(axis, vector) * (1 - cos_angle)

    
    

    
    def set_up_camera(self):
        self.camera_pos = np.array([self.eye_x, self.eye_y, self.eye_z], dtype=np.float32)
        self.camera_front = np.array([self.center_x - self.eye_x, self.center_y - self.eye_y, self.center_z - self.eye_z], dtype=np.float32)
        self.camera_front = self.camera_front / np.linalg.norm(self.camera_front)
        self.camera_up = np.array([self.up_x, self.up_y, self.up_z], dtype=np.float32)
        self.camera_position_speed = 0.3
        self.camera_angle_speed = 1
        
    def restart_simulation(self):
        
        
        collided = False
        time_stop = False

        starting_particles = ParticleGenerator.build_particles_array(2, particle_dtype = Particle.get_np_type(100 * self.time_speed))
         
         
        starting_particles[0] = Positron(POSITRON_STARTING_POSITION, np.asarray([0, 0, 10])).to_np() 
        starting_particles[1] = Electron(ELECTRON_STARTING_POSITION, np.asarray([0, 0, -10])).to_np()

        collision_results_window = False
        particles_created = False
        

        return starting_particles, collision_results_window, particles_created, collided, time_stop

       
    def start_simulating(self):

        ###   THIS WHOLE SECTION IS JUST INITIALISING THE SIMULATION
        
        #self.black_hole_animation = BlackHoleAnimation("blackhole.glb")
        
        imgui.create_context()
        impl = GlfwRenderer(self.window)

        intro_page = IntroductionPage()
        intro_page.display(impl, self.window) 

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
        self.eye_x, self.eye_y, self.eye_z = STARTING_EYE_POSITION # Position the camera slightly off-center and tilted
        
        self.center_x, self.center_y, self.center_z = STARTING_CENTRE_POSITION  # Look towards the center of the cylinder
        self.up_x, self.up_y, self.up_z = STARTING_UP_DIRECTION # Set the up direction
        #gluLookAt(self.eye_x, self.eye_y, self.eye_z, self.center_x, self.center_y, self.center_z, self.up_x, self.up_y, self.up_z)
        self.set_up_camera()

        


        self.flash_manager = Flash()
        #reset_control_panel_stuff
        self.relative_particle_speed = 0.9
        self.simulating = False
        self.enable_fun_mode = False
        self.filled = False
        self.time_speed = 6
        self.get_control_panel_info()

        #Defined During Simulation
        particles, collision_results_window, particles_created, collided, time_stop = self.restart_simulation()
        collision_results = None

        particles_created = False
        show_cylinder = True
        
        time_stop = False
        self.control_panel.reset_checkboxes()

        black_hole = False
        collision_results_window = False
        
        generated_stars = DrawTools.generate_stars(1000) 


        ##### RUNNING THE SIMULATION
        
        while not glfw.window_should_close(self.window):
            
            imgui.new_frame()
            glfw.poll_events()
            if self.instructions_shown:
                ControlInstructions.draw(self.window, self.window_size)
             

            
             
            
            glClearColor(0, 0, 0, 1.0)  # Set the background color to black
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            

            glLoadIdentity()
            
            gluLookAt(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2],
                    self.camera_pos[0] + self.camera_front[0], self.camera_pos[1] + self.camera_front[1], self.camera_pos[2] + self.camera_front[2],
                    self.camera_up[0], self.camera_up[1], self.camera_up[2])
            

            #Draw the background
            DrawTools.draw_stars(generated_stars)
            
            if show_cylinder:
                DrawTools.draw_cylinder(CYLINDER_RADIUS, CYLINDER_HEIGHT, filled = self.filled)
            
            
            

            if not self.simulating:
                
                impl.process_inputs()
               
                self.control_panel.draw_control_panel() 
                self.get_control_panel_info()
                
                self.handle_keyboard_input()
                
                if self.simulating:
                    #Essentially, if the state of simulating changes after validating keyboard inputs then we know that the simulation has been started
                    particles, collision_results_window, particles_created, collided, time_stop = self.restart_simulation()


                #Draw the stationary positrons and electrons, if you delete this section it just resets them.  
                Particle.draw_particles(particles) 
                
                
            #If the experiment has begun 
            if self.simulating:

                #Collided defines when the electron and the positron have collided .
                if not collided:
                    
                    # This is to allow for timestops <- essentially just draw and don't update.
                    if not time_stop:
                        Particle.update_particles(particles) ####################WORRY ZONE, i'm not sure if this will actually work because i've forgot how speed works
                        ##We should likely redefine how speed works to make it how quick it moves in each plane ?
                        #positron.update(self.positron_pos)
                        #electron.update(self.electron_pos)
                        ## Convert this logic to the np form.
                        #print(f"Positron Position {particles[0]['pos']}\n")
                        #self.positron_pos[2] += self.relative_particle_speed * 2/self.time_speed#relative_positron_speed  # Move proton1 along the positive z-axis (towards the center)
                        #self.electron_pos[2] -= self.relative_particle_speed * 2/self.time_speed#relative_electron_speed # Move proton2 along the negative z-axis
                        if particles[0]["pos"][2] > particles[1]["pos"][2]:
                            collided = True
                        #if self.p[2]>self.electron_pos[2]:
                        #    self.collided = True
                    Particle.draw_particles(particles) 
                    
                else: # If the positron and electron have collided
                    if not particles_created:
                        
                        positron_pos = particles[0]["pos"]
                        electron_pos = particles[1]["pos"]
                        particles, result_text = self.particle_generator.generate_particles(self.mode, positron_pos, electron_pos, self.relative_particle_speed,self.flash_manager,self.time_speed)

                        if len(particles)>0 and isinstance(particles[0], Blackhole):
                            black_hole = True

                        particles_created = True
                        #We define the collision results window
                        if self.mode.value == Mode.Educational.value:
                            _, total_energy_MeV, total_energy_GeV = self.utility.calculate_total_energy(self.relative_particle_speed)
                            
                            if total_energy_GeV < 1:
                                energy_text = f"{total_energy_MeV:.2f} MeV"
                            else:
                                energy_text = f"{total_energy_GeV:.2f} GeV"
                            
                            collision_results = {
                                "energy_text": energy_text,
                                "result_text": result_text
                            }
                            collision_results_window = True

                    else:
                        if not time_stop:
                            
                            Particle.update_particles(particles)
                            exploded_on_edge, fell_out_of_end = Particle.is_removed(particles, CYLINDER_RADIUS= CYLINDER_RADIUS, CYLINDER_HEIGHT= CYLINDER_HEIGHT)
                            if np.any(exploded_on_edge):
                                exploded_particles = particles[exploded_on_edge]
                                for particle in exploded_particles:
                                    self.flash_manager.add_flash(position=particle['pos'], size=0.3, brightness=1, duration=2)
                            combined_mask = exploded_on_edge | fell_out_of_end
                            particles = particles[~combined_mask]
                            
                        Particle.draw_particles(particles)
                            
                        self.flash_manager.update_and_draw()



                        if black_hole and particle.check_collision(self.camera_pos):
                            #print("Camera consumed by the black hole!")
                            particles = []
                            black_hole = False
                            #black_hole.play_animation(self.window)


                        
                        if len(particles) == 0 and collided: # Automatically reset the chamber
                            particles, collision_results_window, particles_created, collided, time_stop = self.restart_simulation()
                            self.simulating = False
                            if self.mode.value == Mode.Educational.value:
                                collision_results_window = True
                            
                            
                       
                self.handle_keyboard_input()
                time.sleep(1./240.)
            time.sleep(1./240.)
            if collision_results_window and collision_results is not None:
                CollisionResultsPage.draw(collision_results, self.window, self.window_size)


                

            
            imgui.render()
            impl.render(imgui.get_draw_data())
            glfw.swap_buffers(self.window)
            

        glfw.terminate()
        
if __name__ == "__main__":
    sim = Simulation()
