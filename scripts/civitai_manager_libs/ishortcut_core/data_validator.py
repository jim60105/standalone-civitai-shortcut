"""
Data Validator Module

Handles data validation for model information, file structures,
and data integrity checks.
"""

from typing import Any, List
from ..logging_config import get_logger

logger = get_logger(__name__)


class DataValidator:
    """
    Handles validation operations for model data, file structures,
    and data integrity checks.
    """

    def __init__(self):
        self.logger = logger

    def validate_model_data(self, model_data: dict) -> bool:
        """
        Validate model data structure and required fields.

        Args:
            model_data: Model data dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(model_data, dict):
            self.logger.error("Model data must be a dictionary")
            return False

        # Check required fields
        required_fields = ['id', 'name', 'type']
        for field in required_fields:
            if field not in model_data:
                self.logger.error(f"Missing required field: {field}")
                return False

        # Validate field types
        if not isinstance(model_data['id'], (str, int)):
            self.logger.error("Model ID must be string or integer")
            return False

        if not isinstance(model_data['name'], str):
            self.logger.error("Model name must be string")
            return False

        if not isinstance(model_data['type'], str):
            self.logger.error("Model type must be string")
            return False

        return True

    def validate_version_data(self, version_data: dict) -> bool:
        """
        Validate version data structure.

        Args:
            version_data: Version data dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(version_data, dict):
            self.logger.error("Version data must be a dictionary")
            return False

        required_fields = ['id', 'name']
        for field in required_fields:
            if field not in version_data:
                self.logger.error(f"Missing required version field: {field}")
                return False

        # Validate files if present
        if 'files' in version_data:
            if not self.validate_files_data(version_data['files']):
                return False

        # Validate images if present
        if 'images' in version_data:
            if not self.validate_images_data(version_data['images']):
                return False

        return True

    def validate_files_data(self, files_data: List[dict]) -> bool:
        """
        Validate files data structure.

        Args:
            files_data: List of file dictionaries to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(files_data, list):
            self.logger.error("Files data must be a list")
            return False

        for file_data in files_data:
            if not isinstance(file_data, dict):
                self.logger.error("Each file entry must be a dictionary")
                return False

            required_fields = ['id', 'name']
            for field in required_fields:
                if field not in file_data:
                    self.logger.error(f"Missing required file field: {field}")
                    return False

            # Validate downloadUrl if present
            if 'downloadUrl' in file_data:
                if not isinstance(file_data['downloadUrl'], str):
                    self.logger.error("Download URL must be string")
                    return False

        return True

    def validate_images_data(self, images_data: List[dict]) -> bool:
        """
        Validate images data structure.

        Args:
            images_data: List of image dictionaries to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(images_data, list):
            self.logger.error("Images data must be a list")
            return False

        for image_data in images_data:
            if not isinstance(image_data, dict):
                self.logger.error("Each image entry must be a dictionary")
                return False

            # Validate URL if present
            if 'url' in image_data:
                if not isinstance(image_data['url'], str):
                    self.logger.error("Image URL must be string")
                    return False

            # Validate dimensions if present
            for dim_field in ['width', 'height']:
                if dim_field in image_data:
                    if not isinstance(image_data[dim_field], int):
                        self.logger.error(f"Image {dim_field} must be integer")
                        return False

        return True

    def validate_shortcut_data(self, shortcut_data: dict) -> bool:
        """
        Validate shortcut data structure.

        Args:
            shortcut_data: Shortcut data dictionary to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(shortcut_data, dict):
            self.logger.error("Shortcut data must be a dictionary")
            return False

        for model_id, model_data in shortcut_data.items():
            if not isinstance(model_id, str):
                self.logger.error(f"Model ID must be string: {model_id}")
                return False

            if not self.validate_model_data(model_data):
                self.logger.error(f"Invalid model data for ID: {model_id}")
                return False

        return True

    def validate_url(self, url: str) -> bool:
        """
        Validate URL format.

        Args:
            url: URL string to validate

        Returns:
            True if valid URL format
        """
        if not isinstance(url, str):
            return False

        if not url.strip():
            return False

        # Basic URL validation
        if not (url.startswith('http://') or url.startswith('https://')):
            return False

        return True

    def validate_model_id(self, model_id: str) -> bool:
        """
        Validate model ID format.

        Args:
            model_id: Model ID to validate

        Returns:
            True if valid model ID
        """
        if not isinstance(model_id, str):
            return False

        if not model_id.strip():
            return False

        # Model ID should be numeric or alphanumeric
        if not model_id.isdigit() and not model_id.isalnum():
            return False

        return True

    def validate_file_path(self, file_path: str) -> bool:
        """
        Validate file path format.

        Args:
            file_path: File path to validate

        Returns:
            True if valid file path
        """
        if not isinstance(file_path, str):
            return False

        if not file_path.strip():
            return False

        # Check for dangerous path patterns
        dangerous_patterns = ['../', '..\\', '//', '\\\\']
        for pattern in dangerous_patterns:
            if pattern in file_path:
                self.logger.warning(f"Dangerous path pattern detected: {file_path}")
                return False

        return True

    def validate_json_structure(self, data: Any, expected_keys: List[str]) -> bool:
        """
        Validate JSON structure has expected keys.

        Args:
            data: Data to validate
            expected_keys: List of expected keys

        Returns:
            True if structure is valid
        """
        if not isinstance(data, dict):
            return False

        for key in expected_keys:
            if key not in data:
                self.logger.error(f"Missing expected key: {key}")
                return False

        return True

    def validate_image_metadata(self, metadata: dict) -> bool:
        """
        Validate image metadata structure.

        Args:
            metadata: Image metadata dictionary

        Returns:
            True if valid metadata
        """
        if not isinstance(metadata, dict):
            return False

        # Check for common metadata fields
        numeric_fields = ['width', 'height', 'size']
        for field in numeric_fields:
            if field in metadata:
                if not isinstance(metadata[field], (int, float)):
                    self.logger.error(f"Invalid {field} in image metadata")
                    return False

        return True

    def validate_download_info(self, download_info: dict) -> bool:
        """
        Validate download information structure.

        Args:
            download_info: Download info dictionary

        Returns:
            True if valid download info
        """
        if not isinstance(download_info, dict):
            return False

        required_fields = ['url', 'file_path']
        for field in required_fields:
            if field not in download_info:
                self.logger.error(f"Missing download info field: {field}")
                return False

        # Validate URL
        if not self.validate_url(download_info['url']):
            self.logger.error("Invalid download URL")
            return False

        # Validate file path
        if not self.validate_file_path(download_info['file_path']):
            self.logger.error("Invalid download file path")
            return False

        return True

    def sanitize_filename(self, filename: str) -> str:
        """
        Sanitize filename by removing dangerous characters.

        Args:
            filename: Original filename

        Returns:
            Sanitized filename
        """
        if not isinstance(filename, str):
            return "unknown"

        # Remove dangerous characters
        dangerous_chars = ['<', '>', ':', '"', '|', '?', '*', '/', '\\']
        sanitized = filename
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '_')

        # Remove leading/trailing spaces and dots
        sanitized = sanitized.strip('. ')

        # Ensure filename is not empty
        if not sanitized:
            sanitized = "unknown"

        return sanitized

    def is_safe_path(self, path: str, base_path: str) -> bool:
        """
        Check if path is safe (within base path).

        Args:
            path: Path to check
            base_path: Base path for validation

        Returns:
            True if path is safe
        """
        try:
            import os

            # Resolve absolute paths
            abs_path = os.path.abspath(path)
            abs_base = os.path.abspath(base_path)

            # Check if path is within base path
            return abs_path.startswith(abs_base)
        except Exception as e:
            self.logger.error(f"Path safety check failed: {e}")
            return False
