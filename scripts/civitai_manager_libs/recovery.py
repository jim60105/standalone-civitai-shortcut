import os
import shutil
from typing import Optional

from scripts.civitai_manager_libs.exceptions import FileOperationError, NetworkError
from scripts.civitai_manager_libs.logging_config import get_logger

logger = get_logger(__name__)


class ErrorRecoveryManager:
    """Manages error recovery strategies."""

    @staticmethod
    def handle_file_operation_error(
        error: FileOperationError, operation: str, filepath: str
    ) -> bool:
        """Handle file operation errors with recovery attempts."""
        logger.warning(f"File operation '{operation}' failed for {filepath}: {error}")
        if operation == "read":
            return ErrorRecoveryManager._attempt_file_read_recovery(filepath)
        if operation == "write":
            return ErrorRecoveryManager._attempt_file_write_recovery(filepath)
        if operation == "delete":
            return ErrorRecoveryManager._attempt_file_delete_recovery(filepath)
        return False

    @staticmethod
    def handle_network_error(error: NetworkError, url: str, method: str = "GET") -> Optional[dict]:
        """Handle network errors with fallback strategies."""
        logger.warning(f"Network error for {method} {url}: {error}")
        if "api.civitai.com" in url:
            cached_data = ErrorRecoveryManager._get_cached_api_response(url)
            if cached_data:
                logger.info(f"Using cached data for {url}")
                return cached_data
        return None

    @staticmethod
    def _attempt_file_read_recovery(filepath: str) -> bool:
        """Attempt to recover from file read errors."""
        if os.path.exists(filepath):
            backup_path = f"{filepath}.backup"
            if os.path.exists(backup_path):
                try:
                    shutil.copy2(backup_path, filepath)
                    return True
                except Exception:
                    pass
        return False

    @staticmethod
    def _attempt_file_write_recovery(filepath: str) -> bool:
        """Attempt to recover from file write errors."""
        return False

    @staticmethod
    def _attempt_file_delete_recovery(filepath: str) -> bool:
        """Attempt to recover from file delete errors."""
        return False

    @staticmethod
    def _get_cached_api_response(url: str) -> Optional[dict]:
        """Get cached API response for fallback."""
        return None
