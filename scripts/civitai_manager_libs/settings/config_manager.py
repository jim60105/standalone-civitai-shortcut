"""
Configuration Manager Module

Handles application configuration including loading, saving, validation,
and migration of settings.
"""

import json
from typing import Any, Dict, Optional
from ..logging_config import get_logger
from ..error_handler import with_error_handling
from .defaults import Defaults

logger = get_logger(__name__)


class ConfigManager:
    """Manages application configuration settings."""

    def __init__(self, config_path: str = None):
        """
        Initialize configuration manager.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path or Defaults.CONFIG_FILE_PATH
        self._config_data = {}
        self._load_config()

    @with_error_handling("Failed to load configuration")
    def _load_config(self) -> None:
        """Load configuration from file."""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as file:
                self._config_data = json.load(file)
                logger.info(f"Configuration loaded from {self.config_path}")
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {self.config_path}")
            self._config_data = self._get_default_config()
            self.save_config()
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in configuration file: {e}")
            self._config_data = self._get_default_config()

    @with_error_handling("Failed to save configuration")
    def save_config(self) -> bool:
        """
        Save configuration to file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import os

            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as file:
                json.dump(self._config_data, file, indent=2, ensure_ascii=False)
                logger.info(f"Configuration saved to {self.config_path}")
                return True
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False

    def get_setting(self, key: str, default: Any = None) -> Any:
        """
        Get configuration setting.

        Args:
            key: Setting key (supports dot notation)
            default: Default value if key not found

        Returns:
            Any: Setting value or default
        """
        try:
            keys = key.split('.')
            value = self._config_data
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default

    @with_error_handling("Failed to set configuration")
    def set_setting(self, key: str, value: Any) -> bool:
        """
        Set configuration setting.

        Args:
            key: Setting key (supports dot notation)
            value: Setting value

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            keys = key.split('.')
            config = self._config_data
            for k in keys[:-1]:
                if k not in config:
                    config[k] = {}
                config = config[k]
            config[keys[-1]] = value
            logger.debug(f"Setting updated: {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"Failed to set setting {key}: {e}")
            return False

    def remove_setting(self, key: str) -> bool:
        """
        Remove configuration setting.

        Args:
            key: Setting key to remove

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            keys = key.split('.')
            config = self._config_data
            for k in keys[:-1]:
                config = config[k]
            del config[keys[-1]]
            logger.debug(f"Setting removed: {key}")
            return True
        except (KeyError, TypeError):
            return False

    def get_all_settings(self) -> Dict[str, Any]:
        """
        Get all configuration settings.

        Returns:
            Dict[str, Any]: All settings
        """
        return self._config_data.copy()

    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """
        Update multiple settings.

        Args:
            settings: Dictionary of settings to update

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._config_data.update(settings)
            logger.info(f"Updated {len(settings)} settings")
            return True
        except Exception as e:
            logger.error(f"Failed to update settings: {e}")
            return False

    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to defaults.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._config_data = self._get_default_config()
            result = self.save_config()
            if result:
                logger.info("Configuration reset to defaults")
            return result
        except Exception as e:
            logger.error(f"Failed to reset configuration: {e}")
            return False

    def validate_config(self) -> Dict[str, Any]:
        """
        Validate configuration settings.

        Returns:
            Dict[str, Any]: Validation results
        """
        validation_results = {'valid': True, 'errors': [], 'warnings': []}

        # Validate required settings
        required_settings = ['civitai.api_key', 'paths.models_dir', 'ui.theme']

        for setting in required_settings:
            value = self.get_setting(setting)
            if value is None:
                validation_results['errors'].append(f"Missing required setting: {setting}")
                validation_results['valid'] = False

        # Validate setting types and values
        type_validations = {
            'ui.max_results': int,
            'download.timeout': (int, float),
            'ui.auto_refresh': bool,
        }

        for setting, expected_type in type_validations.items():
            value = self.get_setting(setting)
            if value is not None and not isinstance(value, expected_type):
                validation_results['warnings'].append(
                    f"Setting {setting} has incorrect type: expected {expected_type}, "
                    f"got {type(value)}"
                )

        return validation_results

    def backup_config(self, backup_path: Optional[str] = None) -> bool:
        """
        Create backup of current configuration.

        Args:
            backup_path: Path for backup file

        Returns:
            bool: True if successful, False otherwise
        """
        if backup_path is None:
            backup_path = f"{self.config_path}.backup"

        try:
            import shutil

            shutil.copy2(self.config_path, backup_path)
            logger.info(f"Configuration backed up to {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to backup configuration: {e}")
            return False

    def restore_config(self, backup_path: str) -> bool:
        """
        Restore configuration from backup.

        Args:
            backup_path: Path to backup file

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import shutil

            shutil.copy2(backup_path, self.config_path)
            self._load_config()
            logger.info(f"Configuration restored from {backup_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to restore configuration: {e}")
            return False

    def _get_default_config(self) -> Dict[str, Any]:
        """
        Get default configuration.

        Returns:
            Dict[str, Any]: Default configuration
        """
        return {
            'civitai': {
                'api_key': '',
                'base_url': Defaults.CIVITAI_BASE_URL,
                'timeout': Defaults.DEFAULT_TIMEOUT,
                'max_retries': Defaults.MAX_RETRIES,
            },
            'paths': {
                'models_dir': Defaults.MODELS_DIR,
                'cache_dir': Defaults.CACHE_DIR,
                'data_dir': Defaults.DATA_DIR,
                'thumbnails_dir': Defaults.THUMBNAILS_DIR,
            },
            'ui': {
                'theme': 'default',
                'max_results': Defaults.MAX_SEARCH_RESULTS,
                'auto_refresh': True,
                'show_nsfw': False,
                'language': 'en',
            },
            'download': {
                'timeout': Defaults.DOWNLOAD_TIMEOUT,
                'max_concurrent': Defaults.MAX_CONCURRENT_DOWNLOADS,
                'verify_checksums': True,
                'auto_organize': True,
            },
            'cache': {
                'enable': True,
                'max_age_days': Defaults.CACHE_MAX_AGE_DAYS,
                'max_size_mb': Defaults.CACHE_MAX_SIZE_MB,
            },
            'logging': {'level': 'INFO', 'file_logging': True, 'max_log_files': 5},
        }


class ConfigValidator:
    """Validates configuration settings."""

    @staticmethod
    def validate_api_key(api_key: str) -> bool:
        """
        Validate Civitai API key format.

        Args:
            api_key: API key to validate

        Returns:
            bool: True if valid, False otherwise
        """
        return bool(api_key and len(api_key.strip()) > 0)

    @staticmethod
    def validate_path(path: str, must_exist: bool = False) -> bool:
        """
        Validate file/directory path.

        Args:
            path: Path to validate
            must_exist: Whether path must exist

        Returns:
            bool: True if valid, False otherwise
        """
        if not path:
            return False

        import os

        if must_exist:
            return os.path.exists(path)
        else:
            # Check if path is valid (can be created)
            try:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                return True
            except (OSError, TypeError):
                return False

    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format.

        Args:
            url: URL to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            from urllib.parse import urlparse

            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    @staticmethod
    def validate_timeout(timeout: Any) -> bool:
        """
        Validate timeout value.

        Args:
            timeout: Timeout value to validate

        Returns:
            bool: True if valid, False otherwise
        """
        try:
            timeout_val = float(timeout)
            return timeout_val > 0
        except (TypeError, ValueError):
            return False
