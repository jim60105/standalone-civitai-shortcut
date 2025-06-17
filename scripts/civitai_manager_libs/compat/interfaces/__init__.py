"""
Abstract interfaces for Civitai Shortcut compatibility layer.

This module defines the core interfaces that enable the application to run
in both AUTOMATIC1111 WebUI mode and standalone mode.
"""

from .ipath_manager import IPathManager
from .iconfig_manager import IConfigManager
from .imetadata_processor import IMetadataProcessor
from .iui_bridge import IUIBridge
from .isampler_provider import ISamplerProvider
from .iparameter_processor import IParameterProcessor

__all__ = [
    "IPathManager",
    "IConfigManager",
    "IMetadataProcessor",
    "IUIBridge",
    "ISamplerProvider",
    "IParameterProcessor",
]
