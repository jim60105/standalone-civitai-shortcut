"""End-to-end error handling tests."""

from unittest.mock import patch
from tests.utils.test_helpers import HTTPClientTestHelper


class TestErrorHandlingIntegration:
    """Test error handling across all modules."""

    def setup_method(self):
        """Set up test environment."""
        self.helper = HTTPClientTestHelper()

    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup_temp_environment()

    @patch('civitai_manager_libs.http_client.requests.get')
    @patch('gradio.Error')
    def test_524_error_handling(self, mock_gradio_error, mock_get):
        """Test specific handling of 524 Cloudflare error."""
        # Arrange - Simulate 524 error
        mock_response = self.helper.mock_http_response(status_code=524)
        mock_get.return_value = mock_response

        # Act
        from civitai_manager_libs import civitai

        result = civitai.request_models("test_url")

        # Assert
        assert result is not None  # Should return empty structure, not None
        assert "items" in result
        assert result["items"] == []

        # Check that user-friendly error was shown
        mock_gradio_error.assert_called_once()
        error_message = mock_gradio_error.call_args[0][0]
        assert "連線超時" in error_message or "524" in error_message

    @patch('civitai_manager_libs.http_client.requests.get')
    @patch('gradio.Error')
    def test_timeout_error_handling(self, mock_gradio_error, mock_get):
        """Test timeout error handling."""
        # Arrange
        mock_get.side_effect = self.helper.simulate_network_error("timeout")

        # Act
        from civitai_manager_libs import civitai

        result = civitai.get_model_info("12345")

        # Assert
        assert result is None

        # Check that user-friendly error was shown
        mock_gradio_error.assert_called_once()
        error_message = mock_gradio_error.call_args[0][0]
        assert "超時" in error_message

    @patch('civitai_manager_libs.http_client.requests.get')
    def test_none_response_handling(self, mock_get):
        """Test handling of None responses to prevent TypeError."""
        # Arrange - Simulate scenario that previously caused TypeError
        mock_get.return_value = None

        # Act
        from civitai_manager_libs.civitai_gallery_action import get_paging_information_working

        result = get_paging_information_working("12345")

        # Assert - Should not raise TypeError
        assert result is not None
        assert "totalPages" in result
        assert result["totalPages"] == 0
