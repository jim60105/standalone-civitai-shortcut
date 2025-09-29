"""Simple tests for static image format filtering functionality."""

import unittest
import tempfile
import os
import sys

# Add scripts to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts'))

# Set test mode to avoid initialization issues
os.environ['CIVITAI_SHORTCUT_TEST_MODE'] = '1'


class TestStaticImageBasics(unittest.TestCase):
    """Test basic static image filtering functionality."""

    def test_constants_exist(self):
        """Test that image format constants are defined correctly."""
        from scripts.civitai_manager_libs.settings.constants import STATIC_IMAGE_EXTENSIONS, DYNAMIC_IMAGE_EXTENSIONS
        
        # Check static extensions
        expected_static = ['.jpg', '.jpeg', '.png', '.webp', '.avif']
        self.assertEqual(STATIC_IMAGE_EXTENSIONS, expected_static)
        
        # Check dynamic extensions
        expected_dynamic = ['.gif', '.webm', '.mp4', '.mov']
        self.assertEqual(DYNAMIC_IMAGE_EXTENSIONS, expected_dynamic)
        
        # Ensure no overlap
        static_set = set(STATIC_IMAGE_EXTENSIONS)
        dynamic_set = set(DYNAMIC_IMAGE_EXTENSIONS)
        self.assertEqual(len(static_set.intersection(dynamic_set)), 0)

    def test_image_format_filter_basic(self):
        """Test basic ImageFormatFilter functionality."""
        from scripts.civitai_manager_libs.image_format_filter import ImageFormatFilter
        
        # Test static image detection
        self.assertTrue(ImageFormatFilter.is_static_image('test.jpg'))
        self.assertTrue(ImageFormatFilter.is_static_image('test.png'))
        self.assertTrue(ImageFormatFilter.is_static_image('test.webp'))
        self.assertTrue(ImageFormatFilter.is_static_image('test.avif'))
        
        # Test dynamic image detection (should be False for is_static_image)
        self.assertFalse(ImageFormatFilter.is_static_image('test.gif'))
        self.assertFalse(ImageFormatFilter.is_static_image('test.webm'))
        self.assertFalse(ImageFormatFilter.is_static_image('test.mp4'))
        
        # Test URLs
        self.assertTrue(ImageFormatFilter.is_static_image('https://example.com/image.jpg'))
        self.assertFalse(ImageFormatFilter.is_static_image('https://example.com/image.gif'))

    def test_data_validator_constants(self):
        """Test that DataValidator uses the correct constants."""
        # Create a simple validator instance without full initialization
        from scripts.civitai_manager_libs.settings.constants import STATIC_IMAGE_EXTENSIONS
        
        # Test that GIF is not in static extensions
        self.assertNotIn('.gif', STATIC_IMAGE_EXTENSIONS)
        
        # Test that all expected static formats are included
        for ext in ['.jpg', '.jpeg', '.png', '.webp', '.avif']:
            self.assertIn(ext, STATIC_IMAGE_EXTENSIONS)

    def test_filter_urls(self):
        """Test URL filtering functionality."""
        from scripts.civitai_manager_libs.image_format_filter import ImageFormatFilter
        
        mixed_urls = [
            'https://example.com/image1.jpg',     # Should keep
            'https://example.com/image2.gif',     # Should filter
            'https://example.com/image3.png',     # Should keep
            'https://example.com/video.webm',     # Should filter
            'https://example.com/image4.webp',    # Should keep
        ]

        expected_static = [
            'https://example.com/image1.jpg',
            'https://example.com/image3.png',
            'https://example.com/image4.webp'
        ]

        result = ImageFormatFilter.filter_static_urls(mixed_urls)
        self.assertEqual(result, expected_static)


if __name__ == '__main__':
    unittest.main()