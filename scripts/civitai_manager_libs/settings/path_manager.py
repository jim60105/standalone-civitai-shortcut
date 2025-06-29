"""
Path Manager Module

Handles path resolution, directory management, and file path operations
for the application.
"""

import os
from typing import Optional
from ..logging_config import get_logger
from .defaults import Defaults

logger = get_logger(__name__)


class PathManager:
    """
    Manages all path-related operations including directory creation,
    path resolution, and file system organization.
    """

    def __init__(self, base_path: Optional[str] = None):
        self.logger = logger
        self._base_path = base_path or os.getcwd()
        self._extension_base = ""
        self._initialize_paths()

    def _initialize_paths(self):
        """Initialize all required paths."""
        self._setup_extension_base()
        self._ensure_required_directories()

    def _setup_extension_base(self):
        """Setup the extension base path."""
        try:
            from ..compat.compat_layer import CompatibilityLayer

            compat = CompatibilityLayer.get_compatibility_layer()
            if compat and hasattr(compat, 'path_manager'):
                self._extension_base = compat.path_manager.get_extension_path()
                logger.debug(
                    f"[PathManager] Set extension_base from compat layer: {self._extension_base}"
                )
            else:
                # Fallback to current directory structure
                current_dir = os.path.dirname(os.path.abspath(__file__))
                self._extension_base = os.path.dirname(
                    os.path.dirname(os.path.dirname(current_dir))
                )
                logger.debug(f"[PathManager] Fallback extension_base: {self._extension_base}")
        except Exception as e:
            logger.warning(f"[PathManager] Failed to setup extension base: {e}")
            self._extension_base = self._base_path

    def _ensure_required_directories(self):
        """Ensure all required directories exist."""
        try:
            required_dirs = Defaults.get_required_directories()
            for dir_name in required_dirs:
                dir_path = self.get_absolute_path(dir_name)
                os.makedirs(dir_path, exist_ok=True)
                logger.debug(f"[PathManager] Ensured directory exists: {dir_path}")
        except Exception as e:
            logger.error(f"[PathManager] Failed to create required directories: {e}")

    @property
    def base_path(self) -> str:
        """Get the base path."""
        return self._base_path

    @property
    def extension_base(self) -> str:
        """Get the extension base path."""
        return self._extension_base

    def get_absolute_path(self, relative_path: str) -> str:
        """
        Get absolute path from relative path.

        Args:
            relative_path: Relative path string

        Returns:
            Absolute path string
        """
        if os.path.isabs(relative_path):
            return relative_path
        return os.path.join(self._base_path, relative_path)

    def get_sc_data_path(self) -> str:
        """
        Get the shortcut data directory path.

        Returns:
            Path to shortcut data directory
        """
        return self.get_absolute_path(Defaults.SC_DATA_ROOT)

    def get_sd_data_path(self) -> str:
        """
        Get the stable diffusion data directory path.

        Returns:
            Path to stable diffusion data directory
        """
        return self.get_absolute_path(Defaults.SD_DATA_ROOT)

    def get_shortcut_info_path(self) -> str:
        """
        Get the shortcut info directory path.

        Returns:
            Path to shortcut info directory
        """
        return os.path.join(self.get_sc_data_path(), "sc_infos")

    def get_shortcut_gallery_path(self) -> str:
        """
        Get the shortcut gallery directory path.

        Returns:
            Path to shortcut gallery directory
        """
        return os.path.join(self.get_sc_data_path(), "sc_gallery")

    def get_shortcut_recipes_path(self) -> str:
        """
        Get the shortcut recipes directory path.

        Returns:
            Path to shortcut recipes directory
        """
        return os.path.join(self.get_sc_data_path(), "sc_recipes")

    def get_shortcut_thumbnail_path(self) -> str:
        """
        Get the shortcut thumbnail directory path.

        Returns:
            Path to shortcut thumbnail directory
        """
        return os.path.join(self.get_sc_data_path(), "sc_thumb_images")

    def get_model_folder_path(self, model_type: str) -> str:
        """
        Get the folder path for a specific model type.

        Args:
            model_type: Type of model (e.g., 'Checkpoint', 'LORA')

        Returns:
            Path to model type folder
        """
        folder_mapping = Defaults.get_model_folder_mapping()
        folder_name = folder_mapping.get(model_type, 'other')
        return os.path.join(self.get_sd_data_path(), folder_name)

    def get_model_info_path(self, model_id: str) -> str:
        """
        Get the path for model information storage.

        Args:
            model_id: Model ID

        Returns:
            Path to model info directory
        """
        return os.path.join(self.get_shortcut_info_path(), model_id)

    def get_model_image_path(self, model_id: str) -> str:
        """
        Get the path for model images storage.

        Args:
            model_id: Model ID

        Returns:
            Path to model images directory
        """
        return os.path.join(self.get_model_info_path(model_id), "images")

    def get_model_thumbnail_path(self, model_id: str) -> str:
        """
        Get the path for model thumbnail storage.

        Args:
            model_id: Model ID

        Returns:
            Path to model thumbnail directory
        """
        return os.path.join(self.get_shortcut_thumbnail_path(), model_id)

    def create_model_directory(self, model_id: str) -> str:
        """
        Create directory structure for a model.

        Args:
            model_id: Model ID

        Returns:
            Path to created model directory
        """
        model_path = self.get_model_info_path(model_id)

        # Create main model directory
        os.makedirs(model_path, exist_ok=True)

        # Create subdirectories
        subdirs = ['images', 'thumbnails', 'info']
        for subdir in subdirs:
            subdir_path = os.path.join(model_path, subdir)
            os.makedirs(subdir_path, exist_ok=True)

        logger.info(f"[PathManager] Created model directory structure: {model_path}")
        return model_path

    def get_config_file_path(self, config_name: str = "CivitaiShortCutSetting.json") -> str:
        """
        Get the path for configuration file.

        Args:
            config_name: Name of configuration file

        Returns:
            Path to configuration file
        """
        return os.path.join(self.get_sc_data_path(), config_name)

    def get_shortcut_data_file_path(self, data_name: str = "CivitaiShortCut.json") -> str:
        """
        Get the path for shortcut data file.

        Args:
            data_name: Name of data file

        Returns:
            Path to shortcut data file
        """
        return os.path.join(self.get_sc_data_path(), data_name)

    def get_classification_file_path(
        self, classification_name: str = "CivitaiShortCutClassification.json"
    ) -> str:
        """
        Get the path for classification file.

        Args:
            classification_name: Name of classification file

        Returns:
            Path to classification file
        """
        return os.path.join(self.get_sc_data_path(), classification_name)

    def get_recipe_collection_file_path(
        self, recipe_name: str = "CivitaiShortCutRecipeCollection.json"
    ) -> str:
        """
        Get the path for recipe collection file.

        Args:
            recipe_name: Name of recipe file

        Returns:
            Path to recipe collection file
        """
        return os.path.join(self.get_sc_data_path(), recipe_name)

    def ensure_directory_exists(self, directory_path: str) -> bool:
        """
        Ensure a directory exists, create if it doesn't.

        Args:
            directory_path: Path to directory

        Returns:
            True if directory exists or was created successfully
        """
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"[PathManager] Failed to create directory {directory_path}: {e}")
            return False

    def is_safe_path(self, file_path: str) -> bool:
        """
        Check if file path is safe (within allowed directories).

        Args:
            file_path: Path to validate

        Returns:
            True if path is safe
        """
        try:
            # Convert to absolute path
            abs_path = os.path.abspath(file_path)

            # Check if path is within base directory
            base_abs = os.path.abspath(self._base_path)
            return abs_path.startswith(base_abs)
        except Exception as e:
            logger.error(f"[PathManager] Path safety check failed for {file_path}: {e}")
            return False

    def get_relative_path(self, absolute_path: str) -> str:
        """
        Get relative path from absolute path.

        Args:
            absolute_path: Absolute path

        Returns:
            Relative path from base directory
        """
        try:
            return os.path.relpath(absolute_path, self._base_path)
        except Exception as e:
            logger.error(f"[PathManager] Failed to get relative path for {absolute_path}: {e}")
            return absolute_path

    def clean_filename(self, filename: str) -> str:
        """
        Clean filename by removing invalid characters.

        Args:
            filename: Original filename

        Returns:
            Cleaned filename
        """
        # Remove invalid characters for filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')

        # Remove leading/trailing spaces and dots
        filename = filename.strip('. ')

        # Ensure filename is not empty
        if not filename:
            filename = "unknown"

        return filename

    def get_available_space(self, path: str = None) -> int:
        """
        Get available disk space in bytes.

        Args:
            path: Path to check (defaults to base path)

        Returns:
            Available space in bytes
        """
        try:
            import shutil

            check_path = path or self._base_path
            _, _, free_bytes = shutil.disk_usage(check_path)
            return free_bytes
        except Exception as e:
            logger.error(f"[PathManager] Failed to get disk space for {path}: {e}")
            return 0

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
            logger.error(
                f"[PathManager] Failed to calculate directory size for {directory_path}: {e}"
            )
            return 0

    def cleanup_empty_directories(self, base_path: str = None) -> int:
        """
        Remove empty directories recursively.

        Args:
            base_path: Base path to start cleanup (defaults to sc_data_path)

        Returns:
            Number of directories removed
        """
        cleanup_path = base_path or self.get_sc_data_path()
        removed_count = 0

        try:
            for root, dirs, files in os.walk(cleanup_path, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        if not os.listdir(dir_path):  # Directory is empty
                            os.rmdir(dir_path)
                            removed_count += 1
                            logger.debug(f"[PathManager] Removed empty directory: {dir_path}")
                    except OSError:
                        continue  # Directory not empty or permission issue

            return removed_count
        except Exception as e:
            logger.error(
                f"[PathManager] Failed to cleanup empty directories in {cleanup_path}: {e}"
            )
            return removed_count

    def backup_file(self, file_path: str, backup_suffix: str = ".backup") -> bool:
        """
        Create a backup of a file.

        Args:
            file_path: Path to file to backup
            backup_suffix: Suffix to add to backup file

        Returns:
            True if backup created successfully
        """
        try:
            if not os.path.exists(file_path):
                return False

            backup_path = file_path + backup_suffix
            import shutil

            shutil.copy2(file_path, backup_path)
            logger.info(f"[PathManager] Created backup: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"[PathManager] Failed to backup file {file_path}: {e}")
            return False
