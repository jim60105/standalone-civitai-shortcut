"""
FileProcessor: Handles file operations and directory management.

This module is responsible for:
- Writing model information to local storage
- Creating and managing model directories
- Saving model data to JSON files
- File path management and validation
- Atomic file operations for data integrity

Extracted from ishortcut.py functions:
- write_model_information()
- _create_model_directory()
- _save_model_information()
- delete_model_information()
- Various file I/O operations
"""

import os
import json
import shutil
from typing import Dict, Optional

# Import dependencies from parent modules
from .. import settings
from ..logging_config import get_logger
from ..error_handler import with_error_handling
from ..exceptions import NetworkError, FileOperationError, CivitaiShortcutError

logger = get_logger(__name__)


class FileProcessor:
    """Handles file operations and directory management for model data."""

    def __init__(self):
        """Initialize FileProcessor."""
        pass

    @with_error_handling(
        fallback_value=None,
        exception_types=(NetworkError, FileOperationError, CivitaiShortcutError),
        retry_count=1,
        retry_delay=1.0,
        user_message="Failed to write model information",
    )
    def write_model_information(
        self, model_info: Dict, modelid: str, register_only_information: bool = False
    ) -> Optional[Dict]:
        """
        Write model information to local storage.

        Args:
            model_info: Model information from Civitai API
            modelid: Model ID for file organization
            register_only_information: If True, skip image operations

        Returns:
            Model information dictionary if successful, None otherwise
        """
        logger.info(f"[FileProcessor] Writing model information for {modelid}")

        if not model_info or not modelid:
            logger.warning("[FileProcessor] Invalid model_info or modelid provided")
            return None

        # Create model directory
        model_path = self.create_model_directory(modelid)
        if not model_path:
            logger.error(f"[FileProcessor] Failed to create directory for {modelid}")
            return None

        # Save model information to JSON
        if not self.save_model_information(model_info, model_path, modelid):
            logger.error(f"[FileProcessor] Failed to save model info for {modelid}")
            return None

        logger.info(f"[FileProcessor] Successfully wrote model information for {modelid}")
        return model_info

    @with_error_handling(
        fallback_value=None,
        exception_types=(FileOperationError,),
        retry_count=1,
        retry_delay=1.0,
        user_message="Failed to create model directory",
    )
    def create_model_directory(self, modelid: str) -> Optional[str]:
        """
        Create directory for model information storage.

        Args:
            modelid: Model ID to create directory for

        Returns:
            Path to created directory, or None if failed
        """
        logger.info(f"[FileProcessor] Creating directory for model {modelid}")

        if not modelid:
            logger.warning("[FileProcessor] No modelid provided")
            return None

        try:
            model_path = os.path.join(settings.shortcut_info_folder, modelid)
            logger.debug(f"[FileProcessor] Target path: {model_path}")

            if os.path.exists(model_path):
                logger.info("[FileProcessor] Directory already exists")
            else:
                os.makedirs(model_path, exist_ok=True)
                logger.info("[FileProcessor] Directory created successfully")

            return model_path

        except Exception as e:
            logger.error(f"[FileProcessor] Failed to create directory: {e}")
            raise FileOperationError(f"Cannot create directory for model {modelid}") from e

    @with_error_handling(
        fallback_value=False,
        exception_types=(FileOperationError,),
        retry_count=1,
        retry_delay=1.0,
        user_message="Failed to save model information",
    )
    def save_model_information(self, model_info: Dict, model_path: str, modelid: str) -> bool:
        """
        Save model information to JSON file with atomic operations.

        Args:
            model_info: Model information to save
            model_path: Directory path to save in
            modelid: Model ID for filename

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"[FileProcessor] Saving model info for {modelid}")

        if not model_info or not model_path or not modelid:
            logger.warning("[FileProcessor] Invalid parameters for save operation")
            return False

        try:
            # Generate file paths
            tmp_info_file = os.path.join(model_path, f"tmp{settings.INFO_SUFFIX}{settings.INFO_EXT}")
            model_info_file = os.path.join(
                model_path, f"{modelid}{settings.INFO_SUFFIX}{settings.INFO_EXT}"
            )

            logger.debug(f"[FileProcessor] Temp file: {tmp_info_file}")
            logger.debug(f"[FileProcessor] Final file: {model_info_file}")

            # Write to temporary file first for atomic operation
            with open(tmp_info_file, 'w', encoding='utf-8') as f:
                json.dump(model_info, f, indent=4, ensure_ascii=False)

            # Atomically replace the target file
            os.replace(tmp_info_file, model_info_file)
            logger.info("[FileProcessor] Model info saved successfully")
            return True

        except Exception as e:
            logger.error(f"[FileProcessor] Failed to save model info: {e}")
            # Clean up temporary file if it exists
            try:
                if 'tmp_info_file' in locals() and os.path.exists(tmp_info_file):
                    os.remove(tmp_info_file)
            except Exception:
                pass  # Ignore cleanup errors
            raise FileOperationError(f"Cannot save model information for {modelid}") from e

    def delete_model_information(self, modelid: str) -> bool:
        """
        Delete model information directory and all its contents.

        Args:
            modelid: Model ID to delete information for

        Returns:
            True if deletion was successful or directory didn't exist, False otherwise
        """
        if not modelid:
            logger.warning("[FileProcessor] No modelid provided for deletion")
            return False

        model_path = os.path.join(settings.shortcut_info_folder, modelid)

        # Safety check to prevent accidental deletion of parent directory
        if settings.shortcut_info_folder == model_path:
            logger.error("[FileProcessor] Refusing to delete shortcut info root folder")
            return False

        try:
            if os.path.exists(model_path):
                shutil.rmtree(model_path)
                logger.info(f"[FileProcessor] Deleted model information for {modelid}")
            else:
                logger.debug(f"[FileProcessor] Model directory doesn't exist: {model_path}")
            return True

        except Exception as e:
            logger.error(f"[FileProcessor] Failed to delete model information for {modelid}: {e}")
            return False

    def model_info_exists(self, modelid: str) -> bool:
        """
        Check if model information file exists locally.

        Args:
            modelid: Model ID to check

        Returns:
            True if model info file exists, False otherwise
        """
        if not modelid:
            return False

        model_info_file = os.path.join(
            settings.shortcut_info_folder,
            modelid,
            f"{modelid}{settings.INFO_SUFFIX}{settings.INFO_EXT}",
        )

        exists = os.path.isfile(model_info_file)
        logger.debug(f"[FileProcessor] Model info exists for {modelid}: {exists}")
        return exists

    def get_model_info_file_path(self, modelid: str) -> str:
        """
        Get the full path to model information file.

        Args:
            modelid: Model ID

        Returns:
            Full path to model information JSON file
        """
        return os.path.join(
            settings.shortcut_info_folder,
            modelid,
            f"{modelid}{settings.INFO_SUFFIX}{settings.INFO_EXT}",
        )

    def backup_model_information(self, modelid: str, backup_suffix: str = ".backup") -> bool:
        """
        Create a backup copy of model information file.

        Args:
            modelid: Model ID to backup
            backup_suffix: Suffix to add to backup file

        Returns:
            True if backup was successful, False otherwise
        """
        if not modelid:
            return False

        try:
            source_file = self.get_model_info_file_path(modelid)
            backup_file = f"{source_file}{backup_suffix}"

            if os.path.exists(source_file):
                shutil.copy2(source_file, backup_file)
                logger.info(f"[FileProcessor] Created backup: {backup_file}")
                return True
            else:
                logger.debug(f"[FileProcessor] Source file doesn't exist: {source_file}")
                return False

        except Exception as e:
            logger.error(f"[FileProcessor] Failed to backup model info for {modelid}: {e}")
            return False

    def ensure_directories_exist(self) -> bool:
        """
        Ensure all required directories exist for file operations.

        Returns:
            True if all directories exist or were created successfully
        """
        try:
            # Ensure shortcut info folder exists
            if not os.path.exists(settings.shortcut_info_folder):
                os.makedirs(settings.shortcut_info_folder, exist_ok=True)
                logger.info(
                    f"[FileProcessor] Created shortcut info folder: {settings.shortcut_info_folder}"
                )

            return True

        except Exception as e:
            logger.error(f"[FileProcessor] Failed to create required directories: {e}")
            return False

    def get_model_directory_size(self, modelid: str) -> int:
        """
        Calculate total size of model directory in bytes.

        Args:
            modelid: Model ID to calculate size for

        Returns:
            Total size in bytes, 0 if directory doesn't exist
        """
        if not modelid:
            return 0

        model_path = os.path.join(settings.shortcut_info_folder, modelid)

        if not os.path.exists(model_path):
            return 0

        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(model_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)

            logger.debug(f"[FileProcessor] Model {modelid} directory size: {total_size} bytes")
            return total_size

        except Exception as e:
            logger.error(f"[FileProcessor] Error calculating directory size for {modelid}: {e}")
            return 0

    def cleanup_temp_files(self, modelid: str) -> int:
        """
        Clean up temporary files in model directory.

        Args:
            modelid: Model ID to clean up temp files for

        Returns:
            Number of files cleaned up
        """
        if not modelid:
            return 0

        model_path = os.path.join(settings.shortcut_info_folder, modelid)

        if not os.path.exists(model_path):
            return 0

        cleanup_count = 0
        try:
            for filename in os.listdir(model_path):
                if filename.startswith('tmp') and (
                    filename.endswith(settings.INFO_EXT) or filename.endswith('.tmp')
                ):
                    temp_file = os.path.join(model_path, filename)
                    try:
                        os.remove(temp_file)
                        cleanup_count += 1
                        logger.debug(f"[FileProcessor] Cleaned up temp file: {temp_file}")
                    except Exception as e:
                        logger.warning(
                            f"[FileProcessor] Failed to remove temp file {temp_file}: {e}"
                        )

            if cleanup_count > 0:
                logger.info(f"[FileProcessor] Cleaned up {cleanup_count} temp files for {modelid}")

        except Exception as e:
            logger.error(f"[FileProcessor] Error during temp file cleanup for {modelid}: {e}")

        return cleanup_count
