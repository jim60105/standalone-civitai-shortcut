"""
Compatibility Layer Package

Provides unified access to functionality across WebUI and standalone execution modes.
"""

from .environment_detector import EnvironmentDetector, EnvironmentType
from .compat_layer import (
    CompatibilityLayer,
    get_compatibility_layer,
    reset_compatibility_layer,
)

__all__ = [
    "EnvironmentDetector",
    "EnvironmentType",
    "CompatibilityLayer",
    "get_compatibility_layer",
    "reset_compatibility_layer",
]
