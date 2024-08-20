import numpy as np
from Particles.gluon import Gluon
from constants import Mode
from Particles.squi import Squi

from Particles.muon import Muon
from Particles.photon import Photon
from Particles.pion import Pion
from Particles.wboson import WBoson
from Particles.higgs import HiggsBoson
from Particles.quark import Quark
from Particles.tau import Tau
from Particles.particle import Particle
from Particles.blackhole import Blackhole


from utility import UtilityFunctions, Constants

class ParticleGenerator():
#
    
    def __init__(self):
        self.utility = UtilityFunctions()
    def generate_particles(self, mode, positron_pos, electron_pos, particle_speed, flash_manager, time_speed):
        self.particle_dtype = Particle.get_np_type(100 * time_speed)


        total_energy_eV, total_energy_MeV, total_energy_GeV = self.utility.calculate_total_energy(particle_speed)
        collision_pos = self.utility.calculate_mid_point_positron_electron(positron_pos,electron_pos)

        if mode.value == Mode.Educational.value: # Educational
            particles, result_text = self.generate_educational_particles(total_energy_eV, total_energy_MeV, total_energy_GeV,collision_pos,flash_manager,time_speed)
            return particles, result_text
        
        else:
            particles = self.generate_fun_particles(total_energy_eV, particle_speed, collision_pos, time_speed, flash_manager)
            return particles, ""

    def generate_fun_particles(self, total_energy_eV, particle_speed, collision_pos, time_speed, flash_manager, max_particles =  100000):
        particle_dtype = Particle.get_np_type(100 * particle_speed)
        particles = np.empty(max_particles, dtype=particle_dtype)
    

        if particle_speed == 1.0:
            # Create a black hole instead of particles
            
            black_hole = Blackhole(collision_pos, 1, time_speed = time_speed)
            particles = np.empty() 
            return particles
            #return [black_hole]
         
        for i in range(0,   max_particles):
            if np.random.rand() < 0.7:
                particle_type = np.random.choice(["Photon","Pion", "Muon", "Squi"])
            else:
                particle_type = np.random.choice(["Tau", "Gluon", "Quark", "HiggsBoson", "WBoson"], p=[0.3, 0.3, 0.3, 0.05, 0.05])

            angle_xy = np.random.uniform(0, 2 * np.pi)
            angle_z = np.random.uniform(0, np.pi)
            speed = np.random.uniform(low = 0.2, high = 1.5, size = 3) #Do this for 3d array and initialise all directions to be 0,0,0

            #Remove this

            #particle_x = np.cos(angle_xy) * np.sin(angle_z) * speed
            
            #particle_y = np.sin(angle_xy) * np.sin(angle_z) * speed
            #particle_z = np.cos(angle_z) * speed


            match particle_type:
                case "Photon":
                    particle = Photon(collision_pos, speed,time_speed = time_speed)
                case "Muon":
                    particle = Muon(collision_pos, speed,time_speed = time_speed)
                case "Tau":
                    particle = Tau(collision_pos, speed,time_speed = time_speed)
                case "Gluon":
                    particle = Gluon(collision_pos, speed,time_speed = time_speed)
                case "Pion": 
                    particle = Pion(collision_pos, speed,time_speed = time_speed)
                case "Squi":            
                    particle = Squi(collision_pos, speed, time_speed= time_speed)
                case "HiggsBoson":
                    particle = HiggsBoson(collision_pos, speed, time_speed= time_speed)
                case "WBoson":
                    particle = WBoson(collision_pos, speed, time_speed= time_speed)

                case _: 
                    quark_masses = {
                    'D': 4.9e6,  # Down quark mass in eV/c^2 (using the average of the range)
                    'C': 1.270e9,  # Charm quark mass in eV/c^2
                    'S': 1.01e8,  # Strange quark mass in eV/c^2
                    }

                    quark_types = ['D', 'C', 'S']
                    quark_weights = [quark_masses[q] for q in quark_types]
                    total_weight = sum(quark_weights)
                    quark_probs = [w / total_weight for w in quark_weights]

                    quark_type = np.random.choice(quark_types, p=quark_probs)
                    particle = Quark(collision_pos, speed, quark_type=quark_type, time_speed=time_speed)
                
            particles[i] = particle.to_np()
                

        flash_manager.add_flash(
            position= collision_pos,
            size=2,
            brightness=10,
            duration=3
        )

        return particles
        
    @staticmethod
    def build_particles_array(number_of_particles, particle_dtype):
            np_number_of_particles = np.int64(number_of_particles)

            particles = np.empty(np_number_of_particles, dtype=particle_dtype)

            return particles



    def generate_educational_particles(self,total_energy_eV, total_energy_MeV, total_energy_GeV,collision_pos, flash_manager, time_speed):
        particle_dtype = Particle.get_np_type(100 * time_speed) 

        

        def generate_directions(num_particles):
            flash_manager.add_flash(position=collision_pos, size=0.2, brightness=1.0, duration=2)
            directions = []
            total_vector = np.array([0.0, 0.0, 0.0])

            for _ in range(num_particles - 1):
                # Generate a random 3D unit vector
                phi = np.random.uniform(0, 2 * np.pi)*0.5
                theta = np.random.uniform(0,  np.pi)*0.5
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

        
        def get_particles_array_from_directions(directions, cls, time_speed, collision_pos, speed):
            particles = ParticleGenerator.build_particles_array(len(directions), particle_dtype)
            for i, direction in enumerate(directions):
                particle = cls(collision_pos, direction*speed, time_speed=time_speed).to_np()
                particles[i] = particle
            return particles
       

        if total_energy_MeV<210: # Photons
            
            
            flash_manager.add_flash(position=collision_pos, size=0.2, brightness=1.0, duration=2)
            # Any number of opposite photons can be created, conserving momentum
            choice = np.random.choice([2, 3, 4, 5], p=[0.53, 0.32, 0.11, 0.04])
            
            
            result_text = f"The resultant energy wasn't enough to create a new particle\nand {choice} photons were emitted."
            directions = generate_directions(choice)
            
            particle_speed = 1
            particles = get_particles_array_from_directions(directions, Photon, time_speed, collision_pos, particle_speed)



        elif total_energy_GeV<3.4 and total_energy_MeV>210:#Muons

            result_text = "The rest and kinetic energy of the particle was enough to\nproduce two Muons"
            directions = generate_directions(2)# <- for the two resulting muons 

            muon_m = 1.883531627e-28
            rest_energy_eV_muon =  muon_m * (Constants.c.value**2) / (1.602176634e-19)
            kinetic_energy_per_muon = (total_energy_eV - 2 * rest_energy_eV_muon) / 2

            
            v = Constants.c.value * np.sqrt(1 - (1 / ((kinetic_energy_per_muon / (rest_energy_eV_muon)) + 1))**2)
            particle_speed = v/Constants.c.value
            flash_manager.add_flash(position = collision_pos, size=0.5, brightness=10*particle_speed, duration=2)

            particles = get_particles_array_from_directions(directions, Muon, time_speed, collision_pos, particle_speed)
            


        


        elif total_energy_GeV>=3.4 and total_energy_GeV<9.4: #Tau
            result_text = "The rest and kinetic energy of the particle resulted in\ntwo Tau particles"
            directions = generate_directions(2)
            
            tau_m = 3.167e-27
            rest_energy_eV_tau =  tau_m * (Constants.c.value**2) / (1.602176634e-19)
            kinetic_energy_per_tau = (total_energy_eV - 2 * rest_energy_eV_tau) / 2
            v = Constants.c.value * np.sqrt(1 - (1 / ((kinetic_energy_per_tau / (rest_energy_eV_tau)) + 1))**2)
            particle_speed = v/Constants.c.value
            flash_manager.add_flash(position=collision_pos, size=0.5, brightness=10*particle_speed, duration=2)

            particles = get_particles_array_from_directions(directions, Tau, time_speed, collision_pos, particle_speed) 


        elif total_energy_GeV>=9.4 and total_energy_GeV<30: #gamma gluon gluon
            result_text = "The rest and kinetic energy of the particle produced\na quantum gamma particle, decaying into three\nhigh energy gluons"
            directions = generate_directions(3)
            particle_speed = 1.3 # C -> the gluons are incredibly high powered (I modified it to make it cooler and make it slightly more explosive and fast)
            flash_manager.add_flash(position=collision_pos, size=2, brightness=10*particle_speed, duration=3)

            particles = get_particles_array_from_directions(directions, particle_speed, Gluon, time_speed, particle_speed)
            

        elif total_energy_GeV >= 30 and total_energy_GeV < 80:  # quark quark gluon
            particles = ParticleGenerator.build_particles_array(3, particle_dtype)

            directions = generate_directions(3)
            particle = Gluon(collision_pos, directions[2], time_speed=time_speed)
            particles[0] = particle

            quark_masses = {
                'D': 4.9e6,  # Down quark mass in eV/c^2 (using the average of the range)
                'C': 1.270e9,  # Charm quark mass in eV/c^2
                'S': 1.01e8,  # Strange quark mass in eV/c^2
                # 'T': 1.72e11  # Top quark mass in eV/c^2  WE EXCLUDE THIS ONE BECAUSE THE MASS IS TOO HIGH
            }

            quark_names = {
                'D': "Down",
                'C': "Charm",
                'S': "Strange",
            }

            quark_types = ['D', 'C', 'S']

            chosen_quarks = np.random.choice(quark_types, size=2, replace=False)

            if chosen_quarks[0] != chosen_quarks[1]:
                result_text = f"The rest and kinetic energy of the particle was enough\nto produce a gluon and two Quarks, {quark_names[chosen_quarks[0]]} and {quark_names[chosen_quarks[1]]}"
            else:
                result_text = f"The rest and kinetic energy of the particle was enough\nto produce two {quark_names[chosen_quarks[0]]} Quarks and a gluon"

            total_quarks_energy_eV = total_energy_eV * 0.9  # Allocate 90% of the total energy to the quarks
            #gluon_energy_eV = total_energy_eV - total_quarks_energy_eV  # Allocate the remaining energy to the gluon

            for i, quark_type in enumerate(chosen_quarks):
                quark_mass = quark_masses[quark_type]
                rest_energy_eV_quark = quark_mass

                quark_total_energy_eV = total_quarks_energy_eV / 2

                kinetic_energy_per_quark = quark_total_energy_eV - rest_energy_eV_quark

                v = Constants.c.value * np.sqrt(1 - (1 / ((kinetic_energy_per_quark / (rest_energy_eV_quark)) + 1))**2)
                speed = v / Constants.c.value


                particle = Quark(collision_pos, directions*speed, quark_type=quark_type, time_speed=time_speed)
                particles[i+1] = particle # Forgive me, the quark case is cursed.

            flash_manager.add_flash(
                position=collision_pos,
                size=0.5,
                brightness=5,
                duration=2
            )
    

        #http://www.quantumdiaries.org/2010/05/10/the-z-boson-and-resonances/
        elif total_energy_GeV>=80 and total_energy_GeV<124: #Z Boson -> produces two muons

            directions = generate_directions(2)# <- for the two resulting muons 
            result_text = f"The rest and kinetic energy of the particle was enough\nto produce the Z Boson however, due to its quantum\nnature it decayed instantly into 2 Muons"
            muon_m = 1.883531627e-28
            rest_energy_eV_muon =  muon_m * (Constants.c.value**2) / (1.602176634e-19)
            kinetic_energy_per_muon = (total_energy_eV - 2 * rest_energy_eV_muon) / 2

            
            v = Constants.c.value * np.sqrt(1 - (1 / ((kinetic_energy_per_muon / (rest_energy_eV_muon)) + 1))**2)
            particle_speed = v/Constants.c.value
            flash_manager.add_flash(position=collision_pos, size=0.5, brightness=10*particle_speed, duration=2)


            particles = get_particles_array_from_directions(directions, Muon, time_speed, collision_pos,particle_speed)


            

        elif total_energy_GeV>=124 and total_energy_GeV< 160: # Higgs Boson
            
            

            
            choice = np.random.choice([2, 3, 4, 5, 6], p=[0.4, 0.3, 0.15, 0.1,0.05])
            result_text = f"The rest and kinetic energy of the particle was enough\nto produce the Higgs Boson however, due to its quantum\nnature it decayed instantly into {choice} photons "
            directions = generate_directions(choice)


            particle_speed = 1
            
            particles = get_particles_array_from_directions(directions, Photon, time_speed, collision_pos, particle_speed)

            flash_manager.add_flash(position=collision_pos, size=0.5, brightness=10*particle_speed, duration=3)

        elif total_energy_GeV>=160 and total_energy_GeV< 200: #W+ Boson
            directions = generate_directions(2)
            #wmass = 1e-25
            #rest_energy_eV_w =  wmass * (Constants.c.value**2) / (1.602176634e-19)
            rest_energy_eV_boson = 80e9
            kinetic_energy_per_boson = (total_energy_eV - 2 * rest_energy_eV_boson) / 2

            
            v = Constants.c.value * np.sqrt(1 - (1 / ((kinetic_energy_per_boson / (rest_energy_eV_boson)) + 1))**2)
            particle_speed = v/Constants.c.value
            flash_manager.add_flash(position = collision_pos, size=0.5, brightness=10*particle_speed, duration=2)

            particles = get_particles_array_from_directions(directions, WBoson, time_speed, collision_pos, particle_speed)

            result_text = "The rest and kinetic energy of the particles\ncolliding produced two W+ Bosons"
            
            

        else:

            flash_manager.add_flash(position=collision_pos, size=10, brightness=10, duration=4)
            result_text = "The rest and kinetic energy of the particle is\nmore than the standard model predicts."
            particles = np.empty() 
            
        return particles,result_text
    
    
