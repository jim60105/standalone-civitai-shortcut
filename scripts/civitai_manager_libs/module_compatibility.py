"""
Module Compatibility Initialization

This module provides initialization functions to set up compatibility layer
for all modules that need it.
"""

import sys
from . import setting
from .logging_config import get_logger

logger = get_logger(__name__)


def initialize_compatibility_layer(compat_layer):
    """
    Initialize compatibility layer for all modules.

    Args:
        compat_layer: The compatibility layer instance
    """
    # Set compatibility layer for all modules
    setting.set_compatibility_layer(compat_layer)

    # Set compatibility layer for action modules
    modules_to_inject = [
        'scripts.civitai_manager_libs.setting',
        'scripts.civitai_manager_libs.setting_action',
        'scripts.civitai_manager_libs.civitai_shortcut_action',
        'scripts.civitai_manager_libs.civitai_gallery_action',
        'scripts.civitai_manager_libs.model_action',
        'scripts.civitai_manager_libs.ishortcut_action',
        'scripts.civitai_manager_libs.prompt_ui',
    ]

    for module_name in modules_to_inject:
        if module_name in sys.modules:
            module = sys.modules[module_name]
            if hasattr(module, 'set_compatibility_layer'):
                module.set_compatibility_layer(compat_layer)
            # Also set as global variable for modules that expect it
            setattr(module, '_compat_layer', compat_layer)

    # Initialize settings with compatibility layer; ignore errors to support mock layers
    try:
        setting.init()
    except Exception:
        pass

    logger.info("Compatibility layer initialized for all modules")
