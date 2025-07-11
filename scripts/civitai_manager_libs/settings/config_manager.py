from typing import Optional

"""Configuration manager for the application."""

from ..error_handler import with_error_handling
from ..exceptions import FileOperationError
from ..logging_config import get_logger
from .setting_categories import SettingCategories
from .setting_persistence import SettingPersistence
from .setting_validation import SettingValidator

logger = get_logger(__name__)


class ConfigManager:
    """Manages application settings by coordinating different settings modules."""

    def __init__(self, config_file: Optional[str] = None):
        """Initializes the ConfigManager."""
        # Use the proper path from path_manager if no config_file is provided
        if config_file is None:
            from .path_manager import shortcut_setting

            config_file = shortcut_setting
        self.persistence = SettingPersistence(config_file)
        self.validator = SettingValidator()
        self.defaults = SettingCategories.get_all_defaults()
        self.categories = SettingCategories.get_all_categories()
        self.settings = {}

    @with_error_handling(
        fallback_value={},
        exception_types=(FileOperationError,),
        user_message="Failed to load settings, using defaults.",
    )
    def load_settings(self, reload: bool = False) -> dict:
        """Loads all settings from the persistence layer."""
        if not self.settings or reload:
            self.settings = self.persistence.load_from_file()
        return self.settings

    @with_error_handling(
        fallback_value=False,
        exception_types=(FileOperationError,),
        user_message="Failed to save settings.",
    )
    def save_settings(self, settings: Optional[dict] = None) -> bool:
        """Saves the given settings to the persistence layer."""
        logger.debug(
            "[ConfigManager.save_settings] Called with settings: %s",
            settings,
        )
        logger.debug(
            "[ConfigManager.save_settings] persistence.config_file: %s",
            self.persistence.config_file,
        )
        if settings is None:
            settings = self.settings
        return self.persistence.save_to_file(settings)

    def get_setting(self, key: str, default=None):
        """Gets a single settings value by key."""
        # Always check nested categories first (this is the correct structure)
        value = self._search_nested_setting(key)

        # If not found in nested categories, check flat values as fallback
        # (for backwards compatibility or non-categorized settings)
        if value is None:
            value = self.settings.get(key)

        # If still not found, use provided default or system default
        if value is None:
            value = default if default is not None else self.defaults.get(key)

        if key == 'config_path' and value is None:
            try:
                from scripts.civitai_manager_libs.compat.standalone_adapters import (
                    standalone_path_manager,
                )

                value = standalone_path_manager.StandalonePathManager().get_config_path()
            except Exception:
                value = None
        return value

    def _search_nested_setting(self, key: str):
        """Search for a setting key in nested category structures."""
        # Use SettingCategories for mapping logic
        category_mapping = SettingCategories.get_config_category_mapping()
        special_mappings = SettingCategories.get_special_key_mappings()

        # Check special mappings first
        if key in special_mappings:
            category, nested_key = special_mappings[key]
            category_data = self.settings.get(category)
            if isinstance(category_data, dict) and nested_key in category_data:
                return category_data[nested_key]

        # Use SettingCategories to find which logical category this key belongs to
        logical_category = SettingCategories.find_setting_category(key)
        if logical_category:
            # Map logical category to actual config file category
            config_category = category_mapping.get(logical_category)
            if config_category:
                category_data = self.settings.get(config_category)
                if isinstance(category_data, dict) and key in category_data:
                    return category_data[key]

        # Fallback: search all known categories directly
        categories_to_search = [
            'application_allow',
            'screen_style',
            'image_style',
            'NSFW_filter',
            'download_folders',
            'model_folders',
        ]

        for category in categories_to_search:
            category_data = self.settings.get(category)
            if isinstance(category_data, dict) and key in category_data:
                return category_data[key]

        return None

    def set_setting(self, key: str, value) -> bool:
        """Sets a single settings value after validation."""
        is_valid, message = self.validator.validate_setting(key, value)
        if not is_valid:
            logger.warning(f"Invalid settings for {key}: {message}")
            return False

        self.settings[key] = value
        return self.save_settings()

    def update_settings(self, settings_dict: dict) -> dict:
        """Updates multiple settings at once."""
        validated_settings = {}
        for key, value in settings_dict.items():
            is_valid, message = self.validator.validate_setting(key, value)
            if is_valid:
                validated_settings[key] = value
            else:
                logger.warning(f"Invalid settings for {key}: {message}")

        self.settings.update(validated_settings)
        self.save_settings()
        return validated_settings

    def reset_setting(self, key: str) -> bool:
        """Resets a specific settings to its default value."""
        if key in self.defaults:
            return self.set_setting(key, self.defaults[key])
        return False

    def reset_all_settings(self) -> bool:
        """Resets all settings to their default values."""
        self.settings = self.defaults.copy()
        return self.save_settings()

    def validate_all_settings(self) -> dict:
        """Validates all current settings."""
        validation_results = {}
        for key, value in self.settings.items():
            is_valid, message = self.validator.validate_setting(key, value)
            validation_results[key] = {"valid": is_valid, "message": message}
        return validation_results
