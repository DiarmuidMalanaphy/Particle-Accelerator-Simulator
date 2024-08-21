@echo off
echo Running Particle Accelerator Simulation...

:: Get the local Python executable path
for /f "delims=" %%a in ('py -c "import sys; print(sys.executable)"') do set "homePath=%%a"

:: Update the venv configuration
echo home = %homePath% > .\code\venv\pyvenv.cfg
echo include-system-site-packages = false >> .\code\venv\pyvenv.cfg
echo version = 3.12.5 >> .\code\venv\pyvenv.cfg
echo executable = %homePath% >> .\code\venv\pyvenv.cfg
echo command = "%homePath%" -m venv C:\Users\diarmuid\Particle-Accelerator-Simulator\code\venv >> .\code\venv\pyvenv.cfg

:: Run the simulation script using the updated virtual environment
call "%homePath%" -m venv .\code\venv
call .\code\venv\Scripts\python.exe .\code\simulation.py
