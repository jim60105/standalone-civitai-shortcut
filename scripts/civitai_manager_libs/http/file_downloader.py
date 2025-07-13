"""
File download functionality for CivitaiHttpClient.
"""

import os
import time
from typing import Callable, Optional

from ..logging_config import get_logger
from ..error_handler import with_error_handling
from ..exceptions import AuthenticationError
from ..ui.notification_service import get_notification_service
from .. import settings, util

logger = get_logger(__name__)


class FileDownloadMixin:
    """
    Mixin class providing file download capabilities to CivitaiHttpClient.
    This includes resume functionality, progress tracking, and validation.
    """

    @with_error_handling(
        fallback_value=False,
        exception_types=(Exception,),
        retry_count=0,
        retry_delay=0,
        user_message=None,
    )
    def download_file(
        self,
        url: str,
        filepath: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> bool:
        """Download file with progress tracking. Returns True on success."""
        response = self.get_stream(url)
        if not response:
            return False
        # Handle Content-Length header case-insensitively for streaming downloads
        header_len = response.headers.get(
            "content-length", response.headers.get("Content-Length", 0)
        )
        total = int(header_len or 0)
        downloaded = 0
        try:
            with open(filepath, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if not chunk:
                        continue
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total)
            # Validate file size after download
            if not self._validate_download_size(filepath, total):
                return False
            return True
        except Exception as e:
            logger.error(f"[http_client] File write error: {e}")
            return False

    @with_error_handling(
        fallback_value=False,
        exception_types=(Exception,),
        retry_count=0,
        retry_delay=0,
        user_message=None,
    )
    def download_file_with_resume(
        self,
        url: str,
        filepath: str,
        progress_callback: Optional[Callable] = None,
        headers: Optional[dict] = None,
    ) -> bool:
        """Download file with resume capability and progress tracking."""
        resume_pos = self._get_resume_position(filepath)
        download_headers = self._prepare_download_headers(headers, resume_pos)

        try:
            response = self.get_stream(url, headers=download_headers)
            if not response:
                return False

            total_size = self._calculate_total_size(response, resume_pos)
            return self._perform_resume_download(
                filepath, response, resume_pos, total_size, progress_callback
            )

        except Exception as e:
            return self._handle_download_error(e, url, filepath)

    def _get_resume_position(self, filepath: str) -> int:
        """Get the position to resume download from."""
        if settings.download_resume_enabled and os.path.exists(filepath):
            resume_pos = os.path.getsize(filepath)
            logger.debug(f"[http_client] Resuming download from position: {resume_pos}")
            return resume_pos
        return 0

    def _prepare_download_headers(self, headers: Optional[dict], resume_pos: int) -> dict:
        """Prepare headers for resume download."""
        download_headers = headers.copy() if headers else {}
        if resume_pos > 0:
            download_headers["Range"] = f"bytes={resume_pos}-"
        return download_headers

    def _calculate_total_size(self, response, resume_pos: int) -> int:
        """Calculate total file size including resume position."""
        total_size = int(response.headers.get("Content-Length", 0))
        if resume_pos > 0:
            total_size += resume_pos
        return total_size

    def _perform_resume_download(
        self,
        filepath: str,
        response,
        resume_pos: int,
        total_size: int,
        progress_callback: Optional[Callable],
    ) -> bool:
        """Perform the actual download with resume capability."""
        mode = "ab" if resume_pos > 0 else "wb"

        with open(filepath, mode) as f:
            downloaded = resume_pos
            download_tracker = self._create_download_tracker()

            for chunk in response.iter_content(chunk_size=settings.download_chunk_size):
                if not chunk:
                    continue

                f.write(chunk)
                downloaded += len(chunk)

                if progress_callback:
                    self._update_download_progress(
                        progress_callback, downloaded, total_size, resume_pos, download_tracker
                    )

            # Final progress update
            if progress_callback:
                self._send_final_download_progress(
                    progress_callback, downloaded, total_size, resume_pos, download_tracker
                )

        # Validate downloaded file
        return self._validate_download_size(filepath, total_size)

    def _create_download_tracker(self) -> dict:
        """Create a tracker for download progress timing."""
        return {'start_time': time.time(), 'last_update': time.time(), 'update_interval': 2.0}

    def _update_download_progress(
        self,
        progress_callback: Callable,
        downloaded: int,
        total_size: int,
        resume_pos: int,
        tracker: dict,
    ) -> None:
        """Update download progress if enough time has passed."""
        current_time = time.time()
        if current_time - tracker['last_update'] >= tracker['update_interval']:
            speed = self._calculate_speed(
                downloaded - resume_pos, current_time - tracker['start_time']
            )
            progress_callback(downloaded, total_size, speed)
            tracker['last_update'] = current_time

    def _send_final_download_progress(
        self,
        progress_callback: Callable,
        downloaded: int,
        total_size: int,
        resume_pos: int,
        tracker: dict,
    ) -> None:
        """Send final progress update after download completion."""
        total_time = time.time() - tracker['start_time']
        final_speed = self._calculate_speed(downloaded - resume_pos, total_time)
        progress_callback(downloaded, total_size, final_speed)

    def _calculate_speed(self, bytes_downloaded: int, elapsed_time: float) -> str:
        """Calculate download speed in human-readable format."""
        if elapsed_time <= 0:
            return ""

        speed_bps = bytes_downloaded / elapsed_time

        if speed_bps < 1024:
            return f"{speed_bps:.1f} B/s"
        elif speed_bps < 1024 * 1024:
            return f"{speed_bps / 1024:.1f} KB/s"
        else:
            return f"{speed_bps / (1024 * 1024):.1f} MB/s"

    def _handle_download_error(self, error: Exception, url: str, filepath: str) -> bool:
        """Handle download errors with recovery strategies."""
        # Re-raise AuthenticationError to let caller handle it properly
        if isinstance(error, AuthenticationError):
            logger.debug("[http_client] Re-raising AuthenticationError for proper handling")
            raise error

        error_handled = self._process_download_error_type(error, url)

        if not error_handled:
            logger.error(f"[http_client] Unknown download error: {error}")

        self._cleanup_failed_download(filepath)
        return False

    def _process_download_error_type(self, error: Exception, url: str) -> bool:
        """Process different types of download errors."""
        import requests

        if isinstance(error, requests.exceptions.Timeout):
            return self._handle_timeout_error(url)
        elif isinstance(error, requests.exceptions.ConnectionError):
            return self._handle_connection_error_download(url)
        elif hasattr(error, "response") and error.response:
            return self._handle_download_response_error(error.response)
        return False

    def _handle_timeout_error(self, url: str) -> bool:
        """Handle download timeout errors."""
        logger.warning(f"[http_client] Download timeout for {url}")
        return True

    def _handle_connection_error_download(self, url: str) -> bool:
        """Handle download connection errors."""
        logger.warning(f"[http_client] Connection error for {url}")
        return True

    def _handle_download_response_error(self, response) -> bool:
        """Handle HTTP response errors during download."""
        # Suppress HTTP response errors during download; signal handled
        return True

    def _cleanup_failed_download(self, filepath: str) -> None:
        """Clean up partial file if download failed."""
        try:
            if os.path.exists(filepath) and os.path.getsize(filepath) == 0:
                os.remove(filepath)
        except Exception:
            pass

    def _validate_download_size(
        self, filepath: str, expected_size: int, tolerance: float = 0.1
    ) -> bool:
        """Validate downloaded file size against expected size."""
        if not os.path.exists(filepath):
            return False

        actual_size = os.path.getsize(filepath)
        if expected_size <= 0:
            return True  # Cannot validate if expected size unknown

        size_diff_ratio = abs(actual_size - expected_size) / expected_size
        if size_diff_ratio > tolerance:
            expected_size_str = util.format_file_size(expected_size)
            actual_size_str = util.format_file_size(actual_size)
            logger.warning(
                f"[http_client] File size mismatch: expected {expected_size}, got {actual_size}"
            )
            notification_service = get_notification_service()
            if notification_service:
                notification_service.show_warning(
                    f"⚠️ Downloaded file size differs significantly from expected. "
                    f"Expected: {expected_size_str}, Actual: {actual_size_str}. "
                    f"Please verify the download.",
                )
            return False

        return True
