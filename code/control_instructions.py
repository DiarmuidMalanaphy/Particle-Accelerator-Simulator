import imgui
import glfw


class ControlInstructions():

    @staticmethod
    def draw(window, window_size):
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
        window_x = (window_size[0])   / 3
        window_y = (glfw.get_window_size(window)[1]) // 12 * 10
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


