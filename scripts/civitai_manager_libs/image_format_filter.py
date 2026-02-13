"""
Image Format Filter Module

Provides utilities to filter and validate static image formats.
Filters out dynamic formats like GIF, WebM, MP4 to support only static thumbnails.
"""

import os
from typing import Dict, List, Optional
from urllib.parse import urlparse

from .logging_config import get_logger
from .settings.constants import STATIC_IMAGE_EXTENSIONS, DYNAMIC_IMAGE_EXTENSIONS

logger = get_logger(__name__)

# Civitai API image type values that indicate video/animated content
_DYNAMIC_IMAGE_TYPES = {"video", "animation"}


class ImageFormatFilter:
    """Filter and validate image formats to support only static images."""

    @staticmethod
    def is_static_image_dict(image_dict: Dict) -> bool:
        """
        Check if a Civitai API image dict represents a static image.

        Checks both the ``type`` field from the API response and the URL
        extension.  Returns False when the ``type`` field indicates video /
        animation content **or** the URL has a known dynamic extension.

        Args:
            image_dict: Single image object from Civitai API response.

        Returns:
            True only when the image is considered static.
        """
        if not image_dict or not isinstance(image_dict, dict):
            return False

        # Check the API "type" field first – this is the most reliable signal
        img_type = str(image_dict.get("type", "")).lower()
        if img_type in _DYNAMIC_IMAGE_TYPES:
            logger.debug(
                f"[ImageFormatFilter] Rejected image with type={img_type}: "
                f"{image_dict.get('url', '(no url)')}"
            )
            return False

        # Fall back to URL-extension check
        url = image_dict.get("url", "")
        return ImageFormatFilter.is_static_image(url)

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
                # If path is empty, it might be a malformed URL like http://img.jpg
                # Try to extract extension from the entire URL after the scheme
                if not path or path == '/':
                    # Remove the scheme and try to get extension from the rest
                    remainder = url_or_path[url_or_path.find('://') + 3 :]
                    _, ext = os.path.splitext(remainder.lower())
                else:
                    _, ext = os.path.splitext(path.lower())
            else:
                # Handle file path
                _, ext = os.path.splitext(url_or_path.lower())

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
                # If path is empty, it might be a malformed URL like http://img.gif
                # Try to extract extension from the entire URL after the scheme
                if not path or path == '/':
                    # Remove the scheme and try to get extension from the rest
                    remainder = url_or_path[url_or_path.find('://') + 3 :]
                    _, ext = os.path.splitext(remainder.lower())
                else:
                    _, ext = os.path.splitext(path.lower())
            else:
                # Handle file path
                _, ext = os.path.splitext(url_or_path.lower())

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
    def is_valid_static_image_file(filepath: str) -> bool:
        """
        Check if a local file is actually a valid static image by inspecting magic bytes.

        Returns False for files whose content is MP4, GIF, or other non-static formats
        even if the file extension suggests a static image.
        """
        if not filepath or not os.path.isfile(filepath):
            return False

        try:
            with open(filepath, 'rb') as fh:
                header = fh.read(16)

            if len(header) < 4:
                return False

            # Check for known static image magic bytes first
            is_png = header[:4] == b'\x89PNG'
            is_jpeg = header[:3] == b'\xff\xd8\xff'
            is_webp = header[:4] == b'RIFF' and header[8:12] == b'WEBP'
            is_avif = header[4:8] == b'ftyp' and header[8:12] in (b'avif', b'avis', b'mif1')

            if is_png or is_jpeg or is_webp or is_avif:
                return True

            # Reject video/animation formats
            if header[4:8] == b'ftyp':  # MP4/MOV (non-AVIF ftyp)
                logger.debug(f"[ImageFormatFilter] File is MP4/MOV: {filepath}")
                return False
            if header[:3] == b'GIF':
                logger.debug(f"[ImageFormatFilter] File is GIF: {filepath}")
                return False
            if header[:4] == b'\x1a\x45\xdf\xa3':  # WebM/MKV
                logger.debug(f"[ImageFormatFilter] File is WebM: {filepath}")
                return False

            logger.debug(
                f"[ImageFormatFilter] Unrecognized file format: {filepath} "
                f"(header: {header[:8].hex()})"
            )
            return False

        except Exception as e:
            logger.warning(f"[ImageFormatFilter] Error checking file {filepath}: {e}")
            return False

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
