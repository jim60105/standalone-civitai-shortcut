"""
Settings Package

This package contains the refactored settings management modules split from the
original setting.py file for better organization and maintainability.

Modules:
- config_manager: Core configuration management
- path_manager: Path management utilities
- defaults: Default values and constants
- migration_manager: Configuration migration logic
- validation_manager: Configuration validation
"""

# Import main classes for convenience
from .config_manager import ConfigManager
from .path_manager import PathManager
from .defaults import Defaults
from .migration_manager import MigrationManager
from .validation_manager import ValidationManager

__all__ = ['ConfigManager', 'PathManager', 'Defaults', 'MigrationManager', 'ValidationManager']
