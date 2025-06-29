"""
Download Handlers Module

Manages download-related UI events and operations.
Handles download progress, queue management, and download controls.
"""

from typing import Any, Callable, Dict, List, Optional
from ..logging_config import get_logger
from ..error_handler import with_error_handling

logger = get_logger(__name__)


class DownloadHandlers:
    """
    Manages download-related UI events and operations.
    Handles download progress, queue management, and download controls.
    """

    def __init__(self, ui_controllers=None):
        """
        Initialize download handlers.

        Args:
            ui_controllers: UI controllers instance
        """
        self.ui_controllers = ui_controllers
        self._download_queue = []
        self._active_downloads = {}
        self._download_history = []
        self._progress_callbacks = {}

    @with_error_handling("Failed to start download")
    def start_download(self, download_info: Dict[str, Any]) -> Optional[str]:
        """
        Start a new download.

        Args:
            download_info: Download information

        Returns:
            Optional[str]: Download ID if successful, None otherwise
        """
        # Validate download info
        if not self._validate_download_info(download_info):
            logger.error("Invalid download information")
            return None

        # Generate download ID
        download_id = self._generate_download_id()

        # Add to active downloads
        download_record = {
            'id': download_id,
            'info': download_info.copy(),
            'status': 'starting',
            'progress': 0,
            'start_time': self._get_current_time(),
            'end_time': None,
            'error': None,
        }

        self._active_downloads[download_id] = download_record

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('active_downloads', self._active_downloads)

        logger.info(f"Started download: {download_id}")
        return download_id

    @with_error_handling("Failed to update download progress")
    def update_download_progress(
        self, download_id: str, progress: float, status: str = None
    ) -> bool:
        """
        Update download progress.

        Args:
            download_id: Download identifier
            progress: Progress percentage (0-100)
            status: Optional status update

        Returns:
            bool: True if successful, False otherwise
        """
        if download_id not in self._active_downloads:
            logger.warning(f"Download not found: {download_id}")
            return False

        download_record = self._active_downloads[download_id]
        download_record['progress'] = max(0, min(100, progress))

        if status:
            download_record['status'] = status

        # Call progress callbacks
        if download_id in self._progress_callbacks:
            for callback in self._progress_callbacks[download_id]:
                try:
                    callback(download_id, progress, status)
                except Exception as e:
                    logger.error(f"Error in progress callback: {e}")

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state(
                'download_progress', {'id': download_id, 'progress': progress, 'status': status}
            )

        logger.debug(f"Updated download {download_id}: {progress}% ({status})")
        return True

    @with_error_handling("Failed to complete download")
    def complete_download(self, download_id: str, success: bool = True, error: str = None) -> bool:
        """
        Mark download as completed.

        Args:
            download_id: Download identifier
            success: Whether download was successful
            error: Error message if failed

        Returns:
            bool: True if successful, False otherwise
        """
        if download_id not in self._active_downloads:
            logger.warning(f"Download not found: {download_id}")
            return False

        download_record = self._active_downloads[download_id]
        download_record['end_time'] = self._get_current_time()
        download_record['status'] = 'completed' if success else 'failed'
        download_record['error'] = error

        if success:
            download_record['progress'] = 100

        # Move to history
        self._download_history.append(download_record.copy())
        del self._active_downloads[download_id]

        # Clean up callbacks
        if download_id in self._progress_callbacks:
            del self._progress_callbacks[download_id]

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('active_downloads', self._active_downloads)
            self.ui_controllers.update_ui_state(
                'download_completed', {'id': download_id, 'success': success, 'error': error}
            )

        status = "completed" if success else f"failed ({error})"
        logger.info(f"Download {download_id} {status}")
        return True

    def cancel_download(self, download_id: str) -> bool:
        """
        Cancel an active download.

        Args:
            download_id: Download identifier

        Returns:
            bool: True if cancelled, False otherwise
        """
        if download_id not in self._active_downloads:
            logger.warning(f"Download not found: {download_id}")
            return False

        return self.complete_download(download_id, success=False, error="Cancelled by user")

    def add_to_queue(self, download_info: Dict[str, Any]) -> bool:
        """
        Add download to queue.

        Args:
            download_info: Download information

        Returns:
            bool: True if added, False otherwise
        """
        if not self._validate_download_info(download_info):
            logger.error("Invalid download information for queue")
            return False

        queue_item = {
            'info': download_info.copy(),
            'added_time': self._get_current_time(),
            'priority': download_info.get('priority', 0),
        }

        self._download_queue.append(queue_item)

        # Sort by priority (higher first)
        self._download_queue.sort(key=lambda x: x['priority'], reverse=True)

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('download_queue', self._download_queue)

        logger.info(f"Added download to queue: {download_info.get('name', 'Unknown')}")
        return True

    def get_next_from_queue(self) -> Optional[Dict[str, Any]]:
        """
        Get next download from queue.

        Returns:
            Optional[Dict[str, Any]]: Next download info or None
        """
        if not self._download_queue:
            return None

        queue_item = self._download_queue.pop(0)

        # Update UI state
        if self.ui_controllers:
            self.ui_controllers.update_ui_state('download_queue', self._download_queue)

        return queue_item['info']

    def register_progress_callback(self, download_id: str, callback: Callable) -> bool:
        """
        Register progress callback for download.

        Args:
            download_id: Download identifier
            callback: Callback function

        Returns:
            bool: True if registered, False otherwise
        """
        if not callable(callback):
            logger.error("Invalid callback function")
            return False

        if download_id not in self._progress_callbacks:
            self._progress_callbacks[download_id] = []

        self._progress_callbacks[download_id].append(callback)
        logger.debug(f"Registered progress callback for download: {download_id}")
        return True

    def get_active_downloads(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active downloads.

        Returns:
            Dict[str, Dict[str, Any]]: Active downloads
        """
        return self._active_downloads.copy()

    def get_download_queue(self) -> List[Dict[str, Any]]:
        """
        Get download queue.

        Returns:
            List[Dict[str, Any]]: Download queue
        """
        return self._download_queue.copy()

    def get_download_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get download history.

        Args:
            limit: Maximum number of items to return

        Returns:
            List[Dict[str, Any]]: Download history
        """
        history = self._download_history.copy()
        if limit is not None:
            history = history[-limit:]
        return history

    def clear_download_history(self) -> None:
        """Clear download history."""
        self._download_history.clear()
        logger.info("Download history cleared")

    def get_download_stats(self) -> Dict[str, Any]:
        """
        Get download statistics.

        Returns:
            Dict[str, Any]: Download statistics
        """
        total_downloads = len(self._download_history)
        successful_downloads = sum(1 for d in self._download_history if d['status'] == 'completed')
        failed_downloads = total_downloads - successful_downloads

        return {
            'total_downloads': total_downloads,
            'successful_downloads': successful_downloads,
            'failed_downloads': failed_downloads,
            'active_downloads': len(self._active_downloads),
            'queued_downloads': len(self._download_queue),
            'success_rate': (
                (successful_downloads / total_downloads * 100) if total_downloads > 0 else 0
            ),
        }

    def _validate_download_info(self, download_info: Dict[str, Any]) -> bool:
        """
        Validate download information.

        Args:
            download_info: Download info to validate

        Returns:
            bool: True if valid, False otherwise
        """
        required_fields = ['url', 'filename']
        for field in required_fields:
            if field not in download_info or not download_info[field]:
                logger.error(f"Missing required field: {field}")
                return False

        # Validate URL format
        url = download_info['url']
        if not self._is_valid_url(url):
            logger.error(f"Invalid URL: {url}")
            return False

        return True

    def _is_valid_url(self, url: str) -> bool:
        """
        Check if URL is valid.

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

    def _generate_download_id(self) -> str:
        """
        Generate unique download ID.

        Returns:
            str: Unique download ID
        """
        import time
        import random

        timestamp = int(time.time() * 1000)
        random_num = random.randint(1000, 9999)
        return f"dl_{timestamp}_{random_num}"

    def _get_current_time(self) -> float:
        """
        Get current timestamp.

        Returns:
            float: Current timestamp
        """
        import time

        return time.time()


class DownloadProgressTracker:
    """Tracks and manages download progress information."""

    def __init__(self):
        """Initialize progress tracker."""
        self._progress_data = {}

    def update_progress(self, download_id: str, downloaded: int, total: int) -> Dict[str, Any]:
        """
        Update progress data.

        Args:
            download_id: Download identifier
            downloaded: Bytes downloaded
            total: Total bytes

        Returns:
            Dict[str, Any]: Progress information
        """
        import time

        current_time = time.time()

        if download_id not in self._progress_data:
            self._progress_data[download_id] = {
                'start_time': current_time,
                'last_update': current_time,
                'downloaded': 0,
                'total': total,
                'speed': 0,
            }

        progress_info = self._progress_data[download_id]
        time_diff = current_time - progress_info['last_update']

        if time_diff > 0:
            bytes_diff = downloaded - progress_info['downloaded']
            progress_info['speed'] = bytes_diff / time_diff

        progress_info['downloaded'] = downloaded
        progress_info['last_update'] = current_time

        # Calculate percentage
        percentage = (downloaded / total * 100) if total > 0 else 0

        # Calculate ETA
        if progress_info['speed'] > 0:
            remaining_bytes = total - downloaded
            eta = remaining_bytes / progress_info['speed']
        else:
            eta = None

        return {
            'percentage': percentage,
            'downloaded': downloaded,
            'total': total,
            'speed': progress_info['speed'],
            'eta': eta,
        }

    def get_formatted_progress(self, download_id: str) -> str:
        """
        Get formatted progress string.

        Args:
            download_id: Download identifier

        Returns:
            str: Formatted progress string
        """
        if download_id not in self._progress_data:
            return "No progress data"

        progress_info = self._progress_data[download_id]
        downloaded = progress_info['downloaded']
        total = progress_info['total']
        speed = progress_info['speed']

        # Format bytes
        downloaded_str = self._format_bytes(downloaded)
        total_str = self._format_bytes(total)
        speed_str = self._format_bytes(speed) + '/s'

        percentage = (downloaded / total * 100) if total > 0 else 0

        return f"{percentage:.1f}% ({downloaded_str}/{total_str}) @ {speed_str}"

    def _format_bytes(self, bytes_value: float) -> str:
        """
        Format bytes to human readable string.

        Args:
            bytes_value: Number of bytes

        Returns:
            str: Formatted string
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.1f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.1f} TB"
