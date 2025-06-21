@echo off
chcp 65001 > nul

echo Civitai Shortcut - Standalone Mode
echo ==================================

REM Check if uv is available
set UV_AVAILABLE=false
uv --version >nul 2>&1
if not errorlevel 1 (
    set UV_AVAILABLE=true
    echo Found uv - using modern Python package management
) else (
    echo uv not found - falling back to traditional pip/venv
)

REM Use uv for everything if available
if "%UV_AVAILABLE%"=="true" (
    REM Check Python version with uv
    uv python list >nul 2>&1
    if errorlevel 1 (
        echo Error: No Python installation found by uv
        echo Please install Python 3.8 or newer
        pause
        exit /b 1
    )
    
    REM Get Python version
    for /f "tokens=*" %%i in ('uv run python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2^>nul') do set PYTHON_VERSION=%%i
    if not "%PYTHON_VERSION%"=="" (
        echo Found Python %PYTHON_VERSION%
    )
    
    REM Create logs directory if it doesn't exist
    if not exist "logs" mkdir logs
    
    REM Start the application using uv run
    echo Starting Civitai Shortcut with uv...
    echo Use Ctrl+C to stop the application
    echo.
    
    REM uv run will automatically handle dependencies from requirements.txt
    REM Pass all command line arguments to the Python script
    uv run main.py %*
    
) else (
    REM Fallback to traditional pip/venv approach
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
        echo Creating virtual environment...
        
        REM Create virtual environment
        echo Using python to create virtual environment...
        python -m venv venv
        
        REM Activate virtual environment
        call venv\Scripts\activate.bat
        
        echo Virtual environment created and activated: %CD%\venv
    )

    REM Check dependencies
    echo Checking dependencies...

    REM Check if gradio is installed
    python -c "import gradio" >nul 2>&1
    if errorlevel 1 (
        echo Installing dependencies...
        echo Using pip to install dependencies...
        python -m pip install -r requirements.txt
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
)

echo Application stopped
pause
