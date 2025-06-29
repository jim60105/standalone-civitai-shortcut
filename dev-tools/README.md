# Deve### Quick Reference

```bash
# Show available commands
python dev-tools/dev_tools.py

# Development validation commands
python dev-tools/dev_tools.py quick       # Fast syntax check
python dev-tools/dev_tools.py validate    # Full code validation
python dev-tools/dev_tools.py types       # Type checking with mypy
python dev-tools/dev_tools.py tests       # Run test suite (summary)
python dev-tools/dev_tools.py tests-verbose  # Run tests (detailed output)
python dev-tools/dev_tools.py comprehensive  # Complete validation workflow
```ls - Civitai Shortcut

This directory contains development tools to help catch refactoring issues at coding time, preventing runtime errors and ensuring code quality.

## Getting Started

### Quick Help

To see all available commands, simply run:

```bash
python dev-tools/dev_tools.py
```

This will display the help menu with descriptions of all available commands.

### Quick Reference

```bash
# Development validation commands
python dev-tools/dev_tools.py quick       # Fast syntax check
python dev-tools/dev_tools.py validate    # Full code validation
python dev-tools/dev_tools.py types       # Type checking with mypy
python dev-tools/dev_tools.py tests       # Run test suite (summary)
python dev-tools/dev_tools.py tests-verbose  # Run tests (detailed output)
python dev-tools/dev_tools.py comprehensive  # Complete validation workflow
```

### Running Specific Tests

For targeted testing, use pytest directly:

```bash
# Run specific test file
python -m pytest tests/test_http_client.py -v

# Run specific test class
python -m pytest tests/test_civitai.py::TestCivitai -v

# Run specific test method
python -m pytest tests/test_civitai.py::test_get_model_info_success -v

# Run tests matching pattern
python -m pytest tests/ -k "test_http" -v

# Run tests with coverage
python -m pytest tests/ --cov=scripts/civitai_manager_libs
```

### 1. Code Validator (`validate_code.py`)

Comprehensive code validation tool that checks:
- **Syntax errors**: Invalid Python syntax
- **Import validation**: Missing or broken imports
- **Undefined variables**: Variables that may not be defined in scope
- **Code style**: Flake8 linting issues

**Usage:**
```bash
python dev-tools/validate_code.py
```

### 2. Development Tools Suite (`dev_tools.py`)

Command-line interface for various development tasks:

```bash
# Run comprehensive validation
python dev-tools/dev_tools.py validate

# Quick syntax check only
python dev-tools/dev_tools.py quick

# Type checking (requires mypy)
python dev-tools/dev_tools.py types

# Run test suite (summary output)
python dev-tools/dev_tools.py tests

# Run test suite (verbose output)
python dev-tools/dev_tools.py tests-verbose

# Run comprehensive development validation
python dev-tools/dev_tools.py comprehensive
```

### 3. Development Tools Suite (`dev_tools.py`)

Command-line interface for various development tasks with comprehensive validation capabilities.

## Integration with VS Code

### Setting up Tasks

Add these tasks to your `.vscode/tasks.json`:

```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Validate Code",
            "type": "shell",
            "command": "python",
            "args": ["dev-tools/validate_code.py"],
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "Quick Check",
            "type": "shell",
            "command": "python",
            "args": ["dev-tools/dev_tools.py", "quick"],
            "group": "test"
        }
    ]
}
```

### Keyboard Shortcuts

Add to `.vscode/keybindings.json`:

```json
[
    {
        "key": "ctrl+shift+v",
        "command": "workbench.action.tasks.runTask",
        "args": "Validate Code"
    }
]
```

## Error Detection Capabilities

The validation tools can catch these types of issues:

### 1. Import Errors
```python
# This will be caught:
from non_existent_module import something
import missing_package
```

### 2. Undefined Variables
```python
# This will be caught:
def my_function():
    return undefined_variable  # Error: variable not defined
```

### 3. Global Instance Issues
```python
# This will be caught:
shortcutcollectionmanager.method()  # Should be ishortcut.shortcutcollectionmanager.method()
```

### 4. Syntax Errors
```python
# This will be caught:
def broken_function(
    # Missing closing parenthesis
```

## Recommended Development Workflow

1. **Before making changes**:
   ```bash
   python dev-tools/dev_tools.py quick
   ```

2. **During development** (VS Code):
   - Press `Ctrl+Shift+V` to validate
   - Or use Command Palette: "Tasks: Run Task" → "Validate Code"

3. **Before important changes**:
   - Run comprehensive validation: `python dev-tools/dev_tools.py comprehensive`

## Configuration

### Flake8 Configuration

The project uses `.flake8` configuration file:

```ini
[flake8]
max-line-length = 100
ignore = E203, W503, F401
exclude = 
    venv/,
    env/,
    __pycache__,
    .git/,
    htmlcov/,
    node_modules/
```

### Files Excluded from Validation

- Virtual environments (`venv/`, `env/`)
- Cache directories (`__pycache__`, `htmlcov/`)
- Git directories (`.git/`)
- Node modules (`node_modules/`)

## Troubleshooting

### Common Issues

1. **"Module not found" errors**: Install missing dependencies
   ```bash
   pip install -r requirements.txt
   ```

2. **Flake8 not found**: Install flake8
   ```bash
   pip install flake8
   ```

3. **Permission errors**: Make sure you have write permissions to the dev-tools directory

### Getting Help

Run any tool with `--help` for more information:
```bash
python dev-tools/dev_tools.py --help
```

## Contributing

When adding new validation checks:

1. Add the check to `validate_code.py`
2. Update this README
3. Test with various code scenarios
4. Ensure it doesn't produce false positives

## Benefits

Using these tools helps:
- **Catch errors early**: Before they reach production or cause runtime issues
- **Maintain code quality**: Consistent coding standards
- **Speed up development**: No more runtime debugging of simple errors
- **Improve team collaboration**: Everyone uses the same validation standards
- **Reduce debugging time**: Catch issues locally during development
