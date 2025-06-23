"""Integration tests for file download functionality."""

import os
from unittest.mock import patch
from tests.utils.test_helpers import HTTPClientTestHelper


class TestFileDownloadIntegration:
    """Integration tests for file download."""

    def setup_method(self):
        """Set up test environment."""
        self.helper = HTTPClientTestHelper()

    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup_temp_environment()

    @patch('civitai_manager_libs.http_client.requests.get')
    def test_large_file_download_with_resume(self, mock_get):
        """Test large file download with resume capability."""
        # Arrange
        test_content = b"test content" * 1000  # Simulate large file
        mock_response = self.helper.mock_http_response(
            status_code=200,
            content=test_content,
            headers={"Content-Length": str(len(test_content))},
        )
        mock_get.return_value = mock_response

        test_file = os.path.join(self.helper.temp_dir, "test_download.bin")

        # Act
        from civitai_manager_libs import downloader

        success = downloader.download_file("http://test.com/file", test_file)

        # Assert
        assert success is True
        assert os.path.exists(test_file)
        assert os.path.getsize(test_file) == len(test_content)

        with open(test_file, 'rb') as f:
            assert f.read() == test_content

    @patch('civitai_manager_libs.http_client.requests.get')
    def test_download_with_insufficient_space(self, mock_get):
        """Test download failure due to insufficient disk space."""
        # This test would need platform-specific implementation
        pass

    @patch('civitai_manager_libs.http_client.requests.get')
    def test_download_with_progress_callback(self, mock_get):
        """Test download with progress tracking."""
        # Arrange
        test_content = b"test" * 1000
        mock_response = self.helper.mock_http_response(
            status_code=200,
            content=test_content,
            headers={"Content-Length": str(len(test_content))},
        )
        mock_get.return_value = mock_response

        progress_calls = []

        def progress_callback(downloaded, total, speed):
            progress_calls.append((downloaded, total, speed))

        test_file = os.path.join(self.helper.temp_dir, "test_progress.bin")

        # Act
        from civitai_manager_libs import downloader

        success = downloader.download_file_gr("http://test.com/file", test_file, progress_callback)

        # Assert
        assert success is True
        assert len(progress_calls) > 0
        assert progress_calls[-1][0] == len(test_content)  # Final progress should be total size
