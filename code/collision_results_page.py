import imgui
import glfw

class CollisionResultsPage():

    @staticmethod
    def draw(collision_results, window, window_size):
        
        # Set the initial position and size of the collision results window
        window_width, window_height = window_size[0]/2.5, window_size[1]/3
        window_x = (window_size[0] ) * 2.5  // 5
        window_y = (glfw.get_window_size(window)[1]) // 48
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

