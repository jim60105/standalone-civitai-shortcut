"""Test helper utilities for HTTP client integration tests."""

import os
import json
import tempfile
import shutil
from unittest.mock import Mock
from typing import Dict


class HTTPClientTestHelper:
    """Helper class for HTTP client integration tests."""

    def __init__(self):
        self.temp_dir = None
        self.mock_responses = {}
        self.setup_temp_environment()

    def setup_temp_environment(self):
        """Set up temporary test environment."""
        self.temp_dir = tempfile.mkdtemp(prefix="civitai_test_")

        # Create test directories
        os.makedirs(os.path.join(self.temp_dir, "downloads"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "cache"), exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "images"), exist_ok=True)

    def cleanup_temp_environment(self):
        """Clean up temporary test environment."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def mock_http_response(
        self,
        status_code: int = 200,
        json_data: Dict = None,
        headers: Dict = None,
        content: bytes = None,
    ):
        """Create mock HTTP response."""
        mock_response = Mock()
        mock_response.status_code = status_code
        mock_response.ok = status_code < 400
        mock_response.headers = headers or {}

        if json_data:
            mock_response.json.return_value = json_data
            mock_response.text = json.dumps(json_data)

        if content:
            mock_response.content = content
            mock_response.iter_content.return_value = [
                content[i : i + 1024] for i in range(0, len(content), 1024)
            ]

        return mock_response

    def simulate_network_error(self, error_type: str = "connection"):
        """Simulate different types of network errors."""
        import requests

        if error_type == "connection":
            return requests.exceptions.ConnectionError("Connection failed")
        if error_type == "timeout":
            return requests.exceptions.Timeout("Request timeout")
        if error_type == "http":
            return requests.exceptions.HTTPError("HTTP Error")
        return requests.exceptions.RequestException("Request failed")
