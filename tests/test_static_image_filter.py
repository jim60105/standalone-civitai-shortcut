"""Tests for static image format filtering functionality."""

import unittest
import tempfile
import os
import sys

# Add scripts to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

from scripts.civitai_manager_libs.image_format_filter import ImageFormatFilter
from scripts.civitai_manager_libs.settings.constants import (
    STATIC_IMAGE_EXTENSIONS,
    DYNAMIC_IMAGE_EXTENSIONS,
)


class TestImageFormatFilter(unittest.TestCase):
    """Test suite for ImageFormatFilter class."""

    def test_is_static_image_file_paths(self):
        """Test static image detection for file paths."""
        # Test static formats
        self.assertTrue(ImageFormatFilter.is_static_image('/path/to/image.jpg'))
        self.assertTrue(ImageFormatFilter.is_static_image('/path/to/image.jpeg'))
        self.assertTrue(ImageFormatFilter.is_static_image('/path/to/image.png'))
        self.assertTrue(ImageFormatFilter.is_static_image('/path/to/image.webp'))
        self.assertTrue(ImageFormatFilter.is_static_image('/path/to/image.avif'))

        # Test case insensitive
        self.assertTrue(ImageFormatFilter.is_static_image('/path/to/IMAGE.JPG'))
        self.assertTrue(ImageFormatFilter.is_static_image('/path/to/IMAGE.PNG'))

        # Test dynamic formats (should be False)
        self.assertFalse(ImageFormatFilter.is_static_image('/path/to/image.gif'))
        self.assertFalse(ImageFormatFilter.is_static_image('/path/to/video.webm'))
        self.assertFalse(ImageFormatFilter.is_static_image('/path/to/video.mp4'))
        self.assertFalse(ImageFormatFilter.is_static_image('/path/to/video.mov'))

    def test_is_static_image_urls(self):
        """Test static image detection for URLs."""
        # Test static format URLs
        assert ImageFormatFilter.is_static_image('https://example.com/image.jpg') is True
        assert ImageFormatFilter.is_static_image('https://example.com/image.png') is True
        assert ImageFormatFilter.is_static_image('https://example.com/image.webp') is True

        # Test URLs with query parameters
        assert ImageFormatFilter.is_static_image('https://example.com/image.jpg?width=512') is True
        assert ImageFormatFilter.is_static_image('https://example.com/image.png?v=1') is True

        # Test dynamic format URLs (should be False)
        assert ImageFormatFilter.is_static_image('https://example.com/image.gif') is False
        assert (
            ImageFormatFilter.is_static_image('https://example.com/video.webm?width=512') is False
        )

    def test_is_dynamic_image_file_paths(self):
        """Test dynamic image detection for file paths."""
        # Test dynamic formats
        assert ImageFormatFilter.is_dynamic_image('/path/to/image.gif') is True
        assert ImageFormatFilter.is_dynamic_image('/path/to/video.webm') is True
        assert ImageFormatFilter.is_dynamic_image('/path/to/video.mp4') is True
        assert ImageFormatFilter.is_dynamic_image('/path/to/video.mov') is True

        # Test case insensitive
        assert ImageFormatFilter.is_dynamic_image('/path/to/IMAGE.GIF') is True
        assert ImageFormatFilter.is_dynamic_image('/path/to/VIDEO.WEBM') is True

        # Test static formats (should be False)
        assert ImageFormatFilter.is_dynamic_image('/path/to/image.jpg') is False
        assert ImageFormatFilter.is_dynamic_image('/path/to/image.png') is False

    def test_is_dynamic_image_urls(self):
        """Test dynamic image detection for URLs."""
        # Test dynamic format URLs
        assert ImageFormatFilter.is_dynamic_image('https://example.com/image.gif') is True
        assert ImageFormatFilter.is_dynamic_image('https://example.com/video.webm') is True

        # Test URLs with query parameters
        assert ImageFormatFilter.is_dynamic_image('https://example.com/image.gif?width=512') is True

        # Test static format URLs (should be False)
        assert ImageFormatFilter.is_dynamic_image('https://example.com/image.jpg') is False

    def test_filter_static_urls(self):
        """Test filtering URLs to include only static formats."""
        mixed_urls = [
            'https://example.com/image1.jpg',
            'https://example.com/image2.gif',  # Should be filtered
            'https://example.com/image3.png',
            'https://example.com/video.webm',  # Should be filtered
            'https://example.com/image4.webp',
            'https://example.com/video.mp4',  # Should be filtered
            'https://example.com/image5.avif',
        ]

        expected_static = [
            'https://example.com/image1.jpg',
            'https://example.com/image3.png',
            'https://example.com/image4.webp',
            'https://example.com/image5.avif',
        ]

        result = ImageFormatFilter.filter_static_urls(mixed_urls)
        assert result == expected_static

    def test_filter_static_urls_empty_list(self):
        """Test filtering empty URL list."""
        assert ImageFormatFilter.filter_static_urls([]) == []

    def test_filter_static_urls_all_dynamic(self):
        """Test filtering list with only dynamic formats."""
        dynamic_urls = [
            'https://example.com/image1.gif',
            'https://example.com/video1.webm',
            'https://example.com/video2.mp4',
        ]

        result = ImageFormatFilter.filter_static_urls(dynamic_urls)
        assert result == []

    def test_filter_static_urls_all_static(self):
        """Test filtering list with only static formats."""
        static_urls = [
            'https://example.com/image1.jpg',
            'https://example.com/image2.png',
            'https://example.com/image3.webp',
        ]

        result = ImageFormatFilter.filter_static_urls(static_urls)
        assert result == static_urls

    def test_get_static_extension(self):
        """Test extracting static extension from URLs."""
        assert ImageFormatFilter.get_static_extension('https://example.com/image.jpg') == '.jpg'
        assert ImageFormatFilter.get_static_extension('https://example.com/image.png') == '.png'
        assert ImageFormatFilter.get_static_extension('https://example.com/image.webp') == '.webp'

        # Test with query parameters
        assert (
            ImageFormatFilter.get_static_extension('https://example.com/image.jpg?width=512')
            == '.jpg'
        )

        # Test dynamic formats (should return None)
        assert ImageFormatFilter.get_static_extension('https://example.com/image.gif') is None
        assert ImageFormatFilter.get_static_extension('https://example.com/video.webm') is None

    def test_get_static_extension_invalid_input(self):
        """Test static extension extraction with invalid inputs."""
        assert ImageFormatFilter.get_static_extension('') is None
        assert ImageFormatFilter.get_static_extension('invalid_url') is None
        assert ImageFormatFilter.get_static_extension('https://example.com/no_extension') is None

    def test_get_supported_formats(self):
        """Test getting list of supported static formats."""
        formats = ImageFormatFilter.get_supported_formats()
        assert formats == STATIC_IMAGE_EXTENSIONS
        # Ensure we get a copy, not the original
        formats.append('.test')
        assert '.test' not in ImageFormatFilter.get_supported_formats()

    def test_get_filtered_formats(self):
        """Test getting list of filtered dynamic formats."""
        formats = ImageFormatFilter.get_filtered_formats()
        assert formats == DYNAMIC_IMAGE_EXTENSIONS
        # Ensure we get a copy, not the original
        formats.append('.test')
        assert '.test' not in ImageFormatFilter.get_filtered_formats()

    def test_edge_cases(self):
        """Test edge cases and error handling."""
        # Test None input
        assert ImageFormatFilter.is_static_image(None) is False
        assert ImageFormatFilter.is_dynamic_image(None) is False

        # Test empty string
        assert ImageFormatFilter.is_static_image('') is False
        assert ImageFormatFilter.is_dynamic_image('') is False

        # Test malformed URLs
        assert ImageFormatFilter.is_static_image('not-a-url') is False
        assert ImageFormatFilter.is_static_image('://malformed') is False

        # Test file paths without extensions
        assert ImageFormatFilter.is_static_image('/path/to/file_no_ext') is False
        assert ImageFormatFilter.is_dynamic_image('/path/to/file_no_ext') is False


class TestDataValidatorStaticImages(unittest.TestCase):
    """Test DataValidator integration with static image filtering."""

    def test_validate_static_image_file_valid_formats(self):
        """Test validation of valid static image files."""
        from scripts.civitai_manager_libs.ishortcut_core.data_validator import DataValidator

        validator = DataValidator()

        # Test static formats using temporary files
        with tempfile.TemporaryDirectory() as tmp_dir:
            for ext in STATIC_IMAGE_EXTENSIONS:
                test_file = os.path.join(tmp_dir, f"test{ext}")
                with open(test_file, 'w') as f:
                    f.write("dummy content")

                self.assertTrue(validator.validate_static_image_file(test_file))

    def test_validate_static_image_file_dynamic_formats(self):
        """Test validation rejection of dynamic image files."""
        from scripts.civitai_manager_libs.ishortcut_core.data_validator import DataValidator

        validator = DataValidator()

        # Test dynamic formats (should be rejected)
        with tempfile.TemporaryDirectory() as tmp_dir:
            for ext in DYNAMIC_IMAGE_EXTENSIONS:
                test_file = os.path.join(tmp_dir, f"test{ext}")
                with open(test_file, 'w') as f:
                    f.write("dummy content")

                self.assertFalse(validator.validate_static_image_file(test_file))

    def test_data_validator_updated_extensions(self):
        """Test that DataValidator now uses only static extensions."""
        from scripts.civitai_manager_libs.ishortcut_core.data_validator import DataValidator

        validator = DataValidator()

        # Ensure GIF is no longer in valid extensions
        assert '.gif' not in validator.valid_image_extensions

        # Ensure all static formats are included
        for ext in STATIC_IMAGE_EXTENSIONS:
            assert ext in validator.valid_image_extensions


