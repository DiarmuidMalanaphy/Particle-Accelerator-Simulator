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
from camera_manager import CameraManager


import imgui
from imgui.integrations.glfw import GlfwRenderer
from utility import UtilityFunctions





"""
    3D Simulation of a particle accelerator with different modes for fun or Education


    The simulation is quite simplistic and mostly covers the interaction of an electron and positron colliding at relativistic speeds.

    The educational mode describes the kinetic energy of the input particles and the resultant particle from each speed.

    The fun mode provides a range of particles with interesting colours to observe. 

"""



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
        self.camera_manager = CameraManager()
       
        self.space_key_pressed = True
        self.F_key_pressed = False
        self.R_key_pressed = False
        self.E_key_pressed = False
        self.H_key_pressed = False
        self.instructions_shown = True
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
        return 


    
    def handle_keyboard_input(self):
        # Update camera position with arrow keys
        if glfw.get_key(self.window, glfw.KEY_UP) == glfw.PRESS:
            self.camera_manager.move_camera_up()
        if glfw.get_key(self.window, glfw.KEY_DOWN) == glfw.PRESS:
            self.camera_manager.move_camera_down()
        if glfw.get_key(self.window, glfw.KEY_LEFT) == glfw.PRESS:
            self.camera_manager.move_camera_left()
        if glfw.get_key(self.window, glfw.KEY_RIGHT) == glfw.PRESS:
            self.camera_manager.move_camera_right()
        if glfw.get_key(self.window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS:
            self.camera_manager.move_camera_krs()
        if glfw.get_key(self.window, glfw.KEY_W) == glfw.PRESS:
            self.camera_manager.tilt_camera_forward()
        if glfw.get_key(self.window, glfw.KEY_S) == glfw.PRESS:
            self.camera_manager.tilt_camera_backward()
        if glfw.get_key(self.window, glfw.KEY_A) == glfw.PRESS:
            self.camera_manager.tilt_camera_left()
        if glfw.get_key(self.window, glfw.KEY_D) == glfw.PRESS:
            self.camera_manager.tilt_camera_right()       
        
       

        #TimeStop and restarting experiment 


        #Starts the experiment
        if glfw.get_key(self.window, glfw.KEY_SPACE) == glfw.PRESS and not self.space_key_pressed:
            self.simulating = not self.simulating
            self.control_panel.set_simulating(value = self.simulating)
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
            self.camera_manager.reset_camera()
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

   

    
    

    
           
    def restart_simulation(self):
        
        
        collided = False
        time_stop = False

        starting_particles = ParticleGenerator.build_particles_array(2, particle_dtype = Particle.get_np_type(100 * self.time_speed))
         
         
        starting_particles[0] = Positron(POSITRON_STARTING_POSITION, np.asarray([0, 0, 100 ]), time_speed = self.time_speed).to_np() 
        starting_particles[1] = Electron(ELECTRON_STARTING_POSITION, np.asarray([0, 0, -100 ]), time_speed = self.time_speed).to_np()

        collision_results_window = False
        particles_created = False
        

        return starting_particles, collision_results_window, particles_created, collided, time_stop

    @staticmethod
    def remove_particles(particles, flash_manager):
        exploded_on_edge, fell_out_of_end = Particle.is_removed(particles, CYLINDER_RADIUS= CYLINDER_RADIUS, CYLINDER_HEIGHT= CYLINDER_HEIGHT)
        if np.any(exploded_on_edge):
            exploded_particles = particles[exploded_on_edge]
            for particle in exploded_particles:
                flash_manager.add_flash(position=particle['pos'], size=0.3, brightness=1, duration=2)
        combined_mask = exploded_on_edge | fell_out_of_end
        particles = particles[~combined_mask]
        return particles

    @staticmethod
    def initialise_viewpoints():
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

    
       
    def start_simulating(self):

        ###   THIS WHOLE SECTION IS JUST INITIALISING THE SIMULATION
        
        
        imgui.create_context()
        impl = GlfwRenderer(self.window)

        intro_page = IntroductionPage()
        intro_page.display(impl, self.window) 

        self.initialise_viewpoints() 


        


        


        flash_manager = Flash()
        self.get_control_panel_info()

        #Defined During Simulation
        particles, collision_results_window, particles_created, collided, self.time_stop = self.restart_simulation()
        collision_results = None
        particles_created = False
        show_cylinder = True
        self.time_stop = False
        
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
           
            self.camera_manager.look()

                       

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
                    particles, collision_results_window, particles_created, collided, self.time_stop = self.restart_simulation()


                #Draw the stationary positrons and electrons, if you delete this section it just resets them.
                
                Particle.draw_particles(particles) 
                
                
            #If the experiment has begun 
            if self.simulating:
                
                #Collided defines when the electron and the positron have collided .
                if not collided:
                    
                    if particles[0]["pos"][2] > particles[1]["pos"][2]:
                        collided = True
                    
                else: # If the positron and electron have collided
                    if not particles_created:
                        
                        positron_pos = particles[0]["pos"]
                        electron_pos = particles[1]["pos"]
                        particles, result_text = self.particle_generator.generate_particles(self.mode, positron_pos, electron_pos, self.relative_particle_speed, flash_manager,self.time_speed, max_particles = 10000)

                        if len(particles)>0 and isinstance(particles[0], Blackhole):
                            black_hole = True

                        particles_created = True
                        #We define the collision results window
                        if self.mode.value == Mode.Educational.value:
                            collision_results = UtilityFunctions.get_collision_results(self.relative_particle_speed, result_text)
                            collision_results_window = True
                       


                    else:
                        if not self.time_stop and not black_hole:
                           particles = self.remove_particles(particles, flash_manager) 
                            
                            

                        if black_hole and particles[0].check_collision(self.camera_pos):
                            particles = []
                            black_hole = False


                        
                        if len(particles) == 0 and collided: # Automatically reset the chamber
                            particles, collision_results_window, particles_created, collided, self.time_stop = self.restart_simulation()
                            self.simulating = False
                            self.control_panel.set_simulating(value = self.simulating)
                            if self.mode.value == Mode.Educational.value:
                                
                                collision_results_window = True
                            
                            
                # This is to allow for timestops <- essentially just draw and don't update.
                if not black_hole:
                    if not self.time_stop:
                        Particle.update_particles(particles)
                    flash_manager.update_and_draw() 
                    Particle.draw_particles(particles)
                else:
                    blackhole = particles[0]
                    blackhole.update()
                    blackhole.draw_particle()

                self.handle_keyboard_input()

            time.sleep(1./240.)
            if collision_results_window and collision_results is not None:
                CollisionResultsPage.draw(collision_results, self.window, self.window_size)


                

            
            imgui.render()
            impl.render(imgui.get_draw_data())
            glfw.swap_buffers(self.window)
            

        glfw.terminate()
        
if __name__ == "__main__":
    sim = Simulation()
