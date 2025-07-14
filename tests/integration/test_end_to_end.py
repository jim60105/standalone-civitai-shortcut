"""End-to-end regression tests."""

import os
from unittest.mock import patch
from tests.utils.test_helpers import HTTPClientTestHelper


class TestEndToEndRegression:
    """End-to-end regression tests."""

    def setup_method(self):
        """Set up test environment."""
        self.helper = HTTPClientTestHelper()

    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup_temp_environment()

    @patch('civitai_manager_libs.http.client.requests.Session.get')
    def test_complete_model_workflow(self, mock_session_get):
        """Test complete model download workflow."""
        # Arrange
        model_response = self.helper.mock_http_response(
            status_code=200,
            json_data={
                "id": 12345,
                "name": "Test Model",
                "modelVersions": [
                    {
                        "id": 67890,
                        "name": "v1.0",
                        "files": [
                            {
                                "name": "model.safetensors",
                                "downloadUrl": "http://test.com/model.safetensors",
                            }
                        ],
                        "images": [{"url": "http://test.com/preview.jpg"}],
                    }
                ],
            },
        )

        file_response = self.helper.mock_http_response(
            status_code=200, content=b"fake_model_data", headers={"Content-Length": "15"}
        )

        image_response = self.helper.mock_http_response(
            status_code=200, content=b"fake_image_data", headers={"Content-Type": "image/jpeg"}
        )

        # Configure mock to return different responses based on URL
        def mock_get_side_effect(url, **kwargs):
            if "api/v1/models" in url:
                return model_response
            if "model.safetensors" in url:
                return file_response
            if "preview.jpg" in url:
                return image_response
            return self.helper.mock_http_response(status_code=404)

        mock_session_get.side_effect = mock_get_side_effect

        # Act & Assert
        # Test 1: Get model info
        from civitai_manager_libs import civitai

        model_info = civitai.get_model_info("12345")
        assert model_info is not None
        assert model_info["id"] == 12345

        # Test 2: Download preview image
        from scripts.civitai_manager_libs.ishortcut_core.preview_image_manager import (
            PreviewImageManager,
        )

        # instantiate PreviewImageManager for downloading preview image
        preview_manager = PreviewImageManager(None)
        preview_path = preview_manager.download_preview_image(model_info)
        assert preview_path is not None

        # Test 3: Download model file
        from civitai_manager_libs import downloader

        model_file = os.path.join(self.helper.temp_dir, "model.safetensors")
        success = downloader.download_file("http://test.com/model.safetensors", model_file)
        assert success is True
        assert os.path.exists(model_file)
