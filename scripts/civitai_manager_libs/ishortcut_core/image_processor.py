"""
ImageProcessor: Handles image downloading and thumbnail generation.

This module is responsible for:
- Downloading model preview images and galleries
- Generating thumbnails with proper sizing
- Managing image file operations
- NSFW filtering and image validation
- Parallel image download operations

Extracted from ishortcut.py functions:
- _download_model_images()
- _collect_images_to_download()
- _perform_image_downloads()
- download_thumbnail_image()
- create_thumbnail()
- delete_thumbnail_image()
- is_sc_image()
- get_preview_image_by_model_info()
- download_model_preview_image_by_model_info()
"""

import os
from typing import Dict, List, Optional, Tuple, Callable

# Import PIL only when needed to avoid import errors
try:
    from PIL import Image
except ImportError:
    Image = None

# Import dependencies from parent modules
from .. import util
from .. import settings
from ..logging_config import get_logger
from ..http_client import get_http_client, ParallelImageDownloader
from ..error_handler import with_error_handling
from ..exceptions import NetworkError, FileOperationError, CivitaiShortcutError

logger = get_logger(__name__)

# Thumbnail configuration
THUMBNAIL_MAX_SIZE = (400, 400)


class ImageProcessor:
    """Handles image downloading and thumbnail generation operations."""

    def __init__(self):
        """Initialize ImageProcessor."""
        self.thumbnail_max_size = THUMBNAIL_MAX_SIZE

    @with_error_handling(
        fallback_value=None,
        exception_types=(NetworkError, FileOperationError, CivitaiShortcutError),
        retry_count=1,
        retry_delay=1.0,
        user_message="Failed to download model images",
    )
    def download_model_images(
        self, version_list: List[List], modelid: str, progress: Optional[Callable] = None
    ) -> bool:
        """
        Download images for all model versions.

        Args:
            version_list: List of image lists for each version
            modelid: Model ID for debug logging
            progress: Progress callback for UI updates

        Returns:
            True if download was successful, False otherwise
        """
        if not version_list:
            logger.info(f"[ImageProcessor] No images to download for {modelid}")
            return True

        logger.info(f"[ImageProcessor] Starting image downloads for model {modelid}")

        # Ensure latest configuration values loaded before downloading
        from ..settings.path_manager import load_model_folder_data
        from ..settings import config_manager
        load_model_folder_data(config_manager)
        logger.debug(
            f"[ImageProcessor] Current shortcut_max_download_image_per_version: "
            f"{settings.shortcut_max_download_image_per_version}"
        )

        # Get HTTP client for downloads
        try:
            client = get_http_client()
            logger.debug("[ImageProcessor] HTTP client obtained successfully")
        except Exception as e:
            logger.error(f"[ImageProcessor] Failed to get HTTP client: {e}")
            return False

        # Collect all images that need downloading
        all_images_to_download = self._collect_images_to_download(version_list, modelid)

        if not all_images_to_download:
            logger.info(f"[ImageProcessor] No new images to download for {modelid}")
            return True

        # Download images with progress tracking
        success = self._perform_image_downloads(all_images_to_download, client, progress)

        if success:
            logger.info(f"[ImageProcessor] Image downloads completed for {modelid}")
        else:
            logger.warning(f"[ImageProcessor] Some image downloads failed for {modelid}")

        return success

    @with_error_handling(
        fallback_value=[],
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to collect images to download",
    )
    def _collect_images_to_download(self, version_list: List[List], modelid: str) -> List[Tuple]:
        """
        Collect images that need to be downloaded (don't already exist).

        Args:
            version_list: List of image lists for each version
            modelid: Model ID for debug logging

        Returns:
            List of (version_id, url, filepath) tuples to download
        """
        logger.info(f"[ImageProcessor] Collecting images for {modelid}")
        logger.debug(
            "[ImageProcessor] "
            f"shortcut_max_download_image_per_version = "
            f"{settings.shortcut_max_download_image_per_version}"
        )
        all_images_to_download = []

        for version_idx, image_list in enumerate(version_list):
            logger.debug(f"[ImageProcessor] Processing version {version_idx+1}/{len(version_list)}")
            images_for_version = []

            for img_idx, (vid, url) in enumerate(image_list):
                description_img = settings.get_image_url_to_shortcut_file(modelid, vid, url)

                if os.path.exists(description_img):
                    logger.debug(
                        f"[ImageProcessor] Image {img_idx+1} already exists: {description_img}"
                    )
                    continue

                images_for_version.append((vid, url, description_img))
                logger.info(f"[ImageProcessor] Added image {img_idx+1} for download: {url}")

            # Apply per-version download limit
            if (
                settings.shortcut_max_download_image_per_version
                and len(images_for_version) > settings.shortcut_max_download_image_per_version
            ):
                original_count = len(images_for_version)
                images_for_version = images_for_version[
                    : settings.shortcut_max_download_image_per_version
                ]
                logger.info(
                    f"[ImageProcessor] Limited images from "
                    f"{original_count} to {len(images_for_version)} per version limit"
                )
            else:
                logger.debug(
                    f"[ImageProcessor] No limit applied: "
                    f"settings={settings.shortcut_max_download_image_per_version}, "
                    f"count={len(images_for_version)}"
                )

            all_images_to_download.extend(images_for_version)

        logger.info(f"[ImageProcessor] Total images to download: {len(all_images_to_download)}")
        return all_images_to_download

    @with_error_handling(
        fallback_value=False,
        exception_types=(Exception,),
        retry_count=0,
        user_message="Failed to perform image downloads",
    )
    def _perform_image_downloads(
        self, all_images_to_download: List[Tuple], client, progress: Optional[Callable] = None
    ) -> bool:
        """Perform parallel image downloads with progress tracking."""
        if not all_images_to_download:
            return True

        logger.info(
            f"[ImageProcessor] Starting parallel downloads for {len(all_images_to_download)} images"
        )

        # Prepare download tasks
        image_tasks = [(url, filepath) for _, url, filepath in all_images_to_download]

        # Setup progress wrapper matching progress_callback signature (done, total, desc)
        def progress_wrapper(done, total, desc):
            # Only update progress if a valid Progress callback was provided
            if progress is not None:
                try:
                    # Convert completed count to progress fraction
                    progress(done / total if total else 0, desc=desc)
                except Exception as e:
                    logger.debug(f"[ImageProcessor] Progress update failed: {e}")

        # Execute parallel download
        downloader = ParallelImageDownloader(max_workers=10)
        success_count = downloader.download_images(image_tasks, progress_wrapper)

        logger.debug(
            f"[ImageProcessor] Parallel downloads completed: "
            f"{success_count}/{len(all_images_to_download)} successful"
        )

        # Consider operation successful if majority of downloads succeeded
        download_count = len(all_images_to_download)
        success_rate = success_count / download_count if download_count else 1.0
        return success_rate >= 0.8  # 80% success rate threshold

    def download_thumbnail_image(self, model_id: str, url: str) -> bool:
        """
        Download and generate thumbnail for a shortcut image.

        Args:
            model_id: Model ID for thumbnail naming
            url: URL of image to download

        Returns:
            True if download and thumbnail generation was successful
        """
        if not model_id or not url:
            logger.warning("[ImageProcessor] Invalid model_id or url for thumbnail download")
            return False

        logger.info(f"[ImageProcessor] Downloading thumbnail for model {model_id}")

        # Ensure thumbnail directory exists
        os.makedirs(settings.shortcut_thumbnail_folder, exist_ok=True)

        thumbnail_path = os.path.join(
            settings.shortcut_thumbnail_folder, f"{model_id}{settings.preview_image_ext}"
        )

        try:
            # Download image
            client = get_http_client()
            if not util.download_image_safe(url, thumbnail_path, client, show_error=False):
                logger.warning(f"[ImageProcessor] Failed to download image from {url}")
                return False

            # Generate thumbnail
            return self.create_thumbnail_from_file(model_id, thumbnail_path)

        except Exception as e:
            logger.error(f"[ImageProcessor] Error downloading thumbnail for {model_id}: {e}")
            return False

    def create_thumbnail(self, model_id: str, input_image_path: str) -> bool:
        """
        Create thumbnail from an existing image file.

        Args:
            model_id: Model ID for thumbnail naming
            input_image_path: Path to source image

        Returns:
            True if thumbnail creation was successful
        """
        if not model_id or not input_image_path:
            logger.warning("[ImageProcessor] Invalid parameters for thumbnail creation")
            return False

        if not os.path.exists(input_image_path):
            logger.warning(f"[ImageProcessor] Source image doesn't exist: {input_image_path}")
            return False

        thumbnail_path = os.path.join(
            settings.shortcut_thumbnail_folder, f"{model_id}{settings.preview_image_ext}"
        )

        try:
            # Ensure thumbnail directory exists
            os.makedirs(settings.shortcut_thumbnail_folder, exist_ok=True)

            # Create thumbnail
            with Image.open(input_image_path) as image:
                image.thumbnail(self.thumbnail_max_size)
                image.save(thumbnail_path)

            logger.info(f"[ImageProcessor] Created thumbnail: {thumbnail_path}")
            return True

        except Exception as e:
            logger.error(f"[ImageProcessor] Failed to create thumbnail for {model_id}: {e}")
            return False

    def create_thumbnail_from_file(self, model_id: str, image_file_path: str) -> bool:
        """
        Create thumbnail from downloaded image file.

        Args:
            model_id: Model ID for thumbnail naming
            image_file_path: Path to downloaded image file

        Returns:
            True if thumbnail creation was successful
        """
        try:
            with Image.open(image_file_path) as image:
                image.thumbnail(self.thumbnail_max_size)
                image.save(image_file_path)  # Save thumbnail over original

            logger.info(f"[ImageProcessor] Generated thumbnail for model {model_id}")
            return True

        except Exception as e:
            logger.warning(
                f"[ImageProcessor] Thumbnail generation failed for {image_file_path}: {e}"
            )
            return False

    def delete_thumbnail_image(self, model_id: str) -> bool:
        """
        Delete thumbnail image for a model.

        Args:
            model_id: Model ID to delete thumbnail for

        Returns:
            True if deletion was successful or file didn't exist
        """
        if not model_id:
            return False

        if not self.is_sc_image(model_id):
            logger.debug(f"[ImageProcessor] No thumbnail to delete for model {model_id}")
            return True

        thumbnail_path = os.path.join(
            settings.shortcut_thumbnail_folder, f"{model_id}{settings.preview_image_ext}"
        )

        try:
            os.remove(thumbnail_path)
            logger.info(f"[ImageProcessor] Deleted thumbnail for model {model_id}")
            return True
        except Exception as e:
            logger.error(f"[ImageProcessor] Failed to delete thumbnail for {model_id}: {e}")
            return False

    def is_sc_image(self, model_id: str) -> bool:
        """
        Check if thumbnail image exists for a model.

        Args:
            model_id: Model ID to check

        Returns:
            True if thumbnail exists, False otherwise
        """
        if not model_id:
            return False

        thumbnail_path = os.path.join(
            settings.shortcut_thumbnail_folder, f"{model_id}{settings.preview_image_ext}"
        )

        exists = os.path.isfile(thumbnail_path)
        logger.debug(f"[ImageProcessor] Thumbnail exists for {model_id}: {exists}")
        return exists

    def get_preview_image_url(self, model_info: Dict) -> Optional[str]:
        """
        Extract preview image URL from model info.

        Args:
            model_info: Model information dictionary

        Returns:
            Preview image URL or None if not found
        """
        try:
            # Try to get from model versions
            if 'modelVersions' in model_info and model_info['modelVersions']:
                for version in model_info['modelVersions']:
                    if 'images' in version and version['images']:
                        for image in version['images']:
                            url = image.get('url')
                            if url:
                                logger.debug(
                                    f"[ImageProcessor] Found preview URL in version: {url}"
                                )
                                return url

            # Try to get from direct images
            if 'images' in model_info and model_info['images']:
                for image in model_info['images']:
                    url = image.get('url')
                    if url:
                        logger.debug(f"[ImageProcessor] Found preview URL in model: {url}")
                        return url

            logger.debug("[ImageProcessor] No preview image URL found")
            return None

        except Exception as e:
            logger.error(f"[ImageProcessor] Error extracting preview URL: {e}")
            return None

    def get_preview_image_path(self, model_info: Dict) -> Optional[str]:
        """
        Generate local path for preview image.

        Args:
            model_info: Model information dictionary

        Returns:
            Local path for preview image or None if invalid
        """
        try:
            model_id = model_info.get('id')
            if not model_id:
                return None

            # Ensure preview directory exists
            preview_dir = settings.shortcut_thumbnail_folder
            os.makedirs(preview_dir, exist_ok=True)

            filename = f"model_{model_id}_preview.jpg"
            path = os.path.join(preview_dir, filename)

            logger.debug(f"[ImageProcessor] Generated preview image path: {path}")
            return path

        except Exception as e:
            logger.error(f"[ImageProcessor] Error generating image path: {e}")
            return None

    def download_model_preview_image_by_model_info(self, model_info: Dict) -> Optional[str]:
        """
        Download model preview image with improved error handling.

        Args:
            model_info: Model information dictionary

        Returns:
            Path to downloaded image or None if failed
        """
        if not model_info:
            logger.error(
                "[ImageProcessor] download_model_preview_image_by_model_info: model_info is None"
            )
            return None

        model_id = model_info.get('id')
        if not model_id:
            logger.error(
                "[ImageProcessor] download_model_preview_image_by_model_info: model_id not found"
            )
            return None

        logger.info(f"[ImageProcessor] Downloading preview image for model: {model_id}")

        preview_url = self.get_preview_image_url(model_info)
        if not preview_url:
            logger.warning("[ImageProcessor] No preview image URL found")
            return None

        image_path = self.get_preview_image_path(model_info)
        if not image_path:
            logger.error("[ImageProcessor] Failed to generate image path")
            return None

        if os.path.exists(image_path):
            logger.info(f"[ImageProcessor] Preview image already exists: {image_path}")
            return image_path

        try:
            client = get_http_client()
            success = util.download_image_safe(preview_url, image_path, client, show_error=False)

            if success:
                logger.info(f"[ImageProcessor] Successfully downloaded preview image: {image_path}")
                return image_path
            else:
                logger.error(f"[ImageProcessor] Failed to download preview image: {preview_url}")
                return None

        except Exception as e:
            logger.error(f"[ImageProcessor] Error downloading preview image: {e}")
            return None

    def get_preview_image_by_model_info(self, model_info: Dict) -> str:
        """
        Get preview image, download if not exists.

        Args:
            model_info: Model information dictionary

        Returns:
            Path to preview image (local or fallback)
        """
        if not model_info:
            logger.error("[ImageProcessor] get_preview_image_by_model_info: model_info is None")
            return settings.no_card_preview_image

        image_path = self.get_preview_image_path(model_info)

        if image_path and os.path.exists(image_path):
            logger.info(f"[ImageProcessor] Using existing preview image: {image_path}")
            return image_path

        downloaded_path = self.download_model_preview_image_by_model_info(model_info)
        if downloaded_path:
            return downloaded_path

        logger.info("[ImageProcessor] Using fallback preview image")
        return settings.no_card_preview_image

    def extract_version_images(self, model_info: Dict, modelid: str) -> List[List]:
        """
        Extract image information from model versions.

        Args:
            model_info: Model information from Civitai API
            modelid: Model ID for debug logging

        Returns:
            List of image lists for each version
        """
        logger.info(f"[ImageProcessor] Processing versions for model {modelid}")
        version_list = []

        if "modelVersions" not in model_info:
            logger.warning(f"[ImageProcessor] No modelVersions found for {modelid}")
            return version_list

        version_count = len(model_info["modelVersions"])
        logger.info(f"[ImageProcessor] Found {version_count} versions")

        for idx, version_info in enumerate(model_info["modelVersions"]):
            version_id = version_info.get('id')
            logger.debug(
                f"[ImageProcessor] Processing version {idx+1}/{version_count}, ID: {version_id}"
            )

            if not version_id:
                logger.warning(f"[ImageProcessor] Version {idx+1} has no ID, skipping")
                continue

            if "images" not in version_info:
                logger.warning(f"[ImageProcessor] Version {version_id} has no images")
                continue

            image_list = self._process_version_images(version_info["images"], version_id)
            if image_list:
                version_list.append(image_list)
                logger.info(
                    f"[ImageProcessor] Added {len(image_list)} images for version {version_id}"
                )
            else:
                logger.warning(f"[ImageProcessor] No valid images found for version {version_id}")

        logger.debug(f"[ImageProcessor] Processed {len(version_list)} versions with images")
        return version_list

    def _process_version_images(self, images: List[Dict], version_id: str) -> List[List]:
        """
        Process images for a specific version.

        Args:
            images: List of image data from API
            version_id: Version ID for this set of images

        Returns:
            List of [version_id, img_url] pairs
        """
        image_list = []
        image_count = len(images)
        logger.info(f"[ImageProcessor] Processing {image_count} images for version {version_id}")

        for idx, img in enumerate(images):
            if "url" not in img:
                logger.warning(f"[ImageProcessor] Image {idx+1}/{image_count} has no URL, skipping")
                continue

            img_url = img["url"]

            # Use max width if available
            if "width" in img and img["width"]:
                original_url = img_url
                img_url = util.change_width_from_image_url(img_url, img["width"])
                logger.debug(
                    f"[ImageProcessor] Adjusted image URL width: {original_url} -> {img_url}"
                )

            image_list.append([version_id, img_url])
            logger.debug(f"[ImageProcessor] Added image {idx+1}/{image_count}: {img_url}")

        return image_list
