from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
import numpy as np


STARTING_EYE_POSITION = (3.0, 3.0, 25.0)
STARTING_CENTRE_POSITION = (0.0, 0.0, 0.0)
STARTING_UP_DIRECTION = (0.0, 1.0, 0.0)


class CameraManager():
   
    def __init__(self):
        self.reset_camera()

    def set_up_camera(self):
        self.camera_pos = np.array([self.eye_x, self.eye_y, self.eye_z], dtype=np.float32)
        self.camera_front = np.array([self.center_x - self.eye_x, self.center_y - self.eye_y, self.center_z - self.eye_z], dtype=np.float32)
        self.camera_front = self.camera_front / np.linalg.norm(self.camera_front)
        self.camera_up = np.array([self.up_x, self.up_y, self.up_z], dtype=np.float32)
        self.camera_position_speed = 0.3
        self.camera_angle_speed = 1

    def reset_camera(self):
        self.eye_x, self.eye_y, self.eye_z = STARTING_EYE_POSITION # Position the camera slightly off-center and tilted
        self.center_x, self.center_y, self.center_z = STARTING_CENTRE_POSITION  # Look towards the center of the cylinder
        self.up_x, self.up_y, self.up_z = STARTING_UP_DIRECTION
        self.set_up_camera()

    def move_camera_up(self):
        self.camera_pos += self.camera_front * self.camera_position_speed
        self.fix_range()

    def move_camera_down(self):
        self.camera_pos -= self.camera_front * self.camera_position_speed
        self.fix_range()

    def move_camera_left(self):
        self.camera_pos -= np.cross(self.camera_front, self.camera_up) * self.camera_position_speed
        self.fix_range()

    def move_camera_right(self):
        self.camera_pos += np.cross(self.camera_front, self.camera_up) * self.camera_position_speed
        self.fix_range()

    def move_camera_krs(self):
        self.camera_pos -= self.camera_up * self.camera_position_speed
        self.fix_range()

    def tilt_camera_forward(self):
        pitch = np.radians(self.camera_angle_speed)
        self.camera_front = self.rotate_vector(self.camera_front, pitch, np.cross(self.camera_front, self.camera_up))
        self.camera_up = np.cross(np.cross(self.camera_front, self.camera_up), self.camera_front)
        self.fix_range()

    def tilt_camera_backward(self):
        pitch = np.radians(-self.camera_angle_speed)
        self.camera_front = self.rotate_vector(self.camera_front, pitch, np.cross(self.camera_front, self.camera_up))
        self.camera_up = np.cross(np.cross(self.camera_front, self.camera_up), self.camera_front)
        self.fix_range()


    def tilt_camera_left(self):
        yaw = np.radians(self.camera_angle_speed)
        self.camera_front = self.rotate_vector(self.camera_front, yaw, self.camera_up)
        self.fix_range()


    def tilt_camera_right(self):
        yaw = np.radians(-self.camera_angle_speed)
        self.camera_front = self.rotate_vector(self.camera_front, yaw, self.camera_up)
        self.fix_range()



    def fix_range(self):
        angle_range = 1.0 #There's more viewing range but it hates you using it
        self.camera_front[0] = (self.camera_front[0] + angle_range) % (2 * angle_range) -  angle_range
        self.camera_front[1] = max(-angle_range, min(angle_range, self.camera_front[1]))

        self.camera_front = self.camera_front / np.linalg.norm(self.camera_front)

    def rotate_vector(self, vector, angle, axis):
        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)
        return vector * cos_angle + np.cross(axis, vector) * sin_angle + axis * np.dot(axis, vector) * (1 - cos_angle)
    
    def look(self):
        glLoadIdentity()
            
        gluLookAt(self.camera_pos[0], self.camera_pos[1], self.camera_pos[2],
                    self.camera_pos[0] + self.camera_front[0], self.camera_pos[1] + self.camera_front[1], self.camera_pos[2] + self.camera_front[2],
                    self.camera_up[0], self.camera_up[1], self.camera_up[2])

