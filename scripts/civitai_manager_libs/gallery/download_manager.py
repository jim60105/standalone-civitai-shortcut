"""
Download Manager Module

Handles all download-related functionality including batch downloads,
progress tracking, and file management operations.
Extracted from civitai_gallery_action.py to follow SRP principles.
"""

import os
import shutil
import time
import threading
import datetime
from typing import List, Tuple, Optional, Callable

import gradio as gr

from ..error_handler import with_error_handling
from ..exceptions import NetworkError, FileOperationError
from ..logging_config import get_logger
from ..http import get_http_client, ParallelImageDownloader
from .. import settings
from .. import util

logger = get_logger(__name__)

try:
    from tqdm import tqdm
except ImportError:
    tqdm = lambda iterable, **kwargs: iterable  # noqa: E731


class ModelProcessor:
    """Simple model processor for test compatibility."""

    def get_model_info(self, model_id):
        """Get basic model information."""
        return {'id': model_id, 'name': f'Model_{model_id}'}


class GalleryDownloadManager:
    """Enhanced gallery download management with error handling and retry logic."""

    def __init__(self):
        self.failed_downloads = []
        self.client = get_http_client()
        self.active_downloads = {}

    @with_error_handling(
        fallback_value=False,
        exception_types=(NetworkError, FileOperationError),
        retry_count=2,
        retry_delay=1.0,
        user_message="Failed to download image",
    )
    def download_single_image(self, img_url: str, save_path: str) -> bool:
        """Download a single image with proper error handling."""
        # Create directory if it doesn't exist
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir, exist_ok=True)

        client = get_http_client()
        logger.debug(f"Downloading image from: {img_url}")
        logger.debug(f"Saving to: {save_path}")
        success = client.download_file(img_url, save_path)
        if success:
            logger.debug(f"Successfully downloaded image: {save_path}")
        else:
            logger.warning(f"Failed to download image: {img_url}")
        return success

    def download_images_parallel(
        self, dn_image_list: List[str], progress_callback: Optional[Callable] = None
    ) -> int:
        """Download images with parallel processing and progress tracking."""
        if not dn_image_list:
            return 0

        downloader = ParallelImageDownloader(max_workers=10)
        client = get_http_client()

        # Prepare download tasks
        image_tasks = []
        for img_url in dn_image_list:
            gallery_img_file = settings.get_image_url_to_gallery_file(img_url)
            if not os.path.isfile(gallery_img_file):
                image_tasks.append((img_url, gallery_img_file))

        # Execute parallel download
        success_count = downloader.download_images(image_tasks, progress_callback, client)

        logger.debug(f"Parallel download completed: {success_count}/{len(image_tasks)} successful")
        return success_count

    def download_images_batch(
        self, dn_image_list: List[str], batch_size: Optional[int] = None
    ) -> int:
        """Download images in batches to avoid overwhelming the server."""
        if not dn_image_list:
            return 0

        if batch_size is None:
            batch_size = settings.get_setting('gallery_download_batch_size')

        client = get_http_client()
        success_count = 0

        for i in range(0, len(dn_image_list), batch_size):
            batch = dn_image_list[i : i + batch_size]
            logger.debug(f"Processing batch {i//batch_size + 1}, {len(batch)} images")
            for img_url in batch:
                gallery_img_file = settings.get_image_url_to_gallery_file(img_url)
                if not os.path.isfile(gallery_img_file):
                    if client.download_file(img_url, gallery_img_file):
                        success_count += 1
            time.sleep(0.5)

        return success_count

    def download_images_simple(self, dn_image_list: List[str], client=None) -> int:
        """Download images for gallery with improved error handling."""
        if not dn_image_list:
            return 0

        if client is None:
            client = get_http_client()
        logger.debug(f"Starting download of {len(dn_image_list)} images")

        success_count = 0
        failed_count = 0

        for img_url in dn_image_list:
            gallery_img_file = settings.get_image_url_to_gallery_file(img_url)

            if os.path.isfile(gallery_img_file):
                logger.debug(f"Image already exists: {gallery_img_file}")
                continue

            logger.debug(f"Downloading image: {img_url}")
            if client.download_file(img_url, gallery_img_file):
                success_count += 1
                logger.debug(f"Successfully downloaded: {gallery_img_file}")
            else:
                failed_count += 1
                logger.warning(f"Failed to download: {img_url}")

        logger.debug(f"Download complete: {success_count} success, {failed_count} failed")

        if failed_count > 0:
            gr.Error(
                f"Some images failed to download ({failed_count} files), "
                "please check your network connection 💥!",
                duration=3,
            )

        return success_count

    def download_user_gallery(self, model_id: str, image_urls: List[str]) -> Optional[str]:
        """Download user gallery images to organized folder structure."""
        if not model_id:
            return None

        from ..ishortcut_core.model_processor import ModelProcessor

        modelprocessor = ModelProcessor()
        model_info = modelprocessor.get_model_info(model_id)

        if not model_info:
            return None

        image_folder = util.make_download_image_folder(model_info['name'])

        if not image_folder:
            return None

        save_folder = os.path.join(image_folder, "user_gallery_images")

        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        if image_urls:
            client = get_http_client()
            downloader = ParallelImageDownloader(max_workers=10)
            # Prepare download tasks for URLs; local filepaths are copied immediately
            image_tasks = []
            for img_url in image_urls:
                result = util.is_url_or_filepath(img_url)
                if result == "filepath":
                    if os.path.basename(img_url) != os.path.basename(
                        settings.get_no_card_preview_image()
                    ):
                        dest = os.path.join(save_folder, os.path.basename(img_url))
                        shutil.copyfile(img_url, dest)
                elif result == "url":
                    image_id, _ = os.path.splitext(os.path.basename(img_url))
                    dest = os.path.join(
                        save_folder,
                        f"{image_id}{settings.PREVIEW_IMAGE_SUFFIX}{settings.PREVIEW_IMAGE_EXT}",
                    )
                    image_tasks.append((img_url, dest))
            # Execute parallel download for remote images
            success = downloader.download_images(image_tasks, None, client)
            logger.debug(f"Parallel user gallery download: {success}/{len(image_tasks)} successful")
        return image_folder

    def load_gallery_images(
        self, images_url: List[str], progress
    ) -> Tuple[Optional[List[str]], Optional[List[str]], Optional[str]]:
        """Load gallery images with parallel processing and progress tracking."""
        if images_url:
            dn_image_list = []
            image_list = []

            if not os.path.exists(settings.shortcut_gallery_folder):
                os.makedirs(settings.shortcut_gallery_folder)

            # Collect URLs that need downloading
            urls_to_download = []
            for img_url in images_url:
                result = util.is_url_or_filepath(img_url)
                if result == "url":
                    description_img = settings.get_image_url_to_gallery_file(img_url)
                    if not os.path.isfile(description_img):
                        urls_to_download.append(img_url)

            # Perform parallel download if there are URLs to download
            if urls_to_download:
                # Create progress wrapper to bridge with Gradio progress
                try:
                    # Try to create progress bar with full parameters
                    progress_bar = progress.tqdm(
                        total=len(urls_to_download), desc="Civitai Images Loading"
                    )
                except TypeError:
                    # Fallback for simpler progress implementations that don't support total/desc
                    progress_bar = progress.tqdm(urls_to_download, desc="Civitai Images Loading")

                def progress_wrapper(done, total, desc):
                    """Wrapper to bridge parallel download progress with Gradio progress."""
                    try:
                        # Update progress bar to current completion count
                        if hasattr(progress_bar, 'n') and hasattr(progress_bar, 'update'):
                            if done > progress_bar.n:
                                progress_bar.update(done - progress_bar.n)
                    except Exception as e:
                        logger.debug(f"Progress update failed: {e}")

                # Execute parallel download
                success_count = self.download_images_parallel(urls_to_download, progress_wrapper)

                # For Gradio Progress, we don't need to manually close the progress bar
                # as it's handled automatically when the function completes
                # The close() method requires a _tqdm parameter which is not available here

                logger.debug(
                    f"Gallery parallel download: {success_count}/{len(urls_to_download)} successful"
                )

            # Build final image lists with fallback for failed downloads
            for img_url in images_url:
                result = util.is_url_or_filepath(img_url)
                description_img = settings.get_image_url_to_gallery_file(img_url)
                if result == "filepath":
                    description_img = img_url
                elif result == "url":
                    if not os.path.isfile(description_img):
                        description_img = settings.get_no_card_preview_image()
                else:
                    description_img = settings.get_no_card_preview_image()

                dn_image_list.append(description_img)
                image_list.append(description_img)

            current_time = datetime.datetime.now()
            return dn_image_list, image_list, current_time
        return None, None, gr.update(visible=False)

    def preload_next_page(self, usergal_page_url: str, paging_information: dict) -> None:
        """Preload images for next page in background."""
        if not settings.usergallery_preloading:
            return

        from .. import civitai
        from .gallery_utilities import GalleryUtilities
        from .data_processor import GalleryDataProcessor

        page_url = usergal_page_url
        data_processor = GalleryDataProcessor()
        utilities = GalleryUtilities()

        current_page = data_processor.calculate_current_page(paging_information, usergal_page_url)

        if paging_information:
            if paging_information["totalPageUrls"]:
                total_page_urls = paging_information["totalPageUrls"]
                if len(total_page_urls) > current_page:
                    page_url = total_page_urls[current_page]

        if page_url:
            image_data = None
            json_data = civitai.request_models(utilities.fix_page_url_cursor(page_url))
            try:
                image_data = json_data['items']
            except Exception as e:
                logger.error(str(e))
                return

            dn_image_list = list()

            if image_data:
                for image_info in image_data:
                    if "url" in image_info:
                        img_url = image_info['url']
                        gallery_img_file = settings.get_image_url_to_gallery_file(image_info['url'])
                        if not os.path.isfile(gallery_img_file):
                            dn_image_list.append(img_url)

            if len(dn_image_list) > 0:
                try:
                    thread = threading.Thread(
                        target=self.download_images_simple, args=(dn_image_list,)
                    )
                    thread.start()
                except Exception as e:
                    logger.error(str(e))

    def retry_failed_downloads(self) -> int:
        """Retry all previously failed downloads."""
        if not self.failed_downloads:
            return 0

        logger.debug(f"Retrying {len(self.failed_downloads)} failed downloads")

        retry_list = self.failed_downloads.copy()
        self.failed_downloads.clear()
        success_count = 0

        for img_url, save_path in retry_list:
            if self.download_single_image(img_url, save_path):
                success_count += 1
            else:
                self.failed_downloads.append((img_url, save_path))

        return success_count

    def get_download_statistics(self) -> dict:
        """Get download statistics and status."""
        return {
            'failed_downloads': len(self.failed_downloads),
            'active_downloads': len(self.active_downloads),
            'failed_urls': [url for url, _ in self.failed_downloads],
        }

    def cleanup_incomplete_downloads(self) -> int:
        """Clean up incomplete or corrupted downloads."""
        cleanup_count = 0
        gallery_folder = settings.shortcut_gallery_folder

        if not os.path.exists(gallery_folder):
            return cleanup_count

        for filename in os.listdir(gallery_folder):
            filepath = os.path.join(gallery_folder, filename)
            if os.path.isfile(filepath):
                try:
                    # Check if file is empty or very small (likely incomplete)
                    if os.path.getsize(filepath) < 100:  # Less than 100 bytes
                        os.remove(filepath)
                        cleanup_count += 1
                        logger.debug(f"Removed incomplete download: {filepath}")
                except Exception as e:
                    logger.warning(f"Failed to check/remove file {filepath}: {e}")

        return cleanup_count
