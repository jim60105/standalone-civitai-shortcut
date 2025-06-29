"""
Gallery Download Manager - Image download utilities with retry logic.

This module handles downloading images from gallery with progress tracking,
parallel processing, and retry capabilities.
"""

import os
import time
from typing import List, Tuple, Optional, Callable

from ..logging_config import get_logger
from .. import setting
from ..http_client import get_http_client, ParallelImageDownloader
from ..error_handler import with_error_handling

logger = get_logger(__name__)


@with_error_handling()
def _download_single_image(img_url: str, save_path: str) -> bool:
    """Download a single image with proper error handling."""
    client = get_http_client()
    logger.debug(f"Downloading image from: {img_url}")
    logger.debug(f"Saving to: {save_path}")
    success = client.download_file(img_url, save_path)
    if success:
        logger.debug(f"Successfully downloaded image: {save_path}")
    else:
        logger.warning(f"Failed to download image: {img_url}")
    return success


class GalleryDownloadManager:
    """Manage gallery image downloads with retry capability."""

    def __init__(self):
        self.failed_downloads: List[Tuple[str, str]] = []
        self.client = get_http_client()

    @with_error_handling()
    def download_with_retry(self, img_url: str, save_path: str, max_retries: int = 2) -> bool:
        """Download image with retry on failure."""
        for attempt in range(max_retries + 1):
            if self.client.download_file(img_url, save_path):
                return True
            if attempt < max_retries:
                logger.debug(f"Retry {attempt + 1} for: {img_url}")
                time.sleep(1)
        self.failed_downloads.append((img_url, save_path))
        return False

    @with_error_handling()
    def retry_failed_downloads(self) -> None:
        """Retry all previously failed downloads."""
        if not self.failed_downloads:
            return

        logger.debug(f"Retrying {len(self.failed_downloads)} failed downloads")

        retry_list = self.failed_downloads.copy()
        self.failed_downloads.clear()

        for img_url, save_path in retry_list:
            self.download_with_retry(img_url, save_path, max_retries=1)


@with_error_handling()
def download_images_with_progress(
    dn_image_list: List[str], progress_callback: Optional[Callable] = None
) -> None:
    """Download images with parallel processing and progress tracking."""
    if not dn_image_list:
        return

    downloader = ParallelImageDownloader(max_workers=10)
    client = get_http_client()

    # Prepare download tasks
    image_tasks = []
    for img_url in dn_image_list:
        gallery_img_file = setting.get_image_url_to_gallery_file(img_url)
        if not os.path.isfile(gallery_img_file):
            image_tasks.append((img_url, gallery_img_file))

    # Execute parallel download
    success_count = downloader.download_images(image_tasks, progress_callback, client)

    logger.debug(f"Parallel download completed: {success_count}/{len(image_tasks)} successful")


@with_error_handling()
def download_images_batch(dn_image_list: List[str], batch_size: Optional[int] = None) -> None:
    """Download images in batches to avoid overwhelming the server."""
    if not dn_image_list:
        return

    if batch_size is None:
        batch_size = setting.gallery_download_batch_size

    client = get_http_client()

    for i in range(0, len(dn_image_list), batch_size):
        batch = dn_image_list[i : i + batch_size]
        logger.debug(f"Processing batch {i//batch_size + 1}, {len(batch)} images")
        for img_url in batch:
            gallery_img_file = setting.get_image_url_to_gallery_file(img_url)
            if not os.path.isfile(gallery_img_file):
                client.download_file(img_url, gallery_img_file)
        time.sleep(0.5)
