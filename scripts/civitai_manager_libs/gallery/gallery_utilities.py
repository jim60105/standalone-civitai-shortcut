"""
Gallery Utilities Module

Contains utility functions, URL processing, and compatibility management.
Extracted from civitai_gallery_action.py to follow SRP principles.
"""

import re
from ..logging_config import get_logger

logger = get_logger(__name__)


class GalleryUtilities:
    """Gallery utility functions and helper methods."""

    @staticmethod
    def extract_model_info(url):
        """Extract model ID and version ID from URL."""
        model_id_match = re.search(r'modelId=(\d+)', url)
        model_version_id_match = re.search(r'modelVersionId=(\d+)', url)

        model_id = model_id_match.group(1) if model_id_match else None
        model_version_id = model_version_id_match.group(1) if model_version_id_match else None

        return (model_id, model_version_id)

    @staticmethod
    def extract_url_cursor(url):
        """Extract cursor value from URL."""
        model_cursor_match = re.search(r'cursor=(\d+)', url)
        cursor = int(model_cursor_match.group(1)) if model_cursor_match else 0
        return cursor

    @staticmethod
    def build_default_page_url(modelId, modelVersionId=None, show_nsfw=False, limit=0):
        """Build default page URL with parameters."""
        from .. import civitai
        from .. import settings

        if limit <= 0:
            limit = settings.usergallery_images_rows_per_page * settings.usergallery_images_column

        # 200 is the maximum value
        if limit > 200:
            limit = 200

        page_url = f"{civitai.Url_ImagePage()}?limit={limit}&modelId={modelId}"

        if modelVersionId:
            page_url = f"{page_url}&modelVersionId={modelVersionId}"

        # Image API NSFW filtering is not working properly in testing.
        # So we default to the highest level allowed
        page_url = f"{page_url}&nsfw=X"
        page_url = f"{page_url}&sort=Newest"

        return page_url

    @staticmethod
    def fix_page_url_cursor(page_url, use=True):
        """Fix page URL cursor for API compatibility."""
        from .. import util

        if not use:
            return page_url

        cursor = int(GalleryUtilities.extract_url_cursor(page_url))
        if cursor > 0:
            page_url = util.update_url(page_url, "cursor", cursor + 1)
        return page_url

    @staticmethod
    def validate_model_id(model_id):
        """Validate model ID format."""
        if not model_id:
            return False
        try:
            int(model_id)
            return True
        except (ValueError, TypeError):
            return False

    @staticmethod
    def validate_url_format(url):
        """Validate URL format."""
        if not url or not isinstance(url, str):
            return False
        return url.startswith(('http://', 'https://'))

    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename for safe file operations."""
        if not filename:
            return "unknown"
        # Remove invalid characters for filenames
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename

    @staticmethod
    def calculate_pagination_range(total_pages, current_page, window_size=5):
        """Calculate pagination display range."""
        if total_pages <= window_size:
            return 1, total_pages

        half_window = window_size // 2
        start = max(1, current_page - half_window)
        end = min(total_pages, start + window_size - 1)

        # Adjust start if we're at the end
        if end - start + 1 < window_size:
            start = max(1, end - window_size + 1)

        return start, end


class CompatibilityManager:
    """Manage compatibility layer integration."""

    def __init__(self):
        self._compat_layer = None

    def set_compatibility_layer(self, compat_layer):
        """Set compatibility layer instance."""
        self._compat_layer = compat_layer
        logger.debug(f"Compatibility layer set: {compat_layer}")

    def get_compatibility_layer(self):
        """Get current compatibility layer instance."""
        return self._compat_layer

    def is_standalone_mode(self):
        """Check if running in standalone mode."""
        if self._compat_layer and hasattr(self._compat_layer, 'is_standalone_mode'):
            return self._compat_layer.is_standalone_mode()
        return False

    def is_webui_mode(self):
        """Check if running in WebUI mode."""
        if self._compat_layer and hasattr(self._compat_layer, 'is_webui_mode'):
            return self._compat_layer.is_webui_mode()
        return True  # Default to WebUI mode if no compatibility layer
