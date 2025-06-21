#!/bin/bash

# Civitai Shortcut Startup Script for Linux/macOS

set -e

# Color definitions
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Civitai Shortcut - Standalone Mode${NC}"
echo "=================================="

# Check if uv is available
UV_AVAILABLE=false
if command -v uv &> /dev/null; then
    UV_AVAILABLE=true
    echo -e "${GREEN}Found uv - using modern Python package management${NC}"
else
    echo -e "${YELLOW}uv not found - falling back to traditional pip/venv${NC}"
fi

# Use uv for everything if available
if [[ "$UV_AVAILABLE" == true ]]; then
    # Check Python version with uv
    if ! uv python list &> /dev/null; then
        echo -e "${RED}Error: No Python installation found by uv${NC}"
        echo "Please install Python 3.8 or newer"
        exit 1
    fi
    
    # Get Python version
    PYTHON_VERSION=$(uv run python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null || echo "unknown")
    if [[ "$PYTHON_VERSION" != "unknown" ]]; then
        echo -e "${GREEN}Found Python ${PYTHON_VERSION}${NC}"
    fi
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Start the application using uv run
    echo -e "${GREEN}Starting Civitai Shortcut with uv...${NC}"
    echo "Use Ctrl+C to stop the application"
    echo ""
    
    # uv run will automatically handle dependencies from requirements.txt
    # Pass all command line arguments to the Python script
    exec uv run main.py "$@"
    
else
    # Fallback to traditional pip/venv approach
    # Check Python environment
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}Error: Python 3 not found${NC}"
        echo "Please install Python 3.8 or newer"
        exit 1
    fi

    # Get Python version
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    echo -e "${GREEN}Found Python ${PYTHON_VERSION}${NC}"

    # Check if we're in a virtual environment
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo -e "${GREEN}Using virtual environment: ${VIRTUAL_ENV}${NC}"
    else
        echo -e "${YELLOW}Not in a virtual environment${NC}"
        echo "Creating virtual environment..."
        
        # Create virtual environment
        echo -e "${GREEN}Using python3 to create virtual environment...${NC}"
        python3 -m venv venv
        
        # Activate virtual environment
        source venv/bin/activate
        
        echo -e "${GREEN}Virtual environment created and activated: $(pwd)/venv${NC}"
    fi

    # Check dependencies
    echo -e "${YELLOW}Checking dependencies...${NC}"

    # Check if gradio is installed
    if ! python3 -c "import gradio" &> /dev/null; then
        echo -e "${YELLOW}Installing dependencies...${NC}"
        echo -e "${GREEN}Using pip to install dependencies...${NC}"
        python3 -m pip install -r requirements.txt
        echo -e "${GREEN}Dependencies installed successfully!${NC}"
    else
        echo -e "${GREEN}Dependencies already installed${NC}"
    fi

    # Create logs directory if it doesn't exist
    mkdir -p logs

    # Start the application
    echo -e "${GREEN}Starting Civitai Shortcut...${NC}"
    echo "Use Ctrl+C to stop the application"
    echo ""

    # Pass all command line arguments to the Python script
    exec python3 main.py "$@"
fi

echo -e "${BLUE}Application stopped${NC}"
