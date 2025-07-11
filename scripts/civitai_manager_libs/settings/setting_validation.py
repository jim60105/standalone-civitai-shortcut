"""Manages settings validation logic."""

import os

from ..logging_config import get_logger

logger = get_logger(__name__)


class SettingValidator:
    """Validates application settings."""

    def __init__(self):
        """Initializes the SettingValidator."""
        self.validation_rules = {}
        self._setup_validation_rules()

    def validate_setting(self, key: str, value: any) -> tuple[bool, str]:
        """Validates a single settings value based on predefined rules."""
        if key in self.validation_rules:
            return self.validation_rules[key](value)
        return True, ""

    def validate_ui_settings(self, settings: dict) -> dict:
        """Validates all UI-related settings."""
        # Add specific validation logic for UI settings if needed
        return {k: self.validate_setting(k, v) for k, v in settings.items()}

    def validate_download_settings(self, settings: dict) -> dict:
        """Validates all download-related settings."""
        # Add specific validation logic for download settings if needed
        return {k: self.validate_setting(k, v) for k, v in settings.items()}

    def validate_api_settings(self, settings: dict) -> dict:
        """Validates all API-related settings."""
        # Add specific validation logic for API settings if needed
        return {k: self.validate_setting(k, v) for k, v in settings.items()}

    def validate_model_settings(self, settings: dict) -> dict:
        """Validates all model-related settings."""
        # Add specific validation logic for model settings if needed
        return {k: self.validate_setting(k, v) for k, v in settings.items()}

    def validate_path_setting(self, path: str) -> tuple[bool, str]:
        """Validates a path settings, ensuring it is a valid directory."""
        if not os.path.isdir(path):
            logger.warning(f"Validation failed: Path '{path}' is not a valid directory.")
            return False, f"Path '{path}' is not a valid directory."
        return True, ""

    def validate_range_setting(self, value: any, min_val: any, max_val: any) -> tuple[bool, str]:
        """Validates a numeric settings, ensuring it is within a specified range."""
        if not (min_val <= value <= max_val):
            logger.warning(
                f"Validation failed: Value {value} is out of range ({min_val}-{max_val})."
            )
            return False, f"Value {value} is out of range ({min_val}-{max_val})."
        return True, ""

    def _setup_validation_rules(self) -> None:
        """Sets up the validation rules for different settings."""
        # Import here to avoid circular import
        from .setting_categories import SettingCategories

        self.validation_rules = {
            'download_images_folder': self.validate_path_setting,
            'civitai_api_key': lambda v: (isinstance(v, str), "API key must be a string"),
        }

        # Add range validation for numeric settings based on SettingCategories
        for setting_key in SettingCategories.get_all_defaults().keys():
            min_val, max_val = SettingCategories.get_validation_range(setting_key)
            if min_val is not None and max_val is not None:
                self.validation_rules[setting_key] = lambda v, min_v=min_val, max_v=max_val: (
                    self.validate_range_setting(v, min_v, max_v)
                )
