import time
import glfw
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import pymunk
import pybullet as p
import pybullet_data
from electron import Electron
from kaon import Kaon
from photon import Photon
from pion import Pion
from positron import Positron
from flash import Flash



#Notes to take

"""
Get the actual nuclear reactions between two protons smashing into eachother - so Kaons and Pions
Make it so you can enter different kinetic enrgies, maybe with a scale?
add a noise - Kaboom, if you make the mass high enough maybe black hole
Make sure that energy is conserved
Make the reaction actually occur in a reaction chamber
Make the reactions have a cloud of energy intially so the weird gap of collision doesn't exist.
Different time controls - So make it go at 3x slower



Next addons - Make a summarisation at the end - displaying the amount of kinetic energy, number of particles created and the distribution


Next next step - create an actual simulation of derived ATLAS data and actually understand ROOT


    RULES speed is between 0-1 and represents 0 to c
        - make em able to make it 2 and increase radius to 1 for that case and explode the earth


"""

def initialize_glfw():
    
    if not glfw.init():
        raise Exception("glfw can not be initialized!")

    window = glfw.create_window(720, 600, "Proton-Proton Collision Simulation", None, None)

    if not window:
        glfw.terminate()
        raise Exception("glfw window can not be created!")

    glfw.set_window_pos(window, 400, 200)
    glfw.make_context_current(window)

    return window


   


