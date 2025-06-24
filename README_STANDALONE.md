# Civitai Shortcut - Standalone Mode

This document describes how to run Civitai Shortcut in standalone mode, without requiring the AUTOMATIC1111 WebUI environment.

## Quick Start

### Prerequisites

- Python 3.8 or newer
- Internet connection for downloading models and dependencies

### Installation

1. **Clone or download the repository**
   ```bash
   git clone https://github.com/your-repo/civitai-shortcut.git
   cd civitai-shortcut
   ```

2. **Install dependencies** (automatic during first run)
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

#### Linux/macOS

```bash
# Make the script executable (first time only)
chmod +x start.sh

# Start the application
./start.sh

# Or with custom options
./start.sh --port 8080 --host 0.0.0.0
```

#### Windows

```batch
REM Start the application
start.bat

REM Or with custom options
start.bat --port 8080 --host 0.0.0.0
```

#### Direct Python Execution

```bash
# Basic usage
python main.py

# Custom configuration
python main.py --port 8080 --host 0.0.0.0 --share

# With custom config file
python main.py --config my_config.json

# Debug mode
python main.py --debug
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--host` | Server host address | `0.0.0.0` |
| `--port` | Server port | `7860` |
| `--share` | Create Gradio public share link | `False` |
| `--config` | Custom configuration file path | `None` |
| `--models-path` | Models storage path | `./models` |
| `--output-path` | Output files storage path | `./outputs` |
| `--debug` | Enable debug mode | `False` |
| `--quiet` | Quiet mode, reduce output | `False` |
| `--version` | Show version information | - |

## Configuration

### Default Configuration

The application creates a default configuration on first run. You can customize settings through:

1. **Web Interface**: Go to Settings > Standalone Configuration
2. **Configuration File**: Edit `config/config.json`
3. **Command Line**: Use command line options

### Configuration File Structure

```json
{
  "server": {
    "host": "0.0.0.0",
    "port": 7860,
    "share": false
  },
  "civitai": {
    "api_key": "",
    "download_path": "./models",
    "cache_enabled": true,
    "cache_size_mb": 500
  },
  "debug": {
    "enabled": false
  },
  "paths": {
    "models": "./models",
    "output": "./outputs",
    "cache": "./cache",
    "logs": "./logs"
  }
}
```

## Features

### Model Browser
- Browse and search Civitai models
- Download models directly
- Organize models by categories
- Preview model information and samples

### Prompt Recipe Manager
- Save and manage prompt templates
- Apply recipes to generation
- Share recipes with others

### Classification System
- Organize models by custom categories
- Filter models by type and purpose
- Bulk operations on model collections

### Settings Management
- Configure application behavior
- Manage API keys and paths
- Control caching and performance

## File Structure

```
civitai-shortcut/
├── main.py                 # Main application entry point
├── ui_adapter.py          # UI adapter for standalone mode
├── start.sh               # Linux/macOS startup script
├── start.bat              # Windows startup script
├── requirements.txt       # Python dependencies
├── config/
│   └── config.json       # Configuration file
├── models/               # Downloaded models
├── outputs/              # Generated outputs
├── cache/                # Cached data
├── logs/                 # Application logs
└── scripts/              # Core application code
    └── civitai_manager_libs/
        └── ...
```

## Troubleshooting

### Common Issues

1. **Python not found**
   - Make sure Python 3.8+ is installed and in your PATH
   - On Windows, you might need to use `py` instead of `python`

2. **Permission denied (Linux/macOS)**
   ```bash
   chmod +x start.sh
   ```

3. **Port already in use**
   ```bash
   python main.py --port 8080
   ```

4. **Module not found errors**
   ```bash
   pip install -r requirements.txt
   ```

### Debug Mode

Enable debug mode for detailed logging:

```bash
python main.py --debug
```

This will:
- Enable detailed logging
- Show full error tracebacks
- Log all API requests and responses

### Logs

Application logs are stored in:
- `logs/civitai_shortcut.log` - Main application log
- Console output during execution

## Performance Tips

1. **Use SSD storage** for model files
2. **Increase cache size** for better performance
3. **Use virtual environment** to avoid conflicts
4. **Close other applications** when downloading large models

## Security Notes

- The application runs a local web server
- Use `--host 0.0.0.0` only if you want external access
- Keep your Civitai API key secure
- Regular users should use `0.0.0.0` (localhost)

## Support

For issues and questions:

1. Check the logs in `logs/civitai_shortcut.log`
2. Run with `--debug` for more information
3. Check GitHub issues for similar problems
4. Create a new issue with:
   - Your operating system
   - Python version
   - Full error message
   - Steps to reproduce

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black --line-length=100 --skip-string-normalization .
flake8 .
```

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```
