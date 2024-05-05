@echo off
echo Running Particle Accelerator Simulation...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Please install Python and try again.
    pause
    exit /b
)

REM Create a virtual environment (optional but recommended)
if not exist venv (
    echo Creating a virtual environment...
    python -m venv venv
)

REM Activate the virtual environment
echo Activating the virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r ./requirements.txt
pip3 install -r ./requirements.txt

REM Run the simulation
echo Starting the simulation...
python simulation.py
python3 simulation.py


REM Deactivate the virtual environment
echo Deactivating the virtual environment...
call venv\Scripts\deactivate.bat

echo Simulation completed.
pause
