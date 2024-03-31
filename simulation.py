import time
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np
from constants import Mode, Toggle

from Particles.electron import Electron

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
   
    def __init__(self,mode = Mode.Educational):
        
        self.mode = mode
        self.window_size = (1080, 900)
        
        self.F_key_pressed = False
        self.R_key_pressed = False
        self.E_key_pressed = False
        self.instructions_shown = True
        self.utility = UtilityFunctions()
        self.particle_generator = ParticleGenerator()
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
        imgui.push_item_width(240)
        #imgui.push_item_height(40)
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
        imgui.pop_item_width()
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




        #Unfills
        if glfw.get_key(self.window, glfw.KEY_F) == glfw.PRESS and not self.F_key_pressed:
            self.filled = not self.filled
            self.F_key_pressed = True
        if glfw.get_key(self.window, glfw.KEY_F) == glfw.RELEASE:
            self.F_key_pressed = False

    def draw_cylinder(self,cylinder_radius,cylinder_height,segments = 128):
        glColor3f(0.75, 0.75, 0.75)  # Set the color of the grid lines to grey
        glLineWidth(0.5)  # Set the width of the grid lines
        
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

    def draw_control_instructions(self):
        # imgui.new_frame()
        # Define the control instructions
        instructions = [
            "Press SPACE to stop/start the simulation",
            "Press T to stop/resume time",
            "Press F to fill/unfill the cylinder",
            "Use WASD to change your viewing angle",
            "Use the arrow keys to modify your viewing position",
            "Press R to return to your original position",
            "Press E to hide/unhide control instructions"
        ]

        # Set the position and size of the overlay window
        window_width = 300
        window_height = 150
        window_x = (self.window_size[0])   / 3
        window_y = (glfw.get_window_size(self.window)[1]) // 12 * 10
        # window_x = 10
        # window_y = 10

        #window_width, window_height = self.window_size[0]/2.5, self.window_size[1]/3
        #window_x = (self.window_size[0] )/2
        #window_y = (glfw.get_window_size(self.window)[1]) // 12
        imgui.set_next_window_position(window_x, window_y)
        imgui.set_next_window_size(window_width, window_height)

        # Begin an ImGui window for the overlay
        imgui.set_next_window_position(window_x, window_y)
        imgui.set_next_window_size(window_width, window_height)
        imgui.begin("Control instructions", flags=imgui.WINDOW_ALWAYS_AUTO_RESIZE)

        # Render each line of the instructions
        for line in instructions:
            imgui.text(line)

        imgui.end()

        # End the ImGui window
        # imgui.end()

    def rotate_vector(self, vector, angle, axis):
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        return vector * cos_angle + np.cross(axis, vector) * sin_angle + axis * np.dot(axis, vector) * (1 - cos_angle)

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

    def draw_control_panel(self):
        # imgui.new_frame()
        def draw_checkbox_with_tooltip( label, variable, tooltip_text):
            clicked, variable = imgui.checkbox(label, variable)
            imgui.same_line()
            imgui.text("(i)")
            if imgui.is_item_hovered():
                imgui.set_tooltip(tooltip_text)
            return clicked, variable
        window_width, window_height = self.window_size[0]/2.5, self.window_size[1]/3
                
        window_x = (self.window_size[0]) * 0.3  // 5
        window_y = (glfw.get_window_size(self.window)[1]) // 48
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
        percentage = np.round(((self.time_speed/10)-0.6)*100)
        if percentage>=0:

            formatted_time_speed = f"Time Modifier +{percentage}%"
        else:
            formatted_time_speed = f"Time Modifier {percentage}%"
        imgui.push_item_width(240)
        changed, self.time_speed = imgui.slider_int(formatted_time_speed, self.time_speed, 1, 11)
        imgui.pop_item_width()
        
        
        
        imgui.columns(2, 'checkboxes', False)


        ##########TICKBOXES##################

        clicked, self.LHC_velocity_toggle = draw_checkbox_with_tooltip("Velocity of LHC",self.LHC_velocity_toggle,"Velocity achieved by the Large Hadron Collider")
       
        if clicked:
            if self.LHC_velocity_toggle:
                self.reset_checkboxes(ticked = Toggle.LHCVelocity)
                # https://public-archive.web.cern.ch/en/lhc/Facts-en.html
                self.relative_particle_speed = 0.999999991
            else:
                self.relative_particle_speed = 0.9

        
        clicked, self.synchotron_velocity_toggle = draw_checkbox_with_tooltip("Velocity of Synchotron",self.synchotron_velocity_toggle,"Velocity achieved by the Synchotron, the earliest collider at CERN")
       
        if clicked:
            if self.synchotron_velocity_toggle:
                self.reset_checkboxes(ticked = Toggle.SynchotronVelocity)
                #https://cds.cern.ch/record/1479637/files/1959_E_p29.pdf
                
                self.relative_particle_speed = 0.9993
            else:
                self.relative_particle_speed = 0.9

        clicked, self.enable_fun_mode = draw_checkbox_with_tooltip("Experimental Mode",self.enable_fun_mode,"Makes the collisions more interesting and not true to life")
       
        
        if clicked:
            if self.enable_fun_mode:
                self.mode = Mode.Fun
            else:
                self.mode = Mode.Educational
                
                

        ###SPEED OF LIGHT TOGGLEBOX 
        clicked, self.infinite_energy_toggle = draw_checkbox_with_tooltip("Speed of Light",self.infinite_energy_toggle,"Accelerates the particles to the speed of light")
        
        
        if clicked:
            if self.infinite_energy_toggle:
                self.reset_checkboxes(ticked = Toggle.LightVelocity)
                self.relative_particle_speed = 1.0
            else:
                self.relative_particle_speed = 0.9

        ### Filled in cylinder togglebox
        clicked, self.filled = draw_checkbox_with_tooltip("Fill in Cylinder",self.filled,"Fills in the gaps between the cylinder")
       
        ### MUON VELOCITY TOGGLEBOX
        clicked, self.muon_velocity_toggle = draw_checkbox_with_tooltip("Muon Velocity",self.muon_velocity_toggle,"Accelerates the particles to a velocity to create Muons")
        

        if clicked:
            if self.muon_velocity_toggle:
                self.reset_checkboxes(ticked = Toggle.MuonVelocity)
                self.relative_particle_speed = 0.9999999
            else:
                self.relative_particle_speed = 0.9
                

        
        imgui.next_column()

        ### TAU VELOCITY TOGGLEBOX
        clicked, self.tau_velocity_toggle = draw_checkbox_with_tooltip("Tau Velocity",self.tau_velocity_toggle,"Accelerates the particles to a velocity to create Tau particles")
       
        
        if clicked:
            if self.tau_velocity_toggle:
                self.reset_checkboxes(ticked = Toggle.TauVelocity)
                self.relative_particle_speed = 0.99999997
            else:
                self.relative_particle_speed = 0.9
                
        ### Gamma gluon VELOCITY TOGGLEBOX
        clicked, self.gamma_gluon_toggle = draw_checkbox_with_tooltip("Gamma-Gluon-Gluon Velocity",self.gamma_gluon_toggle,"Accelerates the particles to a velocity to create Gluons")
       

        if clicked:
            if self.gamma_gluon_toggle:
                self.reset_checkboxes(ticked = Toggle.GammaVelocity)
                self.relative_particle_speed = 0.999999997
            else:
                self.relative_particle_speed = 0.9
        
        ### Quark VELOCITY TOGGLEBOX
        clicked, self.quark_toggle = draw_checkbox_with_tooltip("Quark Velocity",self.quark_toggle,"Accelerates the particles to a velocity to create Quarks")
        

        if clicked:
            if self.quark_toggle:
                self.reset_checkboxes(ticked = Toggle.QuarkVelocity)
                self.relative_particle_speed = 0.9999999997
            else:
                self.relative_particle_speed = 0.9

        
        
        
        
        ### Z-Boson VELOCITY TOGGLEBOX
        clicked, self.ZBoson_toggle = draw_checkbox_with_tooltip("ZBoson Velocity",self.ZBoson_toggle,"Accelerates the particles to a velocity to create ZBosons")

        if clicked:
            if self.ZBoson_toggle:
                self.reset_checkboxes(ticked = Toggle.ZBosonVelocity)
                self.relative_particle_speed = 0.99999999994
            else:
                self.relative_particle_speed = 0.9
        
        ### Higgs Boson VELOCITY TOGGLEBOX
        clicked, self.higgs_toggle = draw_checkbox_with_tooltip("Higgs Boson Velocity",self.higgs_toggle,"Accelerates the particles to a velocity to produce the Higgs Boson")
       

        if clicked:
            if self.higgs_toggle:
                self.reset_checkboxes(ticked = Toggle.HiggsBosonVelocity)
                self.relative_particle_speed = 0.99999999997
            else:
                self.relative_particle_speed = 0.9

        ### WPlus VELOCITY TOGGLEBOX
        clicked, self.WPlus_toggle = draw_checkbox_with_tooltip("WPlus Velocity",self.WPlus_toggle,"Accelerates the particles to a velocity to produce the WPlus Boson")
        
        if clicked:
            if self.WPlus_toggle:
                self.reset_checkboxes(ticked = Toggle.WPlusVelocity)
                self.relative_particle_speed = 0.999999999992
            else:
                self.relative_particle_speed = 0.9
        
        

        imgui.dummy(1, 20)  # Add some space before the button (vertical padding)
        imgui.columns(3, "button_col", False)  # Create 3 columns; the button will be in the middle
        imgui.set_column_width(0, 120)  # Adjust the width of the left column
        imgui.next_column()  # Move to the middle column
        imgui.set_column_width(1, 200)  # Adjust the middle column where the button will be

        # Set the button size
        if imgui.button("Start Simulation", width=200, height=40):  # Adjust width and height as needed
            self.simulating = True

        

        
        imgui.columns(1)
        imgui.end()

        # imgui.end()

    def introduction_page(self, img_impl):
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

    def collision_results_window(self, collision_results):
        
        # Set the initial position and size of the collision results window
        window_width, window_height = self.window_size[0]/2.5, self.window_size[1]/3
        window_x = (self.window_size[0] ) * 2.5  // 5
        window_y = (glfw.get_window_size(self.window)[1]) // 48
        imgui.set_next_window_position(window_x, window_y)
        imgui.set_next_window_size(window_width, window_height)

        imgui.begin("Collision Results", True, imgui.WINDOW_ALWAYS_AUTO_RESIZE)

        # Add padding and spacing for better visual layout
        imgui.push_style_var(imgui.STYLE_FRAME_PADDING, (10, 10))
        imgui.push_style_var(imgui.STYLE_ITEM_SPACING, (10, 10))

        
        

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
        collision_results_window = True
        if imgui.button("Close"):
            collision_results_window = False

        imgui.pop_style_var(2)  # Pop the style variables for padding and spacing
        imgui.end()
        # imgui.end()
        return(collision_results_window)

    def set_up_camera(self):
        self.camera_pos = np.array([self.eye_x, self.eye_y, self.eye_z], dtype=np.float32)
        self.camera_front = np.array([self.center_x - self.eye_x, self.center_y - self.eye_y, self.center_z - self.eye_z], dtype=np.float32)
        self.camera_front = self.camera_front / np.linalg.norm(self.camera_front)
        self.camera_up = np.array([self.up_x, self.up_y, self.up_z], dtype=np.float32)
        self.camera_position_speed = 0.3
        self.camera_angle_speed = 1
        
    def restart_simulation(self):
        self.positron_pos = [0, 0, np.round((-CYLINDER_HEIGHT / 2 + 1.5))]  # Adjust start position
        self.electron_pos = [0, 0, np.round(CYLINDER_HEIGHT / 2 - 1.5)]
        
        
        self.collided = False
        positron = Positron(self.positron_pos[0], self.positron_pos[1], self.positron_pos[2], 0.2)
        electron = Electron(self.electron_pos[0], self.electron_pos[1], self.electron_pos[2], 0.2)
        
        collision_results_window = False
        particles_created = False
        particles = []

        return(positron, electron, particles, collision_results_window, particles_created)

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

        ###   THIS WHOLE SECTION IS JUST INITIALISING THE SIMULATION
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
        self.eye_x, self.eye_y, self.eye_z = STARTING_EYE_POSITION # Position the camera slightly off-center and tilted
        
        self.center_x, self.center_y, self.center_z = STARTING_CENTRE_POSITION  # Look towards the center of the cylinder
        self.up_x, self.up_y, self.up_z = STARTING_UP_DIRECTION # Set the up direction
        #gluLookAt(self.eye_x, self.eye_y, self.eye_z, self.center_x, self.center_y, self.center_z, self.up_x, self.up_y, self.up_z)
        self.set_up_camera()

        


        self.flash_manager = Flash()
        self.positron_pos = [0, 0, np.round((-CYLINDER_HEIGHT / 2 + 1.5))]  # Adjust start position
        self.electron_pos = [0, 0, np.round(CYLINDER_HEIGHT / 2 - 1.5)]  # Adjust start position
        self.relative_particle_speed = 0.9
        particles = []    
        self.collided = False
        particles_created = False
        self.simulating = False
        self.time_stop = False
        self.enable_fun_mode = False
        self.filled = False
        self.reset_checkboxes()
        positron = Positron(self.positron_pos[0], self.positron_pos[1], self.positron_pos[2], 0.2)
        electron = Electron(self.electron_pos[0], self.electron_pos[1], self.electron_pos[2], 0.2)
        self.time_speed = 6
        black_hole = False
        collision_results_window = False
        self.stars = self.generate_stars(1000)


        ##### RUNNING THE SIMULATION
        
        while not glfw.window_should_close(self.window):
            
            imgui.new_frame()
            glfw.poll_events()
            if self.instructions_shown:
                self.draw_control_instructions()
            

            
             
            
            glClearColor(0, 0, 0, 1.0)  # Set the background color to black
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            

            glLoadIdentity()
            
            gluLookAt(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2],
                    self.camera_pos[0] + self.camera_front[0], self.camera_pos[1] + self.camera_front[1], self.camera_pos[2] + self.camera_front[2],
                    self.camera_up[0], self.camera_up[1], self.camera_up[2])
            

            #Draw the background
            self.draw_stars()
            
            self.draw_cylinder(CYLINDER_RADIUS,CYLINDER_HEIGHT)
            
            
            

            
            
            
            if not self.simulating:
                
                self.handle_keyboard_input()
                impl.process_inputs()
                self.draw_control_panel()
                
                
                if self.simulating:
                    #Essentially, if the state of simulating changes after validating keyboard inputs then we know that the simulation has been started
                    positron, electron, particles, collision_results_window, particles_created = self.restart_simulation()


                #Draw the stationary positrons and electrons, if you delete this section it just resets them.  
                if not self.collided:
                    positron.draw()
                    electron.draw()
                else:
                    for particle in particles:
                        particle.draw()

                
                
            #If the experiment has begun 
            if self.simulating:

                #Collided defines when the electron and the positron have collided .
                if not self.collided:
                    # This is to allow for timestops <- essentially just draw and don't update.
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
                        
                        
                        particles, result_text = self.particle_generator.generate_particles(self.mode, self.positron_pos, self.electron_pos,self.relative_particle_speed,self.flash_manager,self.time_speed)

                        if len(particles)>0 and isinstance(particles[0], Blackhole):
                            black_hole = True


                        particles_created= True
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
                        
                        for particle in particles:
                            
                            if not self.time_stop:
                                particle.update()
                                particle_pos = particle.pos

                                # Calculate the distance between the particle and the cylinder's center
                                distance = np.sqrt(particle_pos[0]**2 + particle_pos[1]**2)

                                # Check if the particle is outside the cylinder's radius and within the cylinder's height range
                                if (distance > CYLINDER_RADIUS and -CYLINDER_HEIGHT/2 <= particle_pos[2] <= CYLINDER_HEIGHT/2):
                                    # Collision detected
                                    #p.removeBody(particle.particleID)
                                    particles.remove(particle)
                                    self.flash_manager.add_flash(position=particle.pos, size=0.3, brightness=1, duration=2)
                                
                                elif (particle_pos[2]>np.round(CYLINDER_HEIGHT / 2 - 1.5) or particle_pos[2]<np.round(-CYLINDER_HEIGHT / 2 + 1.5)):
                                    
                                    particles.remove(particle)
                            particle.draw()
                            
                        self.flash_manager.update_and_draw()



                        if black_hole and particle.check_collision(self.camera_pos):
                            #print("Camera consumed by the black hole!")
                            particles = []
                            black_hole = False
                            #black_hole.play_animation(self.window)


                        
                        if len(particles) == 0 and self.collided: # Automatically reset the chamber
                            positron, electron, particles, collision_results_window, particles_created = self.restart_simulation()
                            self.simulating = False
                            
                            
                            
                       
                self.handle_keyboard_input()
                time.sleep(1./240.)
            time.sleep(1./240.)
            if collision_results_window:

                collision_results_window = self.collision_results_window(collision_results)

                

            
            imgui.render()
            impl.render(imgui.get_draw_data())
            glfw.swap_buffers(self.window)
            

        glfw.terminate()
        
if __name__ == "__main__":
    sim = Simulation()