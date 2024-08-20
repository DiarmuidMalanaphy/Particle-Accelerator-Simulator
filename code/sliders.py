import imgui
from constants import Mode
import numpy as np

class Slider():
    pass

class LogarithmicSlider(Slider):

    def __init__ (self, label, max_nines = 15, mode = Mode.Educational , value = 0.9):
        self.label = label
        self.max_nines = max_nines 
        self.mode = mode
        self.value = value

    def set_mode(self, mode = Mode.Educational):
        self.mode = mode



    def display(self):
        imgui.push_item_width(240)
        #imgui.push_item_height(40)
        # Directly map the value to a "number of nines" representation
        if self.value >= 1.0:
            slider_pos = self.max_nines
        else:
            slider_pos = max(0, min(self.max_nines, int(np.floor(-np.log10(1 - self.value)))))

        # Adjust the slider
        if self.value == 1:
            if self.mode.value == Mode.Educational:
                value = 0.999999999999999
                changed, new_slider_pos = imgui.slider_int(self.label, slider_pos, 0, self.max_nines, f"{value}c")
                
                
            else:
                changed, new_slider_pos = imgui.slider_int(self.label, slider_pos, 0, self.max_nines, f"c")
        else:
            changed, new_slider_pos = imgui.slider_int(self.label, slider_pos, 0, self.max_nines, f"{self.value}c")
        

        if changed:
            # Convert back to the float value
            if new_slider_pos == self.max_nines:
                new_value = 1
            else:
                new_value = 1 - 10 ** (-new_slider_pos - 1)
        imgui.pop_item_width()
        return changed, self.value if not changed else new_value

