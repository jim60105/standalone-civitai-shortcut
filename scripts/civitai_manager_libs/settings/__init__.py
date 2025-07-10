"""Setting package."""

from .config_manager import ConfigManager
from .constants import *  # noqa: F403,F401
from .initialization import init, set_compatibility_layer, set_NSFW, save_NSFW
from .model_utils import (
    generate_type_basefolder,
    generate_version_foldername,
    get_ui_typename,
    get_imagefn_and_shortcutid_from_recipe_image,
    set_imagefn_and_shortcutid_for_recipe_image,
    get_modelid_from_shortcutname,
    set_shortcutname,
)
from .path_manager import (
    get_extension_base,
    get_model_folders,
    get_image_url_to_shortcut_file,
    get_image_url_to_gallery_file,
    get_no_card_preview_image,
    get_nsfw_disable_image,
    shortcut,
    shortcut_setting,
    shortcut_classification,
    shortcut_civitai_internet_shortcut_url,
    shortcut_recipe,
    shortcut_thumbnail_folder,
    shortcut_recipe_folder,
    shortcut_info_folder,
    shortcut_gallery_folder,
    extension_base,
    root_path,
    model_folders,
)
from .setting_categories import SettingCategories
from .setting_defaults import SettingDefaults
from .setting_persistence import SettingPersistence
from .setting_validation import SettingValidator

# Global configuration manager for backward compatibility
config_manager = ConfigManager()


# Proxy functions for backward compatibility
def get_setting(key: str, default=None):
    """Proxy for ConfigManager.get_setting."""
    return config_manager.get_setting(key, default)


def set_setting(key: str, value):
    """Proxy for ConfigManager.set_setting."""
    return config_manager.set_setting(key, value)


def save_setting(setting_dict: dict):
    """Proxy for ConfigManager.save_settings."""
    return config_manager.save_settings(setting_dict)


def load():
    """Proxy for ConfigManager.load_settings."""
    return config_manager.load_settings()


def __getattr__(name):
    """Provide dynamic access to configuration settings for backward compatibility."""
    # First try to get from config_manager settings
    if hasattr(config_manager, 'settings') and name in config_manager.settings:
        return config_manager.settings[name]

    # Try to get from defaults
    default_value = SettingDefaults.get_default_value(name)
    if default_value is not None:
        return default_value

    # Special handling for some commonly accessed attributes
    if name == 'Extensions_Version':
        return config_manager.get_setting('Extensions_Version', '1.0.0')

    # If nothing found, try to get from config_manager
    value = config_manager.get_setting(name)
    if value is not None:
        return value

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


__all__ = [
    "ConfigManager",
    "SettingCategories",
    "SettingValidator",
    "SettingDefaults",
    "SettingPersistence",
    "config_manager",
    "get_setting",
    "set_setting",
    "save_setting",
    "load",
    "init",
    "set_compatibility_layer",
    "set_NSFW",
    "save_NSFW",
    "generate_type_basefolder",
    "generate_version_foldername",
    "get_ui_typename",
    "get_imagefn_and_shortcutid_from_recipe_image",
    "set_imagefn_and_shortcutid_for_recipe_image",
    "get_modelid_from_shortcutname",
    "set_shortcutname",
    "get_extension_base",
    "get_model_folders",
    "get_image_url_to_shortcut_file",
    "get_image_url_to_gallery_file",
    "get_no_card_preview_image",
    "get_nsfw_disable_image",
    "shortcut",
    "shortcut_setting",
    "shortcut_classification",
    "shortcut_civitai_internet_shortcut_url",
    "shortcut_recipe",
    "shortcut_thumbnail_folder",
    "shortcut_recipe_folder",
    "shortcut_info_folder",
    "shortcut_gallery_folder",
    "extension_base",
    "root_path",
    "model_folders",
]
