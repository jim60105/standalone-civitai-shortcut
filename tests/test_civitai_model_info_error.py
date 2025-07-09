import pytest

from scripts.civitai_manager_libs import civitai
from scripts.civitai_manager_libs.exceptions import (
    ModelNotAccessibleError,
    ModelNotFoundError,
    HTTPError,
    APIError,
)


class DummyResponse:
    def __init__(self, status_code, json_data):
        self.status_code = status_code
        self._json = json_data
        self.url = "http://test"

    def json(self):
        return self._json


class DummyClient:
    def __init__(self, response):
        self.session = self
        self._response = response

    def get(self, url, timeout=None):
        return self._response

    def _handle_response_error(self, response):
        if response.status_code >= 400:
            raise HTTPError(
                message=f"HTTP {response.status_code}",
                status_code=response.status_code,
                url=response.url,
            )


@pytest.mark.parametrize(
    "status_code,json_data,expected_exception",
    [
        (404, {}, ModelNotAccessibleError),
        (200, {}, ModelNotFoundError),
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
