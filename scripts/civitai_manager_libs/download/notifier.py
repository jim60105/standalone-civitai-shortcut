"""
Download notification system for UI and logging.
"""

from ..logging_config import get_logger
from ..error_handler import with_error_handling
from .. import util
from ..ui import notification_service as _ui_notification_service

logger = get_logger(__name__)


# Proxy to UI notification service to allow dynamic patches in both notifier and UI modules
def get_notification_service():
    """Get the current global notification service instance via UI notification module."""
    return _ui_notification_service.get_notification_service()


class DownloadNotifier:
    """Notify users of download status via UI and logs."""

    @staticmethod
    @with_error_handling(
        fallback_value=None,
        exception_types=(Exception,),
        show_notification=True,
        user_message=None,  # let decorator use exception type name
    )
    def notify_start(filename: str, file_size: int = None):
        notification_service = get_notification_service()
        if notification_service:
            size_str = f" ({util.format_file_size(file_size)})" if file_size else ""
            notification_service.show_info(
                f"🚀 Starting download: {filename}{size_str}", duration=3
            )

    @staticmethod
    def notify_progress(filename: str, downloaded: int, total: int, speed: str = ""):
        """Log download progress."""
        if total and total > 0:
            percentage = (downloaded / total) * 100
            downloaded_str = util.format_file_size(downloaded)
            total_str = util.format_file_size(total)
            speed_str = f" at {speed}" if speed else ""
            logger.debug(
                (
                    f"[downloader] Progress: {percentage:.1f}% "
                    f"({downloaded_str}/{total_str}){speed_str}"
                )
            )
        else:
            downloaded_str = util.format_file_size(downloaded)
            speed_str = f" at {speed}" if speed else ""
            logger.debug(f"[downloader] Downloaded: {downloaded_str}{speed_str}")

    @staticmethod
    def notify_complete(filename: str, success: bool, error_msg: str = None):
        """Notify download completion or failure using UI and logs."""
        notification_service = get_notification_service()
        error_detail = f" - {error_msg}" if error_msg else ""

        if notification_service:
            if success:
                notification_service.show_info(f"✅ Download completed: {filename}", duration=5)
            else:
                notification_service.show_error(
                    f"❌ Download failed: {filename}{error_detail}", duration=10
                )

        # Always log the result
        if success:
            logger.info(f"[downloader] Download completed: {filename}")
        else:
            logger.error(f"[downloader] Download failed: {filename}{error_detail}")
