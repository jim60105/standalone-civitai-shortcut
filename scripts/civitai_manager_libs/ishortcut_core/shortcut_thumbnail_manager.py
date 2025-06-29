"""
shortcut_thumbnail_manager.py - Manages thumbnail operations for shortcut collections.

This module provides the ShortcutThumbnailManager class to handle batch thumbnail
updates and NSFW level management for shortcut collections.
"""

from typing import Dict, Any

from ..logging_config import get_logger

from .image_processor import ImageProcessor
from .shortcut_collection_manager import ShortcutCollectionManager

from .. import civitai
from .. import setting

logger = get_logger(__name__)


class ShortcutThumbnailManager:
    """Manages thumbnail operations for shortcut collections."""

    def __init__(
        self,
        image_processor: ImageProcessor,
        collection_manager: ShortcutCollectionManager,
    ):
        self._image_processor = image_processor
        self._collection_manager = collection_manager

    def update_all_thumbnails(self, progress: Any) -> None:
        """Batch update thumbnails for all shortcuts."""
        shortcuts = self._collection_manager.load_shortcuts()
        if not shortcuts:
            return

        for shortcut_id, shortcut_data in progress.tqdm(
            shortcuts.items(), desc="Update Shortcut's Thumbnails"
        ):
            if not shortcut_data:
                continue
            try:
                self._update_shortcut_thumbnail(shortcut_data)
            except Exception:
                logger.error(
                    f"Failed to update thumbnail for shortcut {shortcut_id}",
                    exc_info=True,
                )

        # Save all updates
        self._collection_manager.save_shortcuts(shortcuts)

    def select_optimal_image(self, images: list) -> str:
        """Select best image based on NSFW level preferences."""
        if not images:
            return ""

        cur_nsfw_level = len(setting.NSFW_levels)
        selected_url = ""
        for img in images:
            try:
                level = self._calculate_nsfw_level(img)
            except Exception:
                logger.warning("Error calculating NSFW level, skipping image", exc_info=True)
                continue

            if level < cur_nsfw_level:
                cur_nsfw_level = level
                selected_url = img.get("url", "")

        if not selected_url:
            selected_url = images[0].get("url", "")

        return selected_url

    def _calculate_nsfw_level(self, image_dict: Dict[str, Any]) -> int:
        """Calculate NSFW level from image metadata."""
        if "nsfwLevel" in image_dict:
            level = image_dict.get("nsfwLevel", 1) - 1
            return max(level, 0)

        if "nsfw" in image_dict:
            try:
                return setting.NSFW_levels.index(image_dict["nsfw"])
            except ValueError:
                logger.debug("Unknown NSFW tag, defaulting to max level")

        return len(setting.NSFW_levels)

    def _update_shortcut_thumbnail(self, shortcut_data: Dict[str, Any]) -> None:
        """Update thumbnail for single shortcut."""
        version_info = civitai.get_latest_version_info_by_model_id(shortcut_data.get("id"))
        if not version_info or "images" not in version_info:
            return

        url = self.select_optimal_image(version_info["images"])
        if not url:
            return

        shortcut_data["imageurl"] = url
        # Download and generate thumbnail
        self._image_processor.download_thumbnail_image(shortcut_data.get("id"), url)

    def batch_download_thumbnails(self, shortcuts: Dict[str, Any], progress: Any) -> None:
        """Batch download thumbnails with progress tracking."""
        if not shortcuts:
            return

        for shortcut_id, shortcut_data in progress.tqdm(
            shortcuts.items(), desc="Download Shortcut Thumbnails"
        ):
            image_url = shortcut_data.get("imageurl")
            if not image_url:
                continue

            try:
                self._image_processor.download_thumbnail_image(shortcut_id, image_url)
            except Exception:
                logger.error(
                    f"Failed to download thumbnail for shortcut {shortcut_id}",
                    exc_info=True,
                )