def main():
    window = initialize_glfw()

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
    eye_x, eye_y, eye_z = 3.0, 3.0, 25.0  # Position the camera slightly off-center and tilted
    center_x, center_y, center_z = 0.0, 0.0, 0.0  # Look towards the center of the cylinder
    up_x, up_y, up_z = 0.0, 1.0, 0.0  # Set the up direction
    gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, up_x, up_y, up_z)

    
    
    flash_manager = Flash()

    space = pymunk.Space()
    space.gravity = (0, 0)  # Set gravity to zero for simplicity
    physicsClient = p.connect(p.DIRECT)
    # physicsClient = p.connect(p.GUI)
    cylinder_radius = 5
    cylinder_height = 100

    
    
   # proton1_pos = np.array([0.0, 0.0, -cylinder_height / 2 + 1.5])  # Near one end
    #proton2_pos = np.array([0.0, 0.0, cylinder_height / 2 - 1.5])

    positron_pos = [0, 0, -cylinder_height / 2 + 1.5]  # Adjust start position
    
    positron_collision = p.createCollisionShape(p.GEOM_SPHERE, radius=0.2)
    positron_visual = p.createVisualShape(p.GEOM_SPHERE, radius=0.2, rgbaColor=[1, 0, 0, 1])
    positron_id = p.createMultiBody(baseMass=1, baseCollisionShapeIndex=positron_collision,
                                 baseVisualShapeIndex=positron_visual,
                                   basePosition=positron_pos)

    # Proton 2
    electron_pos = [0, 0, cylinder_height / 2 - 1.5]  # Adjust start position
    
    electron_collision = p.createCollisionShape(p.GEOM_SPHERE, radius=0.2)
    electron_visual = p.createVisualShape(p.GEOM_SPHERE, radius=0.2, rgbaColor=[0, 0, 1, 1])
    electron_id = p.createMultiBody(baseMass=1, 
                                baseCollisionShapeIndex=electron_collision,
                                  baseVisualShapeIndex=electron_visual,
                                    basePosition=electron_pos)
    



    cylinder_collision_shape = p.createCollisionShape(
        shapeType=p.GEOM_CYLINDER,
        radius=cylinder_radius,  # This should match the OpenGL cylinder radius
        height=cylinder_height,  # This should match the OpenGL cylinder height
        collisionFramePosition=[0,0,0]
        
    )

    cylinder_visual_shape = p.createVisualShape(
        shapeType=p.GEOM_CYLINDER,
        radius=cylinder_radius,  # Match the radius used in OpenGL
        length=cylinder_height,  # Use 'length' for height here, to match OpenGL
        rgbaColor=[0.6, 0.6, 0.6, 1],
        visualFramePosition=[0,0,0]
    )

    cylinder_id = p.createMultiBody(
        baseMass=0,  # Static body if mass is 0
        baseCollisionShapeIndex=cylinder_collision_shape,
        baseVisualShapeIndex=cylinder_visual_shape,
        basePosition=[0, 0, 0]  # Centered at the origin, as in your OpenGL code
    )
    
    

    

    positron = Positron(positron_pos[0], positron_pos[1], positron_pos[2], 0.15)
    electron = Electron(electron_pos[0], electron_pos[1], electron_pos[2], 0.15) 


    positron_speed = 0.5
    electron_speed = 0.5
    particles = []
    particle_ids = []
    collided = False
    particles_created = False
    
    while not glfw.window_should_close(window):
        glfw.poll_events()
        glClearColor(0.0, 0.0, 0.0, 1.0)  # Set the background color to black
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glLoadIdentity()
        gluLookAt(eye_x, eye_y, eye_z, center_x, center_y, center_z, up_x, up_y, up_z)

        

        #Draw the cylinder ####


        # Draw the grid lines on the cylinder
        glColor3f(0.0, 1.0, 0.0)  # Set the color of the grid lines to green
        glLineWidth(0.5)  # Set the width of the grid lines
        glBegin(GL_LINES)
        for i in range(128):
            angle = i * (2 * np.pi / 128)
            x = cylinder_radius * np.cos(angle)
            y = cylinder_radius * np.sin(angle)
            glVertex3f(x, y, -cylinder_height / 2)  # Start from the negative end of the cylinder
            glVertex3f(x, y, cylinder_height / 2)
        glEnd()


        ###

        # Animate protons moving towards each other in 3D space until they collide
        if not collided:
            positron.update(positron_pos)
            electron.update(electron_pos)

            positron.draw()
            electron.draw()

            positron_pos[2] += positron_speed  # Move proton1 along the positive z-axis (towards the center)
            electron_pos[2] -= electron_speed # Move proton2 along the negative z-axis

            

            
            p.resetBasePositionAndOrientation(positron_id, positron_pos, [0, 0, 0, 1])
            p.resetBasePositionAndOrientation(electron_id, electron_pos, [0, 0, 0, 1])
            p.stepSimulation()
            contacts = p.getContactPoints(positron_id, electron_id)
            if contacts:
                
                collided = True
                flash_manager.add_flash(position=[(positron_pos[0] + electron_pos[0]) / 2, (positron_pos[1] + electron_pos[1]) / 2, (positron_pos[2] + electron_pos[2]) / 2], size=0.5, brightness=8.0, duration=2)

        else:


            # After collision, create and draw particles with trailing effect
            if not particles_created:
                
                #KE = (1/2)*(m)*(v^2)
                #m of electron/positron  is 9.1093837 × 10-31 kilograms - for computational efficiency  9.1*10*31
                def particle_kinetic_energy(v, m):
                    """
                    Calculate the relativistic kinetic energy given a velocity and mass.
                    - v is the velocity of the particle.
                    - m is the mass of the particle.
                    Returns kinetic energy in eV.
                    """
                    c = 299792458  # Speed of light in m/s

                    # Calculate the Lorentz factor
                    gamma = 1 / np.sqrt(1 - (v**2 / c**2))

                    # Calculate the relativistic kinetic energy in joules
                    KE_joules = (gamma - 1) * m * c**2

                    # Convert kinetic energy to eV
                    KE_eV = KE_joules / (1.602176634e-19)
                    return KE_eV

                # Assuming positron_speed and electron_speed are defined and are fractions of the speed of light (e.g., 0.99 for 99% of the speed of light)
                m = 9.1e-31  # Mass of electron/positron in kg
                c = 299792458
                positron_speed = 0.001 * c  # 99% speed of light
                electron_speed = 0.001 * c  # 99% speed of light

                # Calculate kinetic energy for both particles
                positron_kinetic_energy = particle_kinetic_energy(positron_speed, m)
                electron_kinetic_energy = particle_kinetic_energy(electron_speed, m)

                # Sum of kinetic energies in eV
                total_kinetic_energy_eV = positron_kinetic_energy + electron_kinetic_energy

                # Convert total kinetic energy to GeV
                total_kinetic_energy_GeV = total_kinetic_energy_eV / 10**9
                total_kinetic_energy_MeV = total_kinetic_energy_eV / 10**6

                print(f"Total Kinetic Energy: {total_kinetic_energy_GeV} GeV")
                print(f"Total Kinetic Energy: {total_kinetic_energy_MeV} MeV")
                #https://public-archive.web.cern.ch/en/lhc/Facts-en.html
                rest_energy_eV =  2 * m * (c**2) / (1.602176634e-19)

                total_energy_eV = total_kinetic_energy_eV + rest_energy_eV 

                total_energy_MeV = total_energy_eV / 10**6

                print(f"Total Kinetic Energy: {total_energy_MeV} MeV")

                #Right now we're going to just divide by the amount of energy for a photon
                

                def generate_directions(num_particles):
                    directions = []
                    total_vector = np.array([0.0, 0.0, 0.0])

                    for _ in range(num_particles - 1):
                        # Generate a random 3D unit vector
                        phi = np.random.uniform(0, 2 * np.pi)
                        theta = np.random.uniform(0, np.pi)
                        x = np.sin(theta) * np.cos(phi)
                        y = np.sin(theta) * np.sin(phi)
                        z = np.cos(theta)
                        
                        direction = np.array([x, y, z])
                        directions.append(direction)
                        total_vector += direction

                    # Calculate the last direction to ensure momentum conservation
                    last_direction = -total_vector
                    directions.append(last_direction)

                    return directions

                # Assuming you chose to generate 2 photons, leading to 1 pair
                choice = np.random.choice([2, 3, 4, 5], p=[0.53, 0.32, 0.11, 0.04])
                

                print(choice)

                directions = generate_directions(choice)

                for direction in directions:
                    print(f"Direction: {direction}")


                #for _ in range(choice):
                for direction in directions:

                    #Particles created -> 
                    #   photon photon constant speed <- More dependant on energy
                    #   muon
                    # angle_xy = np.random.uniform(0, 2 * np.pi)
                    # angle_z = np.random.uniform(0, np.pi)
                    # speed = np.random.uniform(0.35, 1)
                    speed = 1

                    # particle_x = np.cos(angle_xy) * np.sin(angle_z) * speed
                    # particle_y = np.sin(angle_xy) * np.sin(angle_z) * speed
                    # particle_z = np.cos(angle_z) * speed

                    #JointSpeed = 

                    # if np.random.rand() < 0.7:
                    #     particle = Pion(1)
                    #     particle_radius = 0.05
                        
                    # else:
                    #     particle = Kaon(particle_x, particle_y, particle_z, speed)
                    #     particle_radius = 0.075
                    particle_x = direction[0] * speed
                    particle_y = direction[1] * speed
                    particle_z = direction[2] * speed
                    particle = Photon(particle_x,particle_y,particle_z,1)
                    
                    particle_radius = 0.05

                    particle_pos = [particle_x, particle_y, particle_z]
                    particle_collision = p.createCollisionShape(p.GEOM_SPHERE, radius=0.05)
                    particle_visual = p.createVisualShape(p.GEOM_SPHERE, radius=particle_radius, rgbaColor=[1, 1, 0, 1])
                    particle_id = p.createMultiBody(baseMass=0.1, baseCollisionShapeIndex=particle_collision,
                                                    baseVisualShapeIndex=particle_visual,
                                                    basePosition=particle_pos)
                    particle_ids.append(particle_id)

                    particles.append(particle)
                particles_created = True

            

            for particle, particle_id in zip(particles, particle_ids):
                particle.update()
                particle.draw()

                
                p.resetBasePositionAndOrientation(particle_id, particle.pos, [0, 0, 0, 1])
                p.stepSimulation()

                contacts = p.getContactPoints(particle_id, cylinder_id)
                if not contacts:
                    
                    p.removeBody(particle_id)
                    particles.remove(particle)
                    particle_ids.remove(particle_id)
                    flash_manager.add_flash(position=particle.pos, size=0.1, brightness=0.5, duration=0.5)
            flash_manager.update_and_draw()
             
            time.sleep(1./240.)
            

        glfw.swap_buffers(window)
        

    glfw.terminate()
if __name__ == "__main__":
    main()