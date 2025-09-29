"""Integration tests for static image filtering throughout the system."""

import pytest
from unittest.mock import Mock, patch
from scripts.civitai_manager_libs.ishortcut_core.image_processor import ImageProcessor
from scripts.civitai_manager_libs.image_format_filter import ImageFormatFilter


class TestStaticImageIntegration:
    """Integration tests for static image filtering across components."""

    def test_image_processor_filters_dynamic_images(self):
        """Test that ImageProcessor filters out dynamic images during collection."""
        # Mock model info with mixed image formats
        version_list = [
            [
                ['version1', 'https://example.com/image1.jpg'],     # Static - should keep
                ['version1', 'https://example.com/image2.gif'],     # Dynamic - should filter
                ['version1', 'https://example.com/image3.png'],     # Static - should keep
                ['version1', 'https://example.com/video.webm'],     # Dynamic - should filter
                ['version1', 'https://example.com/image4.webp'],    # Static - should keep
            ]
        ]
        
        # Mock settings to avoid initialization issues
        with patch('scripts.civitai_manager_libs.ishortcut_core.image_processor.settings') as mock_settings:
            mock_settings.shortcut_max_download_image_per_version = None
            mock_settings.get_image_url_to_shortcut_file.return_value = '/tmp/test.jpg'
            
            # Mock os.path.exists to return False (so all images are considered new)
            with patch('scripts.civitai_manager_libs.ishortcut_core.image_processor.os.path.exists', return_value=False):
                processor = ImageProcessor(thumbnail_folder='/tmp')
                
                result = processor._collect_images_to_download(version_list, 'test_model')
                
                # Should only have static images
                assert len(result) == 3  # Only JPG, PNG, WebP should remain
                
                # Verify the URLs are the expected static ones
                result_urls = [item[1] for item in result]
                assert 'https://example.com/image1.jpg' in result_urls
                assert 'https://example.com/image3.png' in result_urls
                assert 'https://example.com/image4.webp' in result_urls
                
                # Verify dynamic images are filtered out
                assert 'https://example.com/image2.gif' not in result_urls
                assert 'https://example.com/video.webm' not in result_urls

    def test_get_preview_image_url_filters_dynamic(self):
        """Test that get_preview_image_url returns only static format URLs."""
        model_info = {
            'modelVersions': [
                {
                    'images': [
                        {'url': 'https://example.com/preview.gif'},   # Dynamic - should skip
                        {'url': 'https://example.com/preview.jpg'},   # Static - should return
                        {'url': 'https://example.com/preview.webm'},  # Dynamic - should skip
                    ]
                }
            ]
        }
        
        processor = ImageProcessor(thumbnail_folder='/tmp')
        
        result = processor.get_preview_image_url(model_info)
        
        # Should return the first static image found
        assert result == 'https://example.com/preview.jpg'

    def test_get_preview_image_url_no_static_images(self):
        """Test that get_preview_image_url returns None when only dynamic images exist."""
        model_info = {
            'modelVersions': [
                {
                    'images': [
                        {'url': 'https://example.com/preview.gif'},
                        {'url': 'https://example.com/preview.webm'},
                        {'url': 'https://example.com/video.mp4'},
                    ]
                }
            ]
        }
        
        processor = ImageProcessor(thumbnail_folder='/tmp')
        
        result = processor.get_preview_image_url(model_info)
        
        # Should return None as no static images available
        assert result is None

    def test_process_version_images_filters_dynamic(self):
        """Test that _process_version_images filters out dynamic images."""
        images = [
            {'url': 'https://example.com/image1.jpg'},     # Static
            {'url': 'https://example.com/image2.gif'},     # Dynamic - should filter
            {'url': 'https://example.com/image3.png'},     # Static
            {'url': 'https://example.com/video.webm'},     # Dynamic - should filter
            {'url': 'https://example.com/image4.webp'},    # Static
        ]
        
        # Mock util to avoid dependency issues
        with patch('scripts.civitai_manager_libs.ishortcut_core.image_processor.util') as mock_util:
            mock_util.change_width_from_image_url = lambda url, width: url
            
            processor = ImageProcessor(thumbnail_folder='/tmp')
            
            result = processor._process_version_images(images, 'version1')
            
            # Should only have static images
            assert len(result) == 3
            
            # Verify the URLs are the expected static ones
            result_urls = [item[1] for item in result]
            assert 'https://example.com/image1.jpg' in result_urls
            assert 'https://example.com/image3.png' in result_urls
            assert 'https://example.com/image4.webp' in result_urls
            
            # Verify dynamic images are filtered out
            assert 'https://example.com/image2.gif' not in result_urls
            assert 'https://example.com/video.webm' not in result_urls

    def test_extract_version_images_end_to_end_filtering(self):
        """Test end-to-end filtering in extract_version_images."""
        model_info = {
            'modelVersions': [
                {
                    'id': 'version1',
                    'images': [
                        {'url': 'https://example.com/image1.jpg'},
                        {'url': 'https://example.com/image2.gif'},     # Should be filtered
                        {'url': 'https://example.com/image3.png'},
                    ]
                },
                {
                    'id': 'version2',
                    'images': [
                        {'url': 'https://example.com/video.webm'},     # Should be filtered
                        {'url': 'https://example.com/image4.webp'},
                    ]
                }
            ]
        }
        
        # Mock util to avoid dependency issues
        with patch('scripts.civitai_manager_libs.ishortcut_core.image_processor.util') as mock_util:
            mock_util.change_width_from_image_url = lambda url, width: url
            
            processor = ImageProcessor(thumbnail_folder='/tmp')
            
            result = processor.extract_version_images(model_info, 'test_model')
            
            # Should have 2 versions with filtered content
            assert len(result) == 2
            
            # First version should have 2 static images (JPG, PNG)
            version1_images = result[0]
            assert len(version1_images) == 2
            version1_urls = [item[1] for item in version1_images]
            assert 'https://example.com/image1.jpg' in version1_urls
            assert 'https://example.com/image3.png' in version1_urls
            assert 'https://example.com/image2.gif' not in version1_urls
            
            # Second version should have 1 static image (WebP)
            version2_images = result[1]
            assert len(version2_images) == 1
            version2_urls = [item[1] for item in version2_images]
            assert 'https://example.com/image4.webp' in version2_urls
            assert 'https://example.com/video.webm' not in version2_urls

    def test_no_static_images_available(self):
        """Test behavior when no static images are available."""
        # Model info with only dynamic images
        model_info = {
            'modelVersions': [
                {
                    'id': 'version1',
                    'images': [
                        {'url': 'https://example.com/image1.gif'},
                        {'url': 'https://example.com/video.webm'},
                        {'url': 'https://example.com/video.mp4'},
                    ]
                }
            ]
        }
        
        # Mock util to avoid dependency issues
        with patch('scripts.civitai_manager_libs.ishortcut_core.image_processor.util') as mock_util:
            mock_util.change_width_from_image_url = lambda url, width: url
            
            processor = ImageProcessor(thumbnail_folder='/tmp')
            
            # extract_version_images should return empty list since no static images
            result = processor.extract_version_images(model_info, 'test_model')
            assert result == []
            
            # get_preview_image_url should return None
            preview_url = processor.get_preview_image_url(model_info)
            assert preview_url is None

    def test_mixed_formats_with_query_parameters(self):
        """Test filtering works correctly with URLs containing query parameters."""
        images = [
            {'url': 'https://example.com/image1.jpg?width=512&height=512'},  # Static
            {'url': 'https://example.com/image2.gif?v=1'},                   # Dynamic
            {'url': 'https://example.com/image3.png?format=webp'},           # Static  
            {'url': 'https://example.com/video.webm?autoplay=true'},         # Dynamic
        ]
        
        # Mock util to avoid dependency issues
        with patch('scripts.civitai_manager_libs.ishortcut_core.image_processor.util') as mock_util:
            mock_util.change_width_from_image_url = lambda url, width: url
            
            processor = ImageProcessor(thumbnail_folder='/tmp')
            
            result = processor._process_version_images(images, 'version1')
            
            # Should have 2 static images
            assert len(result) == 2
            
            result_urls = [item[1] for item in result]
            assert 'https://example.com/image1.jpg?width=512&height=512' in result_urls
            assert 'https://example.com/image3.png?format=webp' in result_urls
            
            # Dynamic images should be filtered
            assert 'https://example.com/image2.gif?v=1' not in result_urls
            assert 'https://example.com/video.webm?autoplay=true' not in result_urls


class TestConstantsIntegration:
    """Test that constants are properly integrated throughout the system."""

    def test_constants_available(self):
        """Test that image format constants are available and correct."""
        from scripts.civitai_manager_libs.settings.constants import STATIC_IMAGE_EXTENSIONS, DYNAMIC_IMAGE_EXTENSIONS
        
        # Check static extensions
        expected_static = ['.jpg', '.jpeg', '.png', '.webp', '.avif']
        assert STATIC_IMAGE_EXTENSIONS == expected_static
        
        # Check dynamic extensions
        expected_dynamic = ['.gif', '.webm', '.mp4', '.mov']
        assert DYNAMIC_IMAGE_EXTENSIONS == expected_dynamic
        
        # Ensure no overlap
        assert not set(STATIC_IMAGE_EXTENSIONS).intersection(set(DYNAMIC_IMAGE_EXTENSIONS))

    def test_image_format_filter_uses_constants(self):
        """Test that ImageFormatFilter uses the defined constants."""
        from scripts.civitai_manager_libs.settings.constants import STATIC_IMAGE_EXTENSIONS, DYNAMIC_IMAGE_EXTENSIONS
        
        supported = ImageFormatFilter.get_supported_formats()
        filtered = ImageFormatFilter.get_filtered_formats()
        
        assert supported == STATIC_IMAGE_EXTENSIONS
        assert filtered == DYNAMIC_IMAGE_EXTENSIONS