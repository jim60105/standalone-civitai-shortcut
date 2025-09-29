"""
DataValidator: Handles input validation and data consistency checks.

This module is responsible for:
- Validating user inputs and parameters
- Checking data consistency across operations
- URL and file path validation
- Configuration validation
- Parameter range and type validation

Extracted from ishortcut.py functions:
- Input validation within various functions
- Parameter checking logic
- URL validation
- File path validation
- Configuration consistency checks
"""

import os
import re
from typing import Dict, Optional, Any, Union
from urllib.parse import urlparse

# Import dependencies from parent modules
from ..logging_config import get_logger
from ..error_handler import with_error_handling
from ..exceptions import DataValidationError
from ..settings.constants import STATIC_IMAGE_EXTENSIONS

logger = get_logger(__name__)


class DataValidator:
    """Handles data validation and consistency checking operations."""

    def __init__(self):
        """Initialize DataValidator."""
        self.valid_model_types = [
            'Checkpoint',
            'TextualInversion',
            'Hypernetwork',
            'AestheticGradient',
            'LORA',
            'Controlnet',
            'Poses',
            'VAE',
            'LoCon',
            'DoRA',
            'Other',
        ]
        # Use only static image formats - no GIF or other dynamic formats
        self.valid_image_extensions = STATIC_IMAGE_EXTENSIONS.copy()
        self.valid_model_extensions = ['.safetensors', '.ckpt', '.pt', '.pth', '.bin']

    @with_error_handling(
        fallback_value=False,
        exception_types=(DataValidationError,),
        retry_count=0,
        user_message="Failed to validate model ID",
    )
    def validate_model_id(self, model_id: Union[str, int]) -> bool:
        """
        Validate model ID format and range.

        Args:
            model_id: Model ID to validate

        Returns:
            True if valid, False otherwise

        Raises:
            DataValidationError: If validation fails
        """
        if model_id is None:
            raise DataValidationError("Model ID cannot be None")

        # Convert to string for validation
        id_str = str(model_id).strip()

        if not id_str:
            raise DataValidationError("Model ID cannot be empty")

        # Check if it's a valid integer
        try:
            id_int = int(id_str)
            if id_int <= 0:
                raise DataValidationError("Model ID must be positive")

            if id_int > 999999999:  # Reasonable upper limit
                raise DataValidationError("Model ID exceeds maximum value")

        except ValueError:
            raise DataValidationError("Model ID must be a valid integer")

        logger.debug(f"[DataValidator] Model ID {model_id} is valid")
        return True

    @with_error_handling(
        fallback_value=False,
        exception_types=(DataValidationError,),
        retry_count=0,
        user_message="Failed to validate URL",
    )
    def validate_url(self, url: str) -> bool:
        """
        Validate URL format and accessibility.

        Args:
            url: URL to validate

        Returns:
            True if valid, False otherwise

        Raises:
            DataValidationError: If validation fails
        """
        if not url or not isinstance(url, str):
            raise DataValidationError("URL must be a non-empty string")

        url = url.strip()
        if not url:
            raise DataValidationError("URL cannot be empty")

        try:
            parsed = urlparse(url)

            # Check scheme
            if not parsed.scheme:
                raise DataValidationError("URL must have a scheme (http/https)")

            if parsed.scheme not in ['http', 'https']:
                raise DataValidationError("URL must use http or https scheme")

            # Check netloc (domain)
            if not parsed.netloc:
                raise DataValidationError("URL must have a valid domain")

            # Basic domain format check
            if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', parsed.netloc):
                # Allow localhost and IP addresses for development
                if not re.match(r'^(localhost|127\.0\.0\.1|0\.0\.0\.0):\d+$', parsed.netloc):
                    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(:\d+)?$', parsed.netloc):
                        raise DataValidationError("URL has invalid domain format")

        except Exception as e:
            if isinstance(e, DataValidationError):
                raise
            raise DataValidationError(f"Invalid URL format: {e}")

        logger.debug(f"[DataValidator] URL {url} is valid")
        return True

    @with_error_handling(
        fallback_value=False,
        exception_types=(DataValidationError,),
        retry_count=0,
        user_message="Failed to validate file path",
    )
    def validate_file_path(self, file_path: str, must_exist: bool = False) -> bool:
        """
        Validate file path format and existence.

        Args:
            file_path: File path to validate
            must_exist: Whether the file must exist

        Returns:
            True if valid, False otherwise

        Raises:
            DataValidationError: If validation fails
        """
        if not file_path or not isinstance(file_path, str):
            raise DataValidationError("File path must be a non-empty string")

        file_path = file_path.strip()
        if not file_path:
            raise DataValidationError("File path cannot be empty")

        # Check for invalid characters
        invalid_chars = '<>"|?*'
        if any(char in file_path for char in invalid_chars):
            raise DataValidationError(f"File path contains invalid characters: {invalid_chars}")

        # Check if path is absolute (recommended for safety)
        if not os.path.isabs(file_path):
            logger.warning(f"[DataValidator] Relative path detected: {file_path}")

        # Check existence if required
        if must_exist and not os.path.exists(file_path):
            raise DataValidationError(f"File does not exist: {file_path}")

        # Check if parent directory exists (for file creation)
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            logger.warning(f"[DataValidator] Parent directory does not exist: {parent_dir}")

        logger.debug(f"[DataValidator] File path {file_path} is valid")
        return True

    @with_error_handling(
        fallback_value=False,
        exception_types=(DataValidationError,),
        retry_count=0,
        user_message="Failed to validate image file",
    )
    def validate_image_file(self, file_path: str) -> bool:
        """
        Validate image file format and accessibility.

        Args:
            file_path: Path to image file

        Returns:
            True if valid, False otherwise

        Raises:
            DataValidationError: If validation fails
        """
        if not self.validate_file_path(file_path):
            return False

        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        if ext not in self.valid_image_extensions:
            raise DataValidationError(
                f"Invalid image extension {ext}. "
                f"Valid extensions: {self.valid_image_extensions}"
            )

        logger.debug(f"[DataValidator] Image file {file_path} is valid")
        return True

    @with_error_handling(
        fallback_value=False,
        exception_types=(DataValidationError,),
        retry_count=0,
        user_message="Failed to validate static image file",
    )
    def validate_static_image_file(self, file_path: str) -> bool:
        """
        Validate image file format and ensure it's a static format only.

        Args:
            file_path: Path to image file

        Returns:
            True if valid static image format, False otherwise

        Raises:
            DataValidationError: If validation fails
        """
        if not self.validate_file_path(file_path):
            return False

        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        if ext not in self.valid_image_extensions:
            # Provide specific message about static format requirement
            if ext in ['.gif', '.webm', '.mp4', '.mov']:
                raise DataValidationError(
                    f"Dynamic image format {ext} is not supported. "
                    f"Only static formats are allowed: {self.valid_image_extensions}"
                )
            else:
                raise DataValidationError(
                    f"Invalid image extension {ext}. "
                    f"Valid static extensions: {self.valid_image_extensions}"
                )

        logger.debug(f"[DataValidator] Static image file {file_path} is valid")
        return True

    @with_error_handling(
        fallback_value=False,
        exception_types=(DataValidationError,),
        retry_count=0,
        user_message="Failed to validate model file",
    )
    def validate_model_file(self, file_path: str) -> bool:
        """
        Validate model file format and accessibility.

        Args:
            file_path: Path to model file

        Returns:
            True if valid, False otherwise

        Raises:
            DataValidationError: If validation fails
        """
        if not self.validate_file_path(file_path):
            return False

        # Check file extension
        _, ext = os.path.splitext(file_path.lower())
        if ext not in self.valid_model_extensions:
            raise DataValidationError(
                f"Invalid model extension {ext}. "
                f"Valid extensions: {self.valid_model_extensions}"
            )

        logger.debug(f"[DataValidator] Model file {file_path} is valid")
        return True

    @with_error_handling(
        fallback_value=False,
        exception_types=(DataValidationError,),
        retry_count=0,
        user_message="Failed to validate model type",
    )
    def validate_model_type(self, model_type: str) -> bool:
        """
        Validate model type against supported types.

        Args:
            model_type: Model type to validate

        Returns:
            True if valid, False otherwise

        Raises:
            DataValidationError: If validation fails
        """
        if not model_type or not isinstance(model_type, str):
            raise DataValidationError("Model type must be a non-empty string")

        model_type = model_type.strip()
        if not model_type:
            raise DataValidationError("Model type cannot be empty")

        if model_type not in self.valid_model_types:
            raise DataValidationError(
                f"Invalid model type '{model_type}'. " f"Valid types: {self.valid_model_types}"
            )

        logger.debug(f"[DataValidator] Model type {model_type} is valid")
        return True

    @with_error_handling(
        fallback_value=False,
        exception_types=(DataValidationError,),
        retry_count=0,
        user_message="Failed to validate download parameters",
    )
    def validate_download_params(self, params: Dict[str, Any]) -> bool:
        """
        Validate download operation parameters.

        Args:
            params: Download parameters dictionary

        Returns:
            True if valid, False otherwise

        Raises:
            DataValidationError: If validation fails
        """
        required_keys = ['url', 'output_path']

        for key in required_keys:
            if key not in params:
                raise DataValidationError(f"Missing required parameter: {key}")

        # Validate URL
        if not self.validate_url(params['url']):
            return False

        # Validate output path
        output_path = params['output_path']
        if not self.validate_file_path(output_path):
            return False

        # Validate optional parameters
        if 'max_retries' in params:
            max_retries = params['max_retries']
            if not isinstance(max_retries, int) or max_retries < 0:
                raise DataValidationError("max_retries must be a non-negative integer")

        if 'timeout' in params:
            timeout = params['timeout']
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                raise DataValidationError("timeout must be a positive number")

        logger.debug("[DataValidator] Download parameters are valid")
        return True

    @with_error_handling(
        fallback_value=False,
        exception_types=(DataValidationError,),
        retry_count=0,
        user_message="Failed to validate configuration",
    )
    def validate_configuration(self, config: Dict[str, Any]) -> bool:
        """
        Validate application configuration settings.

        Args:
            config: Configuration dictionary

        Returns:
            True if valid, False otherwise

        Raises:
            DataValidationError: If validation fails
        """
        if not isinstance(config, dict):
            raise DataValidationError("Configuration must be a dictionary")

        # Validate folder paths
        folder_keys = [
            'shortcut_folder',
            'shortcut_thumbnail_folder',
            'shortcut_info_folder',
            'shortcut_recipe_folder',
        ]

        for key in folder_keys:
            if key in config:
                folder_path = config[key]
                if folder_path and not self.validate_file_path(folder_path):
                    return False

        # Validate numeric settings
        numeric_settings = {
            'shortcut_max_download_image_per_version': (int, 0, 100),
            'max_description_length': (int, 100, 10000),
            'request_timeout': ((int, float), 1, 300),
        }

        for key, (expected_type, min_val, max_val) in numeric_settings.items():
            if key in config:
                value = config[key]
                if not isinstance(value, expected_type):
                    raise DataValidationError(f"{key} must be of type {expected_type.__name__}")
                if value < min_val or value > max_val:
                    raise DataValidationError(f"{key} must be between {min_val} and {max_val}")

        # Validate boolean settings
        boolean_keys = ['enable_nsfw_filter', 'auto_download_images', 'create_thumbnails']
        for key in boolean_keys:
            if key in config:
                value = config[key]
                if not isinstance(value, bool):
                    raise DataValidationError(f"{key} must be a boolean")

        logger.debug("[DataValidator] Configuration is valid")
        return True

    @with_error_handling(
        fallback_value=False,
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to validate JSON data",
    )
    def validate_json_data(self, data: Any, schema: Optional[Dict] = None) -> bool:
        """
        Validate JSON data structure.

        Args:
            data: Data to validate
            schema: Optional schema for validation

        Returns:
            True if valid, False otherwise
        """
        try:
            # Basic type validation
            if data is None:
                logger.warning("[DataValidator] JSON data is None")
                return False

            # Check if data can be serialized to JSON
            import json

            try:
                json.dumps(data)
            except (TypeError, ValueError) as e:
                logger.error(f"[DataValidator] Data is not JSON serializable: {e}")
                return False

            # Schema validation if provided
            if schema:
                return self._validate_against_schema(data, schema)

            logger.debug("[DataValidator] JSON data is valid")
            return True

        except Exception as e:
            logger.error(f"[DataValidator] Error validating JSON data: {e}")
            return False

    def _validate_against_schema(self, data: Any, schema: Dict) -> bool:
        """
        Validate data against a simple schema.

        Args:
            data: Data to validate
            schema: Schema definition

        Returns:
            True if data matches schema
        """
        try:
            # Simple schema validation (can be extended)
            if 'type' in schema:
                expected_type = schema['type']
                if expected_type == 'dict' and not isinstance(data, dict):
                    return False
                elif expected_type == 'list' and not isinstance(data, list):
                    return False
                elif expected_type == 'string' and not isinstance(data, str):
                    return False
                elif expected_type == 'number' and not isinstance(data, (int, float)):
                    return False

            if 'required_keys' in schema and isinstance(data, dict):
                for key in schema['required_keys']:
                    if key not in data:
                        logger.error(f"[DataValidator] Missing required key: {key}")
                        return False

            return True

        except Exception as e:
            logger.error(f"[DataValidator] Schema validation error: {e}")
            return False

    @with_error_handling(
        fallback_value=True,  # Default to valid for safety
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to perform consistency check",
    )
    def check_data_consistency(self, model_info: Dict, file_info: Dict) -> bool:
        """
        Check consistency between model info and file information.

        Args:
            model_info: Model information from API
            file_info: File information from local storage

        Returns:
            True if data is consistent
        """
        try:
            # Check model ID consistency
            api_id = str(model_info.get('id', ''))
            file_id = str(file_info.get('model_id', ''))

            if api_id != file_id:
                logger.warning(f"[DataValidator] Model ID mismatch: API={api_id}, File={file_id}")
                return False

            # Check version count consistency
            api_versions = len(model_info.get('modelVersions', []))
            file_versions = len(file_info.get('versions', []))

            if api_versions != file_versions:
                logger.info(
                    f"[DataValidator] Version count difference: API={api_versions}, "
                    f"File={file_versions}"
                )
                # This might be normal if API has updates, so not failing

            # Check basic data types
            for key, expected_type in [('name', str), ('type', str)]:
                if key in model_info:
                    if not isinstance(model_info[key], expected_type):
                        logger.warning(
                            f"[DataValidator] Invalid type for {key}: "
                            f"expected {expected_type.__name__}"
                        )
                        return False

            logger.debug("[DataValidator] Data consistency check passed")
            return True

        except Exception as e:
            logger.error(f"[DataValidator] Error in consistency check: {e}")
            return True  # Default to valid to avoid blocking operations
