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
    
    # Try to use uv if available, otherwise fall back to pip
    if command -v uv &> /dev/null; then
        echo -e "${GREEN}Using uv for faster installation...${NC}"
        # uv pip install works in virtual environments without --user
        uv pip install -r requirements.txt
    else
        echo -e "${GREEN}Using pip to install dependencies...${NC}"
        # Remove --user flag since we're now guaranteed to be in a venv
        python3 -m pip install -r requirements.txt
    fi
    
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
python3 main.py "$@"

echo -e "${BLUE}Application stopped${NC}"
