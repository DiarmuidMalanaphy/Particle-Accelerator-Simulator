from constants import Toggle, Mode
import imgui
from sliders import LogarithmicSlider
import glfw
import numpy as np

class ParticleControlPanel():
    
    def __init__(self,window, window_size, relative_particle_speed = 0.9, filled = False, time_speed = 1, mode = Mode.Educational, simulating = False):
                self.window = window
                self.window_size = window_size
                self.slider = LogarithmicSlider( 
                    "Particle Speed",
                    value = relative_particle_speed
                    )
                # These are the values we're looking to extract from this panel.

                self.relative_particle_speed = relative_particle_speed
                self.filled = filled
                self.time_speed = time_speed
                self.mode = mode 
                self.enable_fun_mode = (mode != Mode.Educational)
                self.simulating = simulating

    def get_information(self):

        return self.relative_particle_speed, self.filled, self.time_speed, self.mode, self.simulating
                

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
        changed, self.relative_particle_speed = self.slider.display()
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
                self.relative_particle_speed = 0.999999999982
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

