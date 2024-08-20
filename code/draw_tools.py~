import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


class DrawTools():
    @staticmethod
    def draw_cylinder(cylinder_radius,cylinder_height,filled = False, segments = 128):
        glColor3f(0.75, 0.75, 0.75)  # Set the color of the grid lines to grey
        glLineWidth(0.5)  # Set the width of the grid lines
        
        if filled:
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

    @staticmethod
    def generate_stars(num_stars):
        stars = []
        for _ in range(num_stars):
            x = np.random.uniform(-1.0, 1.0)
            y = np.random.uniform(-1.0, 1.0)
            z = np.random.uniform(-1.0, 1.0)
            stars.append((x, y, z))
        return stars

    @staticmethod
    def draw_stars(stars):
        glPointSize(2.0)  # Set the size of the star points
        glColor3f(1.0, 1.0, 1.0)  # Set the color of the stars to white
        glBegin(GL_POINTS)
        for star in stars:
            glVertex3f(star[0]*100, star[1]*100, star[2] * 100)  # Scale down the z-coordinate
        glEnd()



