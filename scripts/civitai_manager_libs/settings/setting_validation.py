"""Manages setting validation logic."""

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
        """Validates a single setting value based on predefined rules."""
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
        """Validates a path setting, ensuring it is a valid directory."""
        if not os.path.isdir(path):
            logger.warning(f"Validation failed: Path '{path}' is not a valid directory.")
            return False, f"Path '{path}' is not a valid directory."
        return True, ""

    def validate_range_setting(self, value: any, min_val: any, max_val: any) -> tuple[bool, str]:
        """Validates a numeric setting, ensuring it is within a specified range."""
        if not (min_val <= value <= max_val):
            logger.warning(
                f"Validation failed: Value {value} is out of range ({min_val}-{max_val})."
            )
            return False, f"Value {value} is out of range ({min_val}-{max_val})."
        return True, ""

    def _setup_validation_rules(self) -> None:
        """Sets up the validation rules for different settings."""
        self.validation_rules = {
            'shortcut_column': lambda v: self.validate_range_setting(v, 1, 12),
            'shortcut_rows_per_page': lambda v: self.validate_range_setting(v, 1, 10),
            'gallery_column': lambda v: self.validate_range_setting(v, 1, 12),
            'download_images_folder': self.validate_path_setting,
            'civitai_api_key': lambda v: (isinstance(v, str), "API key must be a string"),
            'http_timeout': lambda v: self.validate_range_setting(v, 10, 300),
            'http_max_retries': lambda v: self.validate_range_setting(v, 0, 10),
            'preview_image_quality': lambda v: self.validate_range_setting(v, 1, 100),
        }
