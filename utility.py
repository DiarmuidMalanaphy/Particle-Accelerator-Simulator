import numpy as np
from enum import Enum

class Constants(Enum):
    c = 299792458

class UtilityFunctions():
    # You could make this marginally more efficient by using the combined rest mass and kinetic energy formula
    def calculate_total_energy(self,relative_particle_speed):
        #m of electron/positron  is 9.1093837 × 10-31 kilograms - for computational efficiency  9.1*10*31
        def particle_kinetic_energy(v, m):
            """
            Calculate the relativistic kinetic energy given a velocity and mass.
            - v is the velocity of the particle.
            - m is the mass of the particle.
            Returns kinetic energy in eV.
            """
            
            # Calculate the Lorentz factor
            gamma = 1 / np.sqrt(1 - (v**2 / Constants.c.value**2))

            # Calculate the relativistic kinetic energy in joules
            KE_joules = (gamma - 1) * m * Constants.c.value**2

            # Convert kinetic energy to eV
            KE_eV = KE_joules / (1.602176634e-19)
            return KE_eV

        # Assuming positron_speed and electron_speed are defined and are fractions of the speed of light (e.g., 0.99 for 99% of the speed of light)
        m = 9.1e-31  # Mass of electron/positron in kg
        
        
        unified_speed = relative_particle_speed * Constants.c.value # Unify them for efficiency

        # Calculate kinetic energy for both particles <- ASSUMING THEY'RE BOTH ELECTRONS
    
        total_kinetic_energy_eV = 2 * particle_kinetic_energy(unified_speed, m)

    
        
        #https://public-archive.web.cern.ch/en/lhc/Facts-en.html
        rest_energy_eV =  2 * m * (Constants.c.value**2) / (1.602176634e-19)

        total_energy_eV = total_kinetic_energy_eV + rest_energy_eV 

        total_energy_MeV = total_energy_eV / 10**6

        total_energy_GeV = total_energy_eV / 10**9

        #print(f"Total Kinetic Energy: {total_energy_MeV} MeV, or {total_energy_GeV} GeV")
        

        return(total_energy_eV,total_energy_MeV,total_energy_GeV)


    def calculate_mid_point_positron_electron(self,positron_pos,electron_pos):
        position=[  
                    (positron_pos[0] + electron_pos[0]) / 2,
                    (positron_pos[1] + electron_pos[1]) / 2,
                    (positron_pos[2] + electron_pos[2]) / 2
                ]
        return(position)
    
    
    