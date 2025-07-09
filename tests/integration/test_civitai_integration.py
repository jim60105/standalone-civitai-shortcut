"""Integration tests for civitai.py module."""

import pytest
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

    @patch('civitai_manager_libs.civitai.get_http_client')
    def test_get_model_info_success(self, mock_get_http_client):
        """Test successful model info retrieval."""
        # Arrange
        mock_client = mock_get_http_client.return_value
        mock_client.get_json.return_value = {"id": 12345, "name": "Test Model"}

        # Act
        from civitai_manager_libs import civitai

        result = civitai.get_model_info("12345")

        # Assert
        assert result is not None
        assert result["id"] == 12345
        assert result["name"] == "Test Model"

    @patch('civitai_manager_libs.civitai.get_http_client')
    def test_get_model_info_http_error(self, mock_get_http_client):
        """Test model info retrieval with HTTP error."""
        # Arrange
        mock_client = mock_get_http_client.return_value
        mock_client.get_json.return_value = None

        # Act
        from civitai_manager_libs import civitai
        from civitai_manager_libs.exceptions import ModelNotFoundError

        # Assert - should raise ModelNotFoundError for missing models
        with pytest.raises(ModelNotFoundError):
            civitai.get_model_info("99999")

    @patch('civitai_manager_libs.civitai.get_http_client')
    def test_get_model_info_network_error(self, mock_get_http_client):
        """Test model info retrieval with network error."""
        # Arrange
        mock_client = mock_get_http_client.return_value
        # Simulate network error resulting in None response
        mock_client.get_json.return_value = None

        # Act
        from civitai_manager_libs import civitai
        from civitai_manager_libs.exceptions import ModelNotFoundError

        # Assert - should raise ModelNotFoundError for missing models
        with pytest.raises(ModelNotFoundError):
            civitai.get_model_info("12345")

    @patch('civitai_manager_libs.civitai.get_http_client')
    def test_request_models_with_pagination(self, mock_get_http_client):
        """Test paginated model requests."""
        # Arrange
        mock_client = mock_get_http_client.return_value
        mock_client.get_json.return_value = {
            "items": [{"id": 1}, {"id": 2}],
            "metadata": {"nextPage": "next_url"},
        }

        # Act
        from civitai_manager_libs import civitai

        result = civitai.request_models("test_url")

        # Assert
        assert result is not None
        assert "items" in result
        assert len(result["items"]) == 2
        assert "metadata" in result
