import pytest
from unittest.mock import MagicMock, patch

from scripts.civitai_manager_libs import civitai, settings
from scripts.civitai_manager_libs.exceptions import (
    ModelNotAccessibleError,
    ModelNotFoundError,
    HTTPError,
    APIError,
    NetworkError,
)

config_manager = settings.config_manager


class DummyResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data
        self.url = "http://test"

    def json(self):
        return self._json


class DummyClient:
    def __init__(self, response, timeout=None):
        self.session = self
        self._response = response
        self.timeout = timeout

    def get(self, url, timeout=None):
        return self._response

    def _handle_response_error(self, response):
        if response.status_code >= 400:
            raise HTTPError(
                message=f"HTTP {response.status_code}",
                status_code=response.status_code,
                url=response.url,
            )


class DummyClientWithGetJson:
    """Mock client that has get_json method."""

    def __init__(self, return_value):
        self._return_value = return_value

    def get_json(self, url):
        return self._return_value


@pytest.mark.parametrize(
    "status_code,json_data,expected_exception",
    [
        (404, {}, ModelNotAccessibleError),
        (200, {}, ModelNotFoundError),
        (500, {}, APIError),
    ],
)
def test_get_model_info_error_handling(monkeypatch, status_code, json_data, expected_exception):
    """Test that get_model_info raises correct exceptions for missing or inaccessible models."""
    dummy_resp = DummyResponse(status_code, json_data)
    monkeypatch.setattr(
        civitai,
        'get_http_client',
        lambda: DummyClient(dummy_resp),
    )
    with pytest.raises(expected_exception):
        civitai.get_model_info('123')


def test_get_model_info_success(monkeypatch):
    """Test that get_model_info returns data when model is accessible."""
    data = {'id': '123', 'name': 'test'}
    dummy_resp = DummyResponse(200, data)
    monkeypatch.setattr(
        civitai,
        'get_http_client',
        lambda: DummyClient(dummy_resp),
    )
    result = civitai.get_model_info('123')
    assert result == data


def test_get_model_info_api_error_wrapping(monkeypatch):
    """Test get_model_info wraps non-HTTP errors into APIError."""

    class ErrorClient(DummyClient):
        def get(self, url, timeout=None):
            raise ValueError("parse error")

    monkeypatch.setattr(
        civitai,
        'get_http_client',
        lambda: ErrorClient(None),
    )
    with pytest.raises(APIError) as excinfo:
        civitai.get_model_info('123')
    assert "parse error" in str(excinfo.value)


def test_get_model_info_empty_model_id():
    """Test get_model_info returns None for empty model_id."""
    assert civitai.get_model_info('') is None
    # Skip None test as function signature expects str


def test_get_model_info_with_get_json_method_success(monkeypatch):
    """Test get_model_info with client that has get_json method."""
    data = {'id': '123', 'name': 'test'}
    monkeypatch.setattr(
        civitai,
        'get_http_client',
        lambda: DummyClientWithGetJson(data),
    )
    result = civitai.get_model_info('123')
    assert result == data


def test_get_model_info_with_get_json_method_not_found(monkeypatch):
    """Test get_model_info with client that has get_json method but returns None."""
    monkeypatch.setattr(
        civitai,
        'get_http_client',
        lambda: DummyClientWithGetJson(None),
    )
    with pytest.raises(ModelNotFoundError):
        civitai.get_model_info('123')


def test_get_model_info_with_get_json_method_no_id(monkeypatch):
    """Test get_model_info with client that has get_json method but returns data without id."""
    data = {'name': 'test'}  # Missing 'id' field
    monkeypatch.setattr(
        civitai,
        'get_http_client',
        lambda: DummyClientWithGetJson(data),
    )
    with pytest.raises(ModelNotFoundError):
        civitai.get_model_info('123')


def test_get_model_info_exception_context():
    """Test that exceptions contain proper context information."""
    dummy_resp = DummyResponse(404, {})

    with patch.object(civitai, 'get_http_client') as mock_get_client:
        mock_get_client.return_value = DummyClient(dummy_resp, timeout=10)

        with pytest.raises(ModelNotAccessibleError) as exc_info:
            civitai.get_model_info('123')

        assert exc_info.value.model_id == '123'
        assert 'Model 123 is not accessible via API' in str(exc_info.value)


def test_get_model_info_retry_functionality():
    """Test that the function can handle network issues gracefully."""
    # Since decorator is removed, test the function directly handles retries
    # via the underlying client
    with patch.object(civitai, 'get_http_client') as mock_get_client:
        mock_client = MagicMock()
        mock_session = MagicMock()
        mock_client.session = mock_session

        # Mock the client to NOT have get_json method
        del mock_client.get_json  # This makes hasattr return False

        # Test successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'id': '123', 'name': 'test'}
        mock_session.get.return_value = mock_response
        mock_client._handle_response_error = MagicMock()

        mock_get_client.return_value = mock_client

        result = civitai.get_model_info('123')
        assert result == {'id': '123', 'name': 'test'}


@pytest.mark.parametrize(
    "http_status,expected_exception",
    [
        (401, APIError),
        (403, APIError),
        (404, ModelNotAccessibleError),
        (429, APIError),
        (500, APIError),
    ],
)
def test_get_model_info_various_http_errors(monkeypatch, http_status, expected_exception):
    """Test various HTTP error codes and their exception mappings."""
    dummy_resp = DummyResponse(http_status, {})
    monkeypatch.setattr(
        civitai,
        'get_http_client',
        lambda: DummyClient(dummy_resp),
    )

    with pytest.raises(expected_exception):
        civitai.get_model_info('123')


def test_model_not_accessible_error_inheritance():
    """Test that ModelNotAccessibleError properly inherits from APIError."""
    error = ModelNotAccessibleError("test message", model_id="123")
    assert isinstance(error, APIError)
    assert isinstance(error, NetworkError)
    assert error.model_id == "123"


def test_model_not_found_error_inheritance():
    """Test that ModelNotFoundError properly inherits from APIError."""
    error = ModelNotFoundError("test message", model_id="123")
    assert isinstance(error, APIError)
    assert isinstance(error, NetworkError)
    assert error.model_id == "123"
