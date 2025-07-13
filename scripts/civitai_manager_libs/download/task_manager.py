"""
Download task management and execution.
"""

import os
import time
import threading

from ..logging_config import get_logger
from ..error_handler import with_error_handling
from ..exceptions import (
    AuthenticationRequiredError,
    DownloadError,
    NetworkError,
    HTTPError,
    TimeoutError,
    FileOperationError,
)
from ..http.client_manager import get_http_client
from ..http.image_downloader import ParallelImageDownloader
from .. import util

logger = get_logger(__name__)


class DownloadTask:
    """Data structure for carrying download task parameters."""

    def __init__(self, fid, filename, url, path, total_size=None):
        self.fid = fid
        self.filename = filename
        self.url = url
        self.path = path
        self.total = total_size


@with_error_handling(
    fallback_value=False,
    exception_types=(AuthenticationRequiredError,),  # these errors abort the flow
    retry_count=0,
    user_message="🔐 Authentication required. Please check your API key and try again.",
)
def download_file_with_auth_handling(task: DownloadTask):
    """Handle authenticated downloads, aborting on failure."""
    client = get_http_client()
    return client.download_file_with_resume(task.url, task.path)


@with_error_handling(
    fallback_value=False,
    exception_types=(NetworkError, HTTPError, TimeoutError),  # retryable network errors
    retry_count=3,
    retry_delay=2.0,
    user_message="🌐 Network error occurred. Retrying...",
)
def download_file_with_retry(task: DownloadTask):
    """Handle retryable network errors."""
    client = get_http_client()
    return client.download_file_with_resume(task.url, task.path)


@with_error_handling(
    fallback_value=False,
    exception_types=(DownloadError, FileOperationError),  # file-related errors
    retry_count=1,
    retry_delay=1.0,
    user_message="💾 File operation failed. Please check permissions and disk space.",
)
def download_file_with_file_handling(task: DownloadTask):
    """Handle file operation related errors."""
    client = get_http_client()
    return client.download_file_with_resume(task.url, task.path)


@with_error_handling(
    fallback_value=False,
    exception_types=(Exception),  # file-related errors
    retry_count=1,
    retry_delay=1.0,
)
def download_file_with_notifications(task: DownloadTask):
    """Download file using the existing decorator-based error handling."""
    # Don't call notify_start here since it's already called by the caller

    return (
        download_file_with_auth_handling(task)
        or download_file_with_retry(task)
        or download_file_with_file_handling(task)
    )


def download_image_file(model_name: str, image_urls: list, progress_gr=None):
    """Download model-related images with parallel processing."""
    if not model_name or not image_urls:
        return

    model_folder = util.make_download_image_folder(model_name)
    if not model_folder:
        return

    save_folder = os.path.join(model_folder, "images")
    os.makedirs(save_folder, exist_ok=True)

    # Prepare parallel download tasks
    image_tasks = []
    for index, img_url in enumerate(image_urls, start=1):
        if util.is_url_or_filepath(img_url) == "url":
            dest_name = f"image_{index:03d}.jpg"
            dest_path = os.path.join(save_folder, dest_name)
            image_tasks.append((img_url, dest_path))

    # Setup progress wrapper matching new progress_callback signature (done, total, desc)
    def progress_wrapper(done, total, desc):
        if progress_gr is not None:
            try:
                progress_gr(done / total if total else 0, desc)
            except Exception:
                pass

    # Execute parallel download
    downloader = ParallelImageDownloader(max_workers=10)
    success_count = downloader.download_images(image_tasks, progress_wrapper)

    # Handle final progress update
    total_count = len(image_urls)
    logger.info(
        f"[downloader] Parallel image download complete: {success_count}/{total_count} successful"
    )

    if progress_gr:
        msg = f"Downloaded {success_count}/{total_count} images"
        progress_gr(1.0, msg)


def download_file(url: str, file_path: str) -> bool:
    """Download files using standard HTTP client."""
    client = get_http_client()
    return client.download_file(url, file_path)


def download_file_gr(url: str, file_path: str, progress_gr=None) -> bool:
    """Download files with Gradio progress integration."""
    client = get_http_client()

    def progress_wrapper(downloaded: int, total: int, desc: str = "") -> None:
        if progress_gr is not None:
            try:
                progress_gr(downloaded / total if total else 0, desc)
            except Exception:
                pass

    return client.download_file(url, file_path, progress_callback=progress_wrapper)


class DownloadManager:
    """Manage multiple download tasks with monitoring and control."""

    def __init__(self):
        self.active = {}
        self.history = []
        self.client = get_http_client()

    def start(self, url: str, file_path: str, progress_cb=None) -> str:
        task_id = f"download_{int(time.time())}_{len(self.active)}"

        def wrap(dl, tot, sp=""):
            if progress_cb:
                progress_cb(dl, tot, sp)
            self.active[task_id] = {
                "url": url,
                "path": file_path,
                "downloaded": dl,
                "total": tot,
                "speed": sp,
            }

        thread = threading.Thread(target=self._worker, args=(task_id, url, file_path, wrap))
        thread.daemon = True
        thread.start()
        return task_id

    def _worker(self, tid, url, path, prog):
        try:
            ok = self.client.download_file_with_resume(url, path, progress_callback=prog)
            info = self.active.pop(tid, {})
            info.update({"completed": True, "success": ok, "end": time.time()})
            self.history.append(info)

            # Silent completion - do not send completion notification
            if ok:
                logger.info(f"[downloader] Background download completed: {path}")
            else:
                logger.error(f"[downloader] Background download failed: {url}")

        except Exception as e:
            logger.error(f"[downloader] Worker error {tid}: {e}")
            self.active.pop(tid, None)

    def list_active(self):
        return dict(self.active)

    def cancel(self, tid) -> bool:
        return self.active.pop(tid, None) is not None
