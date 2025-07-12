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

    class FakeGradioError(BaseException):
        def __init__(self, *args, **kwargs):
            super().__init__(*args)

    @patch('civitai_manager_libs.http_client.requests.Session.get')
    @patch('gradio.Error', new=FakeGradioError)
    def test_524_error_handling(self, mock_session_get):
        """Test specific handling of 524 Cloudflare error."""
        import pytest

        # Arrange - Simulate 524 error
        mock_response = self.helper.mock_http_response(status_code=524)
        mock_session_get.return_value = mock_response

        from civitai_manager_libs import civitai

        with pytest.raises(self.FakeGradioError) as excinfo:
            civitai.request_models("test_url")
        assert "Cloudflare Timeout" in str(excinfo.value) or "524" in str(excinfo.value)

    @patch('civitai_manager_libs.http_client.requests.Session.get')
    @patch('gradio.Error', new=FakeGradioError)
    def test_timeout_error_handling(self, mock_session_get):
        """Test timeout error handling."""
        import pytest

        # Arrange
        mock_session_get.side_effect = self.helper.simulate_network_error("timeout")

        from civitai_manager_libs import civitai

        with pytest.raises(self.FakeGradioError) as excinfo:
            civitai.get_model_info("12345")
        assert "Timeout" in str(excinfo.value)

    @patch('civitai_manager_libs.civitai.get_http_client')
    def test_none_response_handling(self, mock_get_http_client):
        """Test handling of None responses to prevent TypeError."""
        # Arrange - Simulate scenario that previously caused TypeError
        mock_client = mock_get_http_client.return_value
        mock_client.get_json.return_value = None

        # Act
        from civitai_manager_libs.gallery import get_paging_information_working

        result = get_paging_information_working("12345")

        # Assert - Should not raise TypeError
        assert result is not None
        assert "totalPages" in result
        assert result["totalPages"] == 0
