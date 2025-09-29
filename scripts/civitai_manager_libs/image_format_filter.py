"""
Image Format Filter Module

Provides utilities to filter and validate static image formats.
Filters out dynamic formats like GIF, WebM, MP4 to support only static thumbnails.
"""

import os
from typing import List, Optional
from urllib.parse import urlparse

from .logging_config import get_logger
from .settings.constants import STATIC_IMAGE_EXTENSIONS, DYNAMIC_IMAGE_EXTENSIONS

logger = get_logger(__name__)


class ImageFormatFilter:
    """Filter and validate image formats to support only static images."""

    @staticmethod
    def is_static_image(url_or_path: str) -> bool:
        """
        Check if image is static format.

        Args:
            url_or_path: URL or file path to check

        Returns:
            True if image is static format (JPG, PNG, WebP, AVIF), False otherwise
        """
        if not url_or_path:
            return False

        try:
            # Extract file extension
            if url_or_path.startswith(('http://', 'https://')):
                # Handle URL - extract path from URL
                parsed = urlparse(url_or_path)
                path = parsed.path
            else:
                # Handle file path
                path = url_or_path

            # Get file extension
            _, ext = os.path.splitext(path.lower())

            # Remove query parameters if present in URL
            if '?' in ext:
                ext = ext.split('?')[0]

            is_static = ext in STATIC_IMAGE_EXTENSIONS
            logger.debug(f"[ImageFormatFilter] {url_or_path} -> {ext} -> static: {is_static}")
            return is_static

        except Exception as e:
            logger.warning(f"[ImageFormatFilter] Error checking format for {url_or_path}: {e}")
            return False

    @staticmethod
    def is_dynamic_image(url_or_path: str) -> bool:
        """
        Check if image is dynamic format.

        Args:
            url_or_path: URL or file path to check

        Returns:
            True if image is dynamic format (GIF, WebM, MP4, MOV), False otherwise
        """
        if not url_or_path:
            return False

        try:
            # Extract file extension
            if url_or_path.startswith(('http://', 'https://')):
                # Handle URL - extract path from URL
                parsed = urlparse(url_or_path)
                path = parsed.path
            else:
                # Handle file path
                path = url_or_path

            # Get file extension
            _, ext = os.path.splitext(path.lower())

            # Remove query parameters if present in URL
            if '?' in ext:
                ext = ext.split('?')[0]

            is_dynamic = ext in DYNAMIC_IMAGE_EXTENSIONS
            logger.debug(f"[ImageFormatFilter] {url_or_path} -> {ext} -> dynamic: {is_dynamic}")
            return is_dynamic

        except Exception as e:
            logger.warning(f"[ImageFormatFilter] Error checking format for {url_or_path}: {e}")
            return False

    @classmethod
    def filter_static_urls(cls, urls: List[str]) -> List[str]:
        """
        Filter list to include only static image URLs.

        Args:
            urls: List of URLs to filter

        Returns:
            List containing only URLs with static image formats
        """
        if not urls:
            return []

        static_urls = []
        filtered_count = 0

        for url in urls:
            if cls.is_static_image(url):
                static_urls.append(url)
            else:
                filtered_count += 1
                logger.debug(f"[ImageFormatFilter] Filtered dynamic image: {url}")

        logger.info(
            f"[ImageFormatFilter] Filtered {filtered_count} dynamic images, "
            f"keeping {len(static_urls)} static images"
        )

        return static_urls

    @classmethod
    def get_static_extension(cls, url: str) -> Optional[str]:
        """
        Get static image extension from URL.

        Args:
            url: URL to extract extension from

        Returns:
            Static image extension if valid, None otherwise
        """
        if not cls.is_static_image(url):
            return None

        try:
            if url.startswith(('http://', 'https://')):
                parsed = urlparse(url)
                path = parsed.path
            else:
                path = url

            _, ext = os.path.splitext(path.lower())

            # Remove query parameters if present
            if '?' in ext:
                ext = ext.split('?')[0]

            return ext if ext in STATIC_IMAGE_EXTENSIONS else None

        except Exception as e:
            logger.warning(f"[ImageFormatFilter] Error extracting extension from {url}: {e}")
            return None

    @staticmethod
    def get_supported_formats() -> List[str]:
        """
        Get list of supported static image formats.

        Returns:
            List of supported static image extensions
        """
        return STATIC_IMAGE_EXTENSIONS.copy()

    @staticmethod
    def get_filtered_formats() -> List[str]:
        """
        Get list of filtered dynamic image formats.

        Returns:
            List of filtered dynamic image extensions
        """
        return DYNAMIC_IMAGE_EXTENSIONS.copy()
