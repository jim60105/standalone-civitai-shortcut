"""Compatibility Layer Package.

Provides unified access to functionality across WebUI and standalone execution modes.
"""

from .environment_detector import EnvironmentDetector, EnvironmentType
from .compat_layer import (
    CompatibilityLayer,
)

__all__ = [
    "EnvironmentDetector",
    "EnvironmentType",
    "CompatibilityLayer",
]
