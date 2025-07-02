"""Integration tests for image download functionality."""

import os
from unittest.mock import patch
from tests.utils.test_helpers import HTTPClientTestHelper


class TestImageDownloadIntegration:
    """Integration tests for image download."""

    def setup_method(self):
        """Set up test environment."""
        self.helper = HTTPClientTestHelper()

    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup_temp_environment()

    @patch('civitai_manager_libs.http_client.requests.Session.get')
    def test_preview_image_download(self, mock_session_get):
        """Test model preview image download."""
        # Arrange
        test_image_data = b"fake_image_data"
        mock_response = self.helper.mock_http_response(
            status_code=200,
            content=test_image_data,
            headers={"Content-Type": "image/jpeg"},
        )
        mock_session_get.return_value = mock_response

        model_info = {
            "id": 12345,
            "name": "Test Model",
            "modelVersions": [{"images": [{"url": "http://test.com/image.jpg"}]}],
        }

        # Act
        from scripts.civitai_manager_libs.ishortcut_core.preview_image_manager import (
            PreviewImageManager,
        )

        # instantiate PreviewImageManager for preview image download
        preview_manager = PreviewImageManager(None)
        result = preview_manager.download_preview_image(model_info)

        # Assert
        assert result is not None
        assert os.path.exists(result)

        with open(result, 'rb') as f:
            assert f.read() == test_image_data

    @patch('civitai_manager_libs.http_client.requests.Session.get')
    def test_gallery_image_batch_download(self, mock_session_get):
        """Test batch download of gallery images."""
        # Arrange
        test_urls = [
            "http://test.com/image1.jpg",
            "http://test.com/image2.jpg",
            "http://test.com/image3.jpg",
        ]

        mock_response = self.helper.mock_http_response(
            status_code=200,
            content=b"test_image_data",
            headers={"Content-Type": "image/jpeg"},
        )
        mock_session_get.return_value = mock_response

        # Act - use isolated gallery folder to ensure downloads occur
        from civitai_manager_libs import civitai_gallery_action, setting

        setting.shortcut_gallery_folder = self.helper.temp_dir

        civitai_gallery_action.download_images(test_urls)

        # Assert
        mock_session_get.assert_called()
        assert mock_session_get.call_count == len(test_urls)
