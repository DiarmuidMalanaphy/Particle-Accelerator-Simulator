from OpenGL.GLU import *
from OpenGL.GL import *

class Flash:
    def __init__(self):
        self.flashes = []

    def add_flash(self, position, size=0.5, brightness=1.0, duration=10):
        """
        Add a new flash to the list.
        Position is a tuple (x, y, z).
        Size determines the radius of the flash sphere.
        Brightness determines the intensity of the flash color (1.0 is max brightness).
        Duration is the number of frames the flash will last.
        """
        self.flashes.append({
            "position": position,
            "size": size,
            "brightness": brightness,
            "duration": duration
        })

    def update_and_draw(self):
        for i in range(len(self.flashes) - 1, -1, -1):
            flash = self.flashes[i]
            glPushMatrix()
            glColor3f(flash["brightness"], flash["brightness"], 0.0)  # Use brightness for color
            glTranslatef(*flash["position"])  # Move to the flash's position
            
            quadric = gluNewQuadric()  # Create a new quadric object
            gluSphere(quadric, flash["size"], 32, 32)  # Draw the sphere with the specified size
            
            glPopMatrix()

            flash["duration"] -= 1
            if flash["duration"] <= 0:
                self.flashes.pop(i)
