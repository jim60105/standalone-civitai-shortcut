"""Integration tests for civitai.py module."""

from unittest.mock import patch
from tests.utils.test_helpers import HTTPClientTestHelper


class TestCivitaiIntegration:
    """Integration tests for civitai module."""

    def setup_method(self):
        """Set up test environment."""
        self.helper = HTTPClientTestHelper()

    def teardown_method(self):
        """Clean up test environment."""
        self.helper.cleanup_temp_environment()

    @patch('civitai_manager_libs.civitai.requests.get')
    def test_get_model_info_success(self, mock_get):
        """Test successful model info retrieval."""
        # Arrange
        mock_response = self.helper.mock_http_response(
            status_code=200, json_data={"id": 12345, "name": "Test Model"}
        )
        mock_get.return_value.__enter__.return_value = mock_response

        # Act
        from civitai_manager_libs import civitai

        result = civitai.get_model_info("12345")

        # Assert
        assert result is not None
        assert result["id"] == 12345
        assert result["name"] == "Test Model"

    @patch('civitai_manager_libs.civitai.requests.get')
    def test_get_model_info_http_error(self, mock_get):
        """Test model info retrieval with HTTP error."""
        # Arrange
        mock_response = self.helper.mock_http_response(status_code=404)
        mock_get.return_value.__enter__.return_value = mock_response

        # Act
        from civitai_manager_libs import civitai

        result = civitai.get_model_info("99999")

        # Assert
        assert result is None

    @patch('civitai_manager_libs.civitai.requests.get')
    def test_get_model_info_network_error(self, mock_get):
        """Test model info retrieval with network error."""
        # Arrange
        mock_get.side_effect = self.helper.simulate_network_error("connection")

        # Act
        from civitai_manager_libs import civitai

        result = civitai.get_model_info("12345")

        # Assert
        assert result is None

    @patch('civitai_manager_libs.civitai.requests.get')
    def test_request_models_with_pagination(self, mock_get):
        """Test paginated model requests."""
        # Arrange
        mock_response = self.helper.mock_http_response(
            status_code=200,
            json_data={"items": [{"id": 1}, {"id": 2}], "metadata": {"nextPage": "next_url"}},
        )
        mock_get.return_value.__enter__.return_value = mock_response

        # Act
        from civitai_manager_libs import civitai

        result = civitai.request_models("test_url")

        # Assert
        assert result is not None
        assert "items" in result
        assert len(result["items"]) == 2
        assert "metadata" in result
