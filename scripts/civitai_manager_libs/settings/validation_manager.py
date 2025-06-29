"""
Validation Manager Module

Handles validation of settings, configurations, and data integrity
throughout the application.
"""

import os
import json
from typing import Any, Dict
from ..logging_config import get_logger
from ..error_handler import with_error_handling

logger = get_logger(__name__)


class ValidationManager:
    """Manages validation of various data types and configurations."""

    def __init__(self):
        """Initialize validation manager."""
        self._validation_rules = self._load_validation_rules()

    @with_error_handling("Failed to validate configuration")
    def validate_configuration(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete configuration.

        Args:
            config: Configuration to validate

        Returns:
            Dict[str, Any]: Validation results
        """
        results = {'valid': True, 'errors': [], 'warnings': [], 'details': {}}

        # Validate each section
        sections = ['civitai', 'paths', 'ui', 'download', 'cache', 'logging']
        for section in sections:
            section_config = config.get(section, {})
            section_result = self._validate_section(section, section_config)
            results['details'][section] = section_result

            if not section_result['valid']:
                results['valid'] = False
                results['errors'].extend(section_result['errors'])
            results['warnings'].extend(section_result['warnings'])

        return results

    def _validate_section(self, section: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate configuration section.

        Args:
            section: Section name
            config: Section configuration

        Returns:
            Dict[str, Any]: Section validation results
        """
        results = {'valid': True, 'errors': [], 'warnings': []}

        validation_method = getattr(self, f'_validate_{section}_section', None)
        if validation_method:
            return validation_method(config)

        return results

    def _validate_civitai_section(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate Civitai configuration section.

        Args:
            config: Civitai configuration

        Returns:
            Dict[str, Any]: Validation results
        """
        results = {'valid': True, 'errors': [], 'warnings': []}

        # Validate API key
        api_key = config.get('api_key', '')
        if not api_key:
            results['warnings'].append("Civitai API key is not set")
        elif not self._validate_api_key_format(api_key):
            results['errors'].append("Invalid Civitai API key format")
            results['valid'] = False

        # Validate base URL
        base_url = config.get('base_url', '')
        if not base_url:
            results['errors'].append("Civitai base URL is required")
            results['valid'] = False
        elif not self._validate_url(base_url):
            results['errors'].append("Invalid Civitai base URL format")
            results['valid'] = False

        # Validate timeout
        timeout = config.get('timeout', 30)
        if not self._validate_positive_number(timeout):
            results['errors'].append("Invalid timeout value")
            results['valid'] = False

        # Validate max retries
        max_retries = config.get('max_retries', 3)
        if not self._validate_positive_integer(max_retries):
            results['errors'].append("Invalid max retries value")
            results['valid'] = False

        return results

    def _validate_paths_section(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate paths configuration section.

        Args:
            config: Paths configuration

        Returns:
            Dict[str, Any]: Validation results
        """
        results = {'valid': True, 'errors': [], 'warnings': []}

        required_paths = ['models_dir', 'cache_dir', 'data_dir']
        for path_key in required_paths:
            path_value = config.get(path_key, '')
            if not path_value:
                results['errors'].append(f"Path {path_key} is required")
                results['valid'] = False
            elif not self._validate_path(path_value):
                results['warnings'].append(f"Path {path_key} may not be accessible: {path_value}")

        return results

    def _validate_ui_section(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate UI configuration section.

        Args:
            config: UI configuration

        Returns:
            Dict[str, Any]: Validation results
        """
        results = {'valid': True, 'errors': [], 'warnings': []}

        # Validate theme
        theme = config.get('theme', 'default')
        valid_themes = ['default', 'dark', 'light']
        if theme not in valid_themes:
            results['warnings'].append(f"Unknown theme: {theme}")

        # Validate max results
        max_results = config.get('max_results', 50)
        if not self._validate_positive_integer(max_results) or max_results > 1000:
            results['errors'].append("Invalid max results value (must be 1-1000)")
            results['valid'] = False

        # Validate boolean settings
        boolean_settings = ['auto_refresh', 'show_nsfw']
        for setting in boolean_settings:
            value = config.get(setting)
            if value is not None and not isinstance(value, bool):
                results['warnings'].append(f"Setting {setting} should be boolean")

        return results

    def _validate_download_section(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate download configuration section.

        Args:
            config: Download configuration

        Returns:
            Dict[str, Any]: Validation results
        """
        results = {'valid': True, 'errors': [], 'warnings': []}

        # Validate timeout
        timeout = config.get('timeout', 300)
        if not self._validate_positive_number(timeout):
            results['errors'].append("Invalid download timeout value")
            results['valid'] = False

        # Validate max concurrent downloads
        max_concurrent = config.get('max_concurrent', 3)
        if not self._validate_positive_integer(max_concurrent) or max_concurrent > 10:
            results['errors'].append("Invalid max concurrent downloads (must be 1-10)")
            results['valid'] = False

        return results

    def _validate_cache_section(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate cache configuration section.

        Args:
            config: Cache configuration

        Returns:
            Dict[str, Any]: Validation results
        """
        results = {'valid': True, 'errors': [], 'warnings': []}

        # Validate max age
        max_age_days = config.get('max_age_days', 30)
        if not self._validate_positive_integer(max_age_days):
            results['errors'].append("Invalid cache max age value")
            results['valid'] = False

        # Validate max size
        max_size_mb = config.get('max_size_mb', 1000)
        if not self._validate_positive_number(max_size_mb):
            results['errors'].append("Invalid cache max size value")
            results['valid'] = False

        return results

    def _validate_logging_section(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate logging configuration section.

        Args:
            config: Logging configuration

        Returns:
            Dict[str, Any]: Validation results
        """
        results = {'valid': True, 'errors': [], 'warnings': []}

        # Validate log level
        level = config.get('level', 'INFO')
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if level.upper() not in valid_levels:
            results['errors'].append(f"Invalid log level: {level}")
            results['valid'] = False

        # Validate max log files
        max_log_files = config.get('max_log_files', 5)
        if not self._validate_positive_integer(max_log_files):
            results['errors'].append("Invalid max log files value")
            results['valid'] = False

        return results

    @with_error_handling("Failed to validate model data")
    def validate_model_data(self, model_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate model data structure.

        Args:
            model_data: Model data to validate

        Returns:
            Dict[str, Any]: Validation results
        """
        results = {'valid': True, 'errors': [], 'warnings': []}

        # Required fields
        required_fields = ['id', 'name', 'type']
        for field in required_fields:
            if field not in model_data:
                results['errors'].append(f"Missing required field: {field}")
                results['valid'] = False

        # Validate ID
        model_id = model_data.get('id')
        if model_id is not None and not self._validate_positive_integer(model_id):
            results['errors'].append("Invalid model ID")
            results['valid'] = False

        # Validate name
        name = model_data.get('name', '')
        if not isinstance(name, str) or len(name.strip()) == 0:
            results['errors'].append("Invalid model name")
            results['valid'] = False

        # Validate type
        model_type = model_data.get('type', '')
        valid_types = ['Checkpoint', 'LORA', 'TextualInversion', 'Hypernetwork', 'VAE']
        if model_type not in valid_types:
            results['warnings'].append(f"Unknown model type: {model_type}")

        # Validate versions if present
        versions = model_data.get('modelVersions', [])
        if versions and isinstance(versions, list):
            for i, version in enumerate(versions):
                version_result = self._validate_version_data(version)
                if not version_result['valid']:
                    results['errors'].extend(
                        [f"Version {i}: {error}" for error in version_result['errors']]
                    )
                    results['valid'] = False

        return results

    def _validate_version_data(self, version_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate version data structure.

        Args:
            version_data: Version data to validate

        Returns:
            Dict[str, Any]: Validation results
        """
        results = {'valid': True, 'errors': [], 'warnings': []}

        # Required fields
        required_fields = ['id', 'name']
        for field in required_fields:
            if field not in version_data:
                results['errors'].append(f"Missing required field: {field}")
                results['valid'] = False

        # Validate files if present
        files = version_data.get('files', [])
        if files and isinstance(files, list):
            for i, file_data in enumerate(files):
                file_result = self._validate_file_data(file_data)
                if not file_result['valid']:
                    results['errors'].extend(
                        [f"File {i}: {error}" for error in file_result['errors']]
                    )
                    results['valid'] = False

        return results

    def _validate_file_data(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate file data structure.

        Args:
            file_data: File data to validate

        Returns:
            Dict[str, Any]: Validation results
        """
        results = {'valid': True, 'errors': [], 'warnings': []}

        # Required fields
        required_fields = ['name', 'downloadUrl']
        for field in required_fields:
            if field not in file_data:
                results['errors'].append(f"Missing required field: {field}")
                results['valid'] = False

        # Validate download URL
        download_url = file_data.get('downloadUrl', '')
        if download_url and not self._validate_url(download_url):
            results['errors'].append("Invalid download URL")
            results['valid'] = False

        return results

    # Utility validation methods
    def _validate_api_key_format(self, api_key: str) -> bool:
        """Validate API key format."""
        return bool(api_key and len(api_key.strip()) >= 10)

    def _validate_url(self, url: str) -> bool:
        """Validate URL format."""
        try:
            from urllib.parse import urlparse

            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def _validate_positive_number(self, value: Any) -> bool:
        """Validate positive number."""
        try:
            num_val = float(value)
            return num_val > 0
        except (TypeError, ValueError):
            return False

    def _validate_positive_integer(self, value: Any) -> bool:
        """Validate positive integer."""
        try:
            int_val = int(value)
            return int_val > 0
        except (TypeError, ValueError):
            return False

    def _validate_path(self, path: str) -> bool:
        """Validate file system path."""
        if not path:
            return False
        try:
            # Check if we can create the directory
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            return True
        except (OSError, TypeError):
            return False

    def _load_validation_rules(self) -> Dict[str, Any]:
        """
        Load validation rules from configuration.

        Returns:
            Dict[str, Any]: Validation rules
        """
        return {
            'api_key_min_length': 10,
            'max_results_limit': 1000,
            'max_concurrent_downloads': 10,
            'valid_log_levels': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
            'valid_themes': ['default', 'dark', 'light'],
            'valid_model_types': ['Checkpoint', 'LORA', 'TextualInversion', 'Hypernetwork', 'VAE'],
        }

    @with_error_handling("Failed to validate data integrity")
    def validate_data_integrity(self, data_dir: str) -> Dict[str, Any]:
        """
        Validate data directory integrity.

        Args:
            data_dir: Data directory path

        Returns:
            Dict[str, Any]: Integrity validation results
        """
        results = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'checked_files': 0,
            'corrupted_files': [],
        }

        if not os.path.exists(data_dir):
            results['errors'].append(f"Data directory does not exist: {data_dir}")
            results['valid'] = False
            return results

        # Check essential files
        essential_files = ['settings.json', 'models.json', 'classifications.json']

        for filename in essential_files:
            filepath = os.path.join(data_dir, filename)
            file_result = self._validate_json_file(filepath)
            results['checked_files'] += 1

            if not file_result['valid']:
                results['errors'].extend(file_result['errors'])
                results['corrupted_files'].append(filename)
                results['valid'] = False

        return results

    def _validate_json_file(self, filepath: str) -> Dict[str, Any]:
        """
        Validate JSON file.

        Args:
            filepath: Path to JSON file

        Returns:
            Dict[str, Any]: File validation results
        """
        results = {'valid': True, 'errors': []}

        if not os.path.exists(filepath):
            results['errors'].append(f"File does not exist: {filepath}")
            results['valid'] = False
            return results

        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                json.load(file)
        except json.JSONDecodeError as e:
            results['errors'].append(f"Invalid JSON in {filepath}: {e}")
            results['valid'] = False
        except Exception as e:
            results['errors'].append(f"Error reading {filepath}: {e}")
            results['valid'] = False

        return results
