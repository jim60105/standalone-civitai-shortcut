@echo off
chcp 65001 > nul

echo Civitai Shortcut - Standalone Mode
echo ==================================

REM Check Python environment
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    echo Please install Python 3.8 or newer
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Get Python version
for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

REM Check if we're in a virtual environment
if defined VIRTUAL_ENV (
    echo Using virtual environment: %VIRTUAL_ENV%
) else (
    echo Not in a virtual environment
    echo It's recommended to use a virtual environment
)

REM Check dependencies
echo Checking dependencies...

REM Check if requirements.txt exists
if not exist "requirements.txt" (
    echo Creating basic requirements.txt...
    (
        echo gradio^>=3.41.2
        echo requests^>=2.25.0
        echo Pillow^>=8.0.0
        echo numpy^>=1.20.0
        echo packaging^>=20.0
    ) > requirements.txt
)

REM Check if gradio is installed
python -c "import gradio" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    
    REM Try to use uv if available, otherwise fall back to pip
    uv --version >nul 2>&1
    if not errorlevel 1 (
        echo Using uv for faster installation...
        uv pip install -r requirements.txt
    ) else (
        echo Using pip to install dependencies...
        python -m pip install -r requirements.txt --user
    )
    
    echo Dependencies installed successfully!
) else (
    echo Dependencies already installed
)

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Start the application
echo Starting Civitai Shortcut...
echo Use Ctrl+C to stop the application
echo.

REM Pass all command line arguments to the Python script
python main.py %*

echo Application stopped
pause
