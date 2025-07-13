"""
Parallel image downloader with thread-safe progress tracking.
"""

import threading
import time
import concurrent.futures
from typing import Callable, List, Tuple, Optional

from ..logging_config import get_logger
from ..exceptions import AuthenticationError
from ..ui.notification_service import get_notification_service

logger = get_logger(__name__)


class ParallelImageDownloader:
    """Parallel image downloader with thread-safe progress tracking."""

    def __init__(self, max_workers: int = 10):
        self.max_workers = max_workers
        self.progress_lock = threading.Lock()
        self.completed_count = 0
        self.total_count = 0

        # Progress throttling mechanism
        self.last_progress_update = 0.0
        self.progress_update_interval = 0.1  # 100ms throttle interval
        self.pending_update = False

    def download_images(
        self,
        image_tasks: List[Tuple[str, str]],
        progress_callback: Optional[Callable] = None,
        client=None,
    ) -> int:
        """Download images using ThreadPoolExecutor with progress tracking and throttling."""
        if not image_tasks:
            return 0

        self.total_count = len(image_tasks)
        self.completed_count = 0
        # Initialize throttling state
        self.last_progress_update = time.time()
        self.pending_update = False
        # Initialize authentication error tracking
        self._auth_errors = []
        success_count = 0

        if client is None:
            from .client_manager import get_http_client

            client = get_http_client()

        # Start periodic progress update timer
        progress_timer = None
        if progress_callback:
            progress_timer = self._start_progress_timer(progress_callback)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                future_to_task = {
                    executor.submit(self._download_single_image, url, filepath, client): (
                        url,
                        filepath,
                    )
                    for url, filepath in image_tasks
                }
                for future in concurrent.futures.as_completed(future_to_task):
                    url, filepath = future_to_task[future]
                    try:
                        if future.result():
                            success_count += 1
                            logger.info(
                                f"[parallel_downloader] Successfully downloaded: {filepath}"
                            )
                        else:
                            logger.error(f"[parallel_downloader] Failed to download: {url}")
                            # Note: Individual image download failures are often auth-related
                            # Authentication errors are now collected and handled below
                    except Exception as e:
                        logger.error(f"[parallel_downloader] Download exception for {url}: {e}")
                    finally:
                        self._update_progress(progress_callback)

            # Show authentication error if any images failed due to auth issues
            if self._auth_errors:
                # Notify the first authentication error via notification service
                first_auth_error = self._auth_errors[0]
                service = get_notification_service()
                if service:
                    service.show_error(str(first_auth_error))
                auth_count = len(self._auth_errors)
                logger.error(
                    f"[parallel_downloader] {auth_count} image(s) failed due to authentication"
                )

            return success_count
        finally:
            # Stop periodic timer and send final update
            if progress_timer:
                self._stop_progress_timer(progress_timer)
            if progress_callback:
                self._send_final_progress_update(progress_callback)

    def _download_single_image(self, url: str, filepath: str, client) -> bool:
        """Download single image with error handling."""
        try:
            return client.download_file(url, filepath)
        except AuthenticationError as e:
            # Log authentication error and let the caller handle it
            logger.warning(f"[parallel_downloader] Authentication error for {url}: {e}")
            # Store the error for the main thread to handle
            if not hasattr(self, '_auth_errors'):
                self._auth_errors = []
            self._auth_errors.append(e)
            return False

    def _update_progress(self, progress_callback: Optional[Callable]):
        """Thread-safe progress update with throttling mechanism."""
        if not progress_callback:
            return

        with self.progress_lock:
            self.completed_count += 1
            current_time = time.time()

            should_update = self._should_send_progress_update(current_time)
            if should_update:
                self._send_progress_update(progress_callback, current_time)
            else:
                self.pending_update = True

    def _should_send_progress_update(self, current_time: float) -> bool:
        """Determine if progress update should be sent now."""
        is_final_update = self.completed_count >= self.total_count
        time_since_last = current_time - self.last_progress_update
        return time_since_last >= self.progress_update_interval or is_final_update

    def _send_progress_update(self, progress_callback: Callable, current_time: float) -> None:
        """Send progress update to callback."""
        done = self.completed_count
        total = self.total_count
        desc = f"Downloading image {done}/{total}"
        progress_callback(done, total, desc)
        self.last_progress_update = current_time
        self.pending_update = False

    def _start_progress_timer(self, progress_callback: Callable) -> threading.Timer:
        """Start periodic progress update timer."""

        def periodic_update():
            with self.progress_lock:
                if self.pending_update and self.completed_count < self.total_count:
                    done = self.completed_count
                    total = self.total_count
                    desc = f"Downloading image {done}/{total}"
                    progress_callback(done, total, desc)
                    self.last_progress_update = time.time()
                    self.pending_update = False

            # Schedule next update if not complete
            if self.completed_count < self.total_count:
                timer = threading.Timer(self.progress_update_interval, periodic_update)
                timer.daemon = True
                timer.start()
                return timer
            return None

        timer = threading.Timer(self.progress_update_interval, periodic_update)
        timer.daemon = True
        timer.start()
        return timer

    def _stop_progress_timer(self, timer: threading.Timer):
        """Stop progress update timer."""
        if timer:
            timer.cancel()

    def _send_final_progress_update(self, progress_callback: Callable):
        """Send final progress update."""
        with self.progress_lock:
            if self.completed_count > 0:
                done = self.completed_count
                total = self.total_count
                desc = f"Downloaded {done}/{total} images"
                progress_callback(done, total, desc)
