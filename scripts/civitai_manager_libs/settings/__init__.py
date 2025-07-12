"""Setting package."""

from .config_manager import ConfigManager
from .constants import *  # noqa: F403,F401
from .initialization import set_compatibility_layer, set_NSFW, save_NSFW
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
from .setting_persistence import SettingPersistence
from .setting_validation import SettingValidator

# Global configuration manager for backward compatibility
config_manager = ConfigManager()

# Provide default ui_typenames for compatibility with legacy code/tests
UI_TYPENAMES = getattr(config_manager, 'ui_typenames', None)
if UI_TYPENAMES is None:
    from .constants import UI_TYPENAMES as DEFAULT_UI_TYPENAMES

    UI_TYPENAMES = DEFAULT_UI_TYPENAMES.copy()
    config_manager.settings['ui_typenames'] = UI_TYPENAMES


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
    # Special handling for civitai/usergal/download_information_tab
    if name == 'civitai_information_tab':
        from .constants import DEFAULT_CIVITAI_INFORMATION_TAB

        return DEFAULT_CIVITAI_INFORMATION_TAB
    if name == 'usergal_information_tab':
        from .constants import DEFAULT_USERGAL_INFORMATION_TAB

        return DEFAULT_USERGAL_INFORMATION_TAB
    if name == 'download_information_tab':
        from .constants import DEFAULT_DOWNLOAD_INFORMATION_TAB

        return DEFAULT_DOWNLOAD_INFORMATION_TAB

    # First try to get using config_manager.get_setting which handles nested lookups
    value = config_manager.get_setting(name)  # type: ignore
    if value is not None:
        return value

    # Try to get from defaults
    default_value = SettingCategories.get_default_value(name)
    if default_value is not None:
        return default_value

    # Special handling for some commonly accessed attributes
    if name == 'Extensions_Version':
        return config_manager.get_setting('Extensions_Version', '1.0.0')  # type: ignore

    # Special handling for path-related properties
    if name == 'no_card_preview_image':
        return get_no_card_preview_image()

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


def init(*args, **kwargs):
    from .path_manager import extension_base as pm_extension_base
    from .initialization import init as real_init

    real_init(*args, **kwargs)
    global extension_base
    extension_base = pm_extension_base


__all__ = [
    "ConfigManager",
    "SettingCategories",
    "SettingValidator",
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
