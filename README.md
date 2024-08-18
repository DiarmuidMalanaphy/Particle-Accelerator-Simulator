# Particle Accelerator Simulation

## Overview

This project is a 3D simulation of a particle accelerator that allows users to explore the interaction between electrons and positrons colliding at relativistic speeds.

## Key Features

- **3D Simulation**: Utilizes PyOpenGL to efficiently render dynamic 3D objects within Python, creating visually appealing and interactive experiences.
- **Scientific Accuracy**: Built on research into electron and positron collisions, ensuring that particle interactions and the resulting particles are modeled with a high degree of scientific precision.
- **Real-World Accelerator Simulations**: Includes simulations of velocities achieved by renowned particle accelerators, such as the Large Hadron Collider (LHC) and the early CERN Synchrotron.

## Modes

The project provides three separate stages for the user:

### 1. Control Panel

- Modify simulation parameters, including velocities and collision settings.
- Includes preset velocities for simulating the LHC, the early CERN Synchrotron, and the velocities needed to create fundamental particles.
- ![Control Panel](code/images/control_panel.png)

### 2. Educational Mode

- Provides descriptions of the kinetic energy of input particles and the resultant particles.
- Designed to illustrate the exponential growth of kinetic energy at relativistic speeds.
- ![Educational Mode](code/images/Education_mode.png)

### 3. Experimental Mode

- Focuses on visually engaging particle interactions and behaviors.
- Allows users to explore a 3D environment in a more relaxed and exploratory manner.
- ![Experimental Mode](code/images/fun_mode.png)

## Practical Requirements

- Python 3.x
- On Windows, if you encounter issues running the `run.bat` file, you may need to install C++ tools (though this shouldn't be necessary).

## Installation and Setup

1. Clone the repository to your local machine using the command:
    ```bash
    git clone https://github.com/DiarmuidMalanaphy/Particle-Accelerator-Simulator/
    ```
2. Ensure Python is installed on your system.

### On Windows

1. Run the `.bat` file to automatically start the application.

### On Linux or macOS

Unfortunately, due to a bug in Imgui, the application is currently not supported on Linux or macOS.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.


