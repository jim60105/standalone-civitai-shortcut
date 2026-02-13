"""
preview_image_manager.py - Manages model preview images for gallery display.

This module provides the PreviewImageManager class to handle preview image
URL extraction, download, caching, and cleanup.
"""

import os
from typing import Dict, Any, Optional

from ..logging_config import get_logger
from .. import settings
from ..util import download_image_safe
from ..http import get_http_client
from .shortcut_collection_manager import ShortcutCollectionManager

logger = get_logger(__name__)


class PreviewImageManager:
    """Manages model preview images for gallery display."""

    def __init__(self, collection_manager: ShortcutCollectionManager):
        self._collection_manager = collection_manager

    def get_preview_image_url(self, model_info: Dict[str, Any]) -> Optional[str]:
        """Extract optimal preview image URL from model info, static images only."""
        if not model_info:
            return None
        try:
            from ..image_format_filter import ImageFormatFilter

            # Try modelVersions first
            if "modelVersions" in model_info and model_info["modelVersions"]:
                for version in model_info["modelVersions"]:
                    if "images" in version and version["images"]:
                        for image in version["images"]:
                            url = image.get("url")
                            if url and ImageFormatFilter.is_static_image_dict(image):
                                return url
            # Fallback to direct images in model_info
            if "images" in model_info and model_info["images"]:
                for image in model_info["images"]:
                    url = image.get("url")
                    if url and ImageFormatFilter.is_static_image_dict(image):
                        return url
        except Exception:
            logger.error("Error extracting preview URL", exc_info=True)
        return None

    def get_preview_image_path(self, model_info: Dict[str, Any]) -> Optional[str]:
        """Generate local path for preview image storage."""
        model_id = model_info.get("id") if model_info else None
        if not model_id:
            return None
        try:
            preview_dir = settings.shortcut_thumbnail_folder
            os.makedirs(preview_dir, exist_ok=True)
            filename = f"model_{model_id}_preview.jpg"
            return os.path.join(preview_dir, filename)
        except Exception:
            logger.error("Error generating preview image path", exc_info=True)
            return None

    def download_preview_image(self, model_info: Dict[str, Any]) -> Optional[str]:
        """Download model preview image with error handling."""
        url = self.get_preview_image_url(model_info)
        if not url:
            logger.warning("No preview image URL found")
            return None
        path = self.get_preview_image_path(model_info)
        if not path:
            return None
        if os.path.exists(path):
            logger.info(f"Preview image already exists: {path}")
            return path
        client = get_http_client()
        success = download_image_safe(url, path, client, show_error=False)
        if success:
            logger.info(f"Successfully downloaded preview image: {path}")
            return path
        logger.error(f"Failed to download preview image: {url}")
        return None

    def get_preview_image(self, model_info: Dict[str, Any]) -> str:
        """Get preview image path, download if not exists, or fallback."""
        path = self.get_preview_image_path(model_info)
        if path and os.path.exists(path):
            return path
        downloaded = self.download_preview_image(model_info)
        if downloaded:
            return downloaded
        return settings.get_no_card_preview_image()

    def cleanup_unused_previews(self) -> int:
        """Remove preview images for models no longer in shortcuts."""
        removed = 0
        try:
            shortcuts = self._collection_manager.load_shortcuts()
            valid_ids = {str(mid) for mid in shortcuts.keys()}
            preview_dir = settings.shortcut_thumbnail_folder
            for fname in os.listdir(preview_dir):
                if fname.startswith("model_") and fname.endswith("_preview.jpg"):
                    mid = fname[len("model_") : -len("_preview.jpg")]
                    if mid not in valid_ids:
                        path = os.path.join(preview_dir, fname)
                        os.remove(path)
                        removed += 1
                        logger.info(f"Removed unused preview image: {path}")
        except Exception:
            logger.error("Error cleaning up unused previews", exc_info=True)
        return removed
