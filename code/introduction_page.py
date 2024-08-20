import imgui
import glfw
class IntroductionPage():

    def __init__(self):
        pass

    def display(self, img_impl, window):
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

            self.handle_intro_keys(window)
            imgui.render()
            img_impl.render(imgui.get_draw_data())
            glfw.swap_buffers(window)

    def handle_intro_keys(self, window):
        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            self.intro_page = False
            self.space_key_pressed = True



