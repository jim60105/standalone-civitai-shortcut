"""
File Processor Module

Handles file operations including directory creation, file I/O,
and model information file management.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from ..logging_config import get_logger
from ..error_handler import with_error_handling
from ..exceptions import FileOperationError

logger = get_logger(__name__)


class FileProcessor:
    """
    Handles file operations for model data including directory management,
    file creation, and data persistence.
    """

    def __init__(self):
        self.logger = logger

    @with_error_handling(
        fallback_value="",
        exception_types=(FileOperationError, OSError),
        retry_count=1,
        retry_delay=0.5,
        user_message="Failed to create model directory",
    )
    def create_model_directory(self, modelid: str) -> str:
        """
        Create directory structure for model data storage.

        Args:
            modelid: Model ID for directory creation

        Returns:
            Path to created model directory
        """
        from .. import setting  # Import here to avoid circular dependency

        try:
            # Create main model path
            model_path = os.path.join(setting.shortcut_info_path, modelid)
            os.makedirs(model_path, exist_ok=True)

            # Create subdirectories
            subdirs = ['images', 'thumbnails', 'info']
            for subdir in subdirs:
                subdir_path = os.path.join(model_path, subdir)
                os.makedirs(subdir_path, exist_ok=True)

            self.logger.info(f"Created model directory: {model_path}")
            return model_path

        except Exception as e:
            self.logger.error(f"Failed to create directory for model {modelid}: {e}")
            raise FileOperationError(f"Directory creation failed: {e}")

    @with_error_handling(
        fallback_value=False,
        exception_types=(FileOperationError, OSError, json.JSONDecodeError),
        retry_count=2,
        retry_delay=0.5,
        user_message="Failed to save model information",
    )
    def save_model_information(self, model_info: dict, model_path: str, modelid: str) -> bool:
        """
        Save model information to JSON file.

        Args:
            model_info: Model information dictionary
            model_path: Path to model directory
            modelid: Model ID for filename

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            info_path = os.path.join(model_path, 'info')
            filename = f"{modelid}.json"
            filepath = os.path.join(info_path, filename)

            # Ensure directory exists
            os.makedirs(info_path, exist_ok=True)

            # Save model information
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(model_info, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved model information: {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save model info for {modelid}: {e}")
            raise FileOperationError(f"Failed to save model information: {e}")

    def load_model_information(self, modelid: str) -> Optional[dict]:
        """
        Load model information from JSON file.

        Args:
            modelid: Model ID to load information for

        Returns:
            Model information dictionary or None if not found
        """
        from .. import setting  # Import here to avoid circular dependency

        try:
            info_path = os.path.join(setting.shortcut_info_path, modelid, 'info')
            filename = f"{modelid}.json"
            filepath = os.path.join(info_path, filename)

            if not os.path.exists(filepath):
                return None

            with open(filepath, 'r', encoding='utf-8') as f:
                model_info = json.load(f)

            return model_info

        except Exception as e:
            self.logger.error(f"Failed to load model info for {modelid}: {e}")
            return None

    def delete_model_directory(self, modelid: str) -> bool:
        """
        Delete model directory and all its contents.

        Args:
            modelid: Model ID for directory deletion

        Returns:
            True if deleted successfully, False otherwise
        """
        from .. import setting  # Import here to avoid circular dependency

        try:
            model_path = os.path.join(setting.shortcut_info_path, modelid)

            if os.path.exists(model_path):
                shutil.rmtree(model_path)
                self.logger.info(f"Deleted model directory: {model_path}")
                return True
            else:
                self.logger.warning(f"Model directory not found: {model_path}")
                return False

        except Exception as e:
            self.logger.error(f"Failed to delete directory for model {modelid}: {e}")
            return False

    def create_model_info_file(self, model_data: dict, filepath: str) -> bool:
        """
        Create a model information file at specified path.

        Args:
            model_data: Model data to save
            filepath: Full path where to save the file

        Returns:
            True if created successfully, False otherwise
        """
        try:
            # Ensure parent directory exists
            parent_dir = os.path.dirname(filepath)
            os.makedirs(parent_dir, exist_ok=True)

            # Write model data to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(model_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Created model info file: {filepath}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to create model info file {filepath}: {e}")
            return False

    def process_model_files(self, version_info: dict) -> List[Dict[str, Any]]:
        """
        Process model files information from version data.

        Args:
            version_info: Version information containing files

        Returns:
            List of processed file information
        """
        if not version_info or 'files' not in version_info:
            return []

        processed_files = []
        for file_info in version_info['files']:
            processed_file = {
                'id': file_info.get('id'),
                'name': file_info.get('name', ''),
                'type': file_info.get('type', ''),
                'sizeKB': file_info.get('sizeKB', 0),
                'format': file_info.get('metadata', {}).get('format', ''),
                'size': file_info.get('metadata', {}).get('size', ''),
                'fp': file_info.get('metadata', {}).get('fp', ''),
                'primary': file_info.get('primary', False),
                'downloadUrl': file_info.get('downloadUrl', ''),
                'pickleScanResult': file_info.get('pickleScanResult', 'Unknown'),
                'virusScanResult': file_info.get('virusScanResult', 'Unknown'),
                'scannedAt': file_info.get('scannedAt'),
            }
            processed_files.append(processed_file)

        return processed_files

    def get_file_extension(self, filename: str) -> str:
        """
        Get file extension from filename.

        Args:
            filename: Name of the file

        Returns:
            File extension (without dot)
        """
        return Path(filename).suffix.lstrip('.')

    def validate_file_path(self, filepath: str) -> bool:
        """
        Validate if file path is safe and accessible.

        Args:
            filepath: Path to validate

        Returns:
            True if path is valid, False otherwise
        """
        try:
            # Convert to Path object for validation
            path_obj = Path(filepath)

            # Check if path is absolute
            if path_obj.is_absolute():
                # Check if parent directory exists or can be created
                parent_dir = path_obj.parent
                if not parent_dir.exists():
                    try:
                        parent_dir.mkdir(parents=True, exist_ok=True)
                    except OSError:
                        return False

            return True

        except Exception as e:
            self.logger.error(f"Invalid file path {filepath}: {e}")
            return False

    def ensure_directory_exists(self, directory_path: str) -> bool:
        """
        Ensure directory exists, create if it doesn't.

        Args:
            directory_path: Path to directory

        Returns:
            True if directory exists or was created successfully
        """
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create directory {directory_path}: {e}")
            return False

    def get_directory_size(self, directory_path: str) -> int:
        """
        Calculate total size of directory in bytes.

        Args:
            directory_path: Path to directory

        Returns:
            Total size in bytes
        """
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(directory_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            return total_size
        except Exception as e:
            self.logger.error(f"Failed to calculate directory size for {directory_path}: {e}")
            return 0

    def cleanup_empty_directories(self, base_path: str) -> int:
        """
        Remove empty directories recursively.

        Args:
            base_path: Base path to start cleanup from

        Returns:
            Number of directories removed
        """
        removed_count = 0
        try:
            for root, dirs, files in os.walk(base_path, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if not os.listdir(dir_path):  # Directory is empty
                            os.rmdir(dir_path)
                            removed_count += 1
                            self.logger.debug(f"Removed empty directory: {dir_path}")
                    except OSError:
                        continue  # Directory not empty or permission issue

            return removed_count

        except Exception as e:
            self.logger.error(f"Failed to cleanup empty directories in {base_path}: {e}")
            return removed_count