class TestStandaloneMetadataProcessorStaticSupport(unittest.TestCase):
    """Test StandaloneMetadataProcessor static format support."""

    def test_supported_formats_static_only(self):
        """Test that metadata processor only supports static formats."""
        from scripts.civitai_manager_libs.compat.standalone_adapters.standalone_metadata_processor import (  # noqa: E501
            StandaloneMetadataProcessor,
        )

        processor = StandaloneMetadataProcessor()

        # Ensure GIF is no longer supported
        assert '.gif' not in processor.supported_formats

        # Ensure all static formats are supported
        for ext in STATIC_IMAGE_EXTENSIONS:
            assert ext in processor.supported_formats

        # Ensure no dynamic formats are supported
        for ext in DYNAMIC_IMAGE_EXTENSIONS:
            assert ext not in processor.supported_formats


class TestIsValidStaticImageFile(unittest.TestCase):
    """Tests for ImageFormatFilter.is_valid_static_image_file."""

    def _write_file(self, header: bytes) -> str:
        f = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        f.write(header)
        f.close()
        return f.name

    def test_valid_png(self):
        path = self._write_file(b'\x89PNG\r\n\x1a\n' + b'\x00' * 8)
        self.assertTrue(ImageFormatFilter.is_valid_static_image_file(path))
        os.unlink(path)

    def test_valid_jpeg(self):
        path = self._write_file(b'\xff\xd8\xff\xe0' + b'\x00' * 12)
        self.assertTrue(ImageFormatFilter.is_valid_static_image_file(path))
        os.unlink(path)

    def test_valid_webp(self):
        path = self._write_file(b'RIFF\x00\x00\x00\x00WEBP' + b'\x00' * 4)
        self.assertTrue(ImageFormatFilter.is_valid_static_image_file(path))
        os.unlink(path)

    def test_rejects_mp4(self):
        path = self._write_file(b'\x00\x00\x00\x1cftypisom' + b'\x00' * 4)
        self.assertFalse(ImageFormatFilter.is_valid_static_image_file(path))
        os.unlink(path)

    def test_rejects_gif(self):
        path = self._write_file(b'GIF89a' + b'\x00' * 10)
        self.assertFalse(ImageFormatFilter.is_valid_static_image_file(path))
        os.unlink(path)

    def test_rejects_webm(self):
        path = self._write_file(b'\x1a\x45\xdf\xa3' + b'\x00' * 12)
        self.assertFalse(ImageFormatFilter.is_valid_static_image_file(path))
        os.unlink(path)

    def test_nonexistent_file(self):
        self.assertFalse(ImageFormatFilter.is_valid_static_image_file("/no/such/file.png"))

    def test_empty_file(self):
        path = self._write_file(b'')
        self.assertFalse(ImageFormatFilter.is_valid_static_image_file(path))
        os.unlink(path)

    def test_avif_file(self):
        path = self._write_file(b'\x00\x00\x00\x1cftypavif' + b'\x00' * 4)
        self.assertTrue(ImageFormatFilter.is_valid_static_image_file(path))
        os.unlink(path)
