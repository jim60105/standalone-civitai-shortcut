"""
Module Compatibility Initialization

This module provides initialization functions to set up compatibility layer
for all modules that need it.
"""

from . import setting
from . import util
from . import civitai_shortcut_action
from . import model_action
from . import recipe_action
from . import ishortcut_action
from . import civitai_gallery_action
from . import setting_action
from . import prompt_ui


def initialize_compatibility_layer(compat_layer):
    """
    Initialize compatibility layer for all modules.

    Args:
        compat_layer: The compatibility layer instance
    """
    # Set compatibility layer for all modules
    setting.set_compatibility_layer(compat_layer)

    # Set compatibility layer for action modules
    civitai_shortcut_action.set_compatibility_layer(compat_layer)
    model_action.set_compatibility_layer(compat_layer)
    recipe_action.set_compatibility_layer(compat_layer)
    ishortcut_action.set_compatibility_layer(compat_layer)
    civitai_gallery_action.set_compatibility_layer(compat_layer)
    setting_action.set_compatibility_layer(compat_layer)
    prompt_ui.set_compatibility_layer(compat_layer)

    # Initialize settings with compatibility layer; ignore errors to support mock layers
    try:
        setting.init()
    except Exception:
        pass

    util.printD("Compatibility layer initialized for all modules")


def get_compatibility_status():
    """
    Get the status of compatibility layer initialization.

    Returns:
        dict: Status information about compatibility layer
    """
    compat_layer = setting.get_compatibility_layer()

    if not compat_layer:
        return {"status": "not_initialized", "mode": "unknown", "webui_available": False}

    return {
        "status": "initialized",
        "mode": compat_layer.mode,
        "webui_available": compat_layer.is_webui_mode(),
        "standalone_mode": compat_layer.is_standalone_mode(),
    }
