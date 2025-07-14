"""Unit tests for CivitaiHttpClient error handling and POST retry logic."""
import json
import time

import pytest
import requests

from scripts.civitai_manager_libs.http.client import CivitaiHttpClient
from scripts.civitai_manager_libs.exceptions import NetworkError, ConnectionError as CConnErr, TimeoutError


class DummyResponse:
    def __init__(self, status_code=200, url='http://test', headers=None):
        self.status_code = status_code
        self.url = url
        self.headers = headers or {}
    def json(self):
        return {'ok': True}


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    """Disable actual sleeping during retries."""
    monkeypatch.setattr(time, 'sleep', lambda s: None)
    yield


def test_handle_connection_error_timeout_and_connection(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=3, max_retries=1, retry_delay=0)
    # Timeout exception yields TimeoutError
    with pytest.raises(TimeoutError) as exc:
        client._handle_connection_error(requests.exceptions.Timeout(), 'urlX')
    assert 'urlX' in str(exc.value)
    # ConnectionError exception yields our ConnectionError
    with pytest.raises(CConnErr) as exc2:
        client._handle_connection_error(requests.exceptions.ConnectionError(), 'urlY')
    assert 'urlY' in str(exc2.value)
    # Other exception yields NetworkError
    with pytest.raises(NetworkError):
        client._handle_connection_error(ValueError('oops'), 'urlZ')


def test_post_json_success(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=2, retry_delay=0)
    # Successful POST returns JSON immediately
    resp = DummyResponse(status_code=200)
    monkeypatch.setattr(client.session, 'post', lambda url, json, timeout: resp)
    result = client.post_json('u', {'a': 1})
    assert result == {'ok': True}


def test_post_json_http_error_and_retry(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=2, retry_delay=0)
    # Always return HTTP 500 to trigger retry and then fallback
    resp = DummyResponse(status_code=500)
    monkeypatch.setattr(client.session, 'post', lambda url, json, timeout: resp)
    result = client.post_json('u', {'a': 1})
    assert result is None


def test_post_json_connection_and_decode_errors(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    # Simulate ConnectionError during post
    monkeypatch.setattr(client.session, 'post', lambda url, json, timeout: (_ for _ in ()).throw(requests.ConnectionError('fail')))
    result = client.post_json('u', None)
    assert result is None
    # Simulate JSON decoding error
    class BadJSON(DummyResponse):
        def json(self):
            raise json.JSONDecodeError('err', '', 0)
    monkeypatch.setattr(client.session, 'post', lambda url, json, timeout: BadJSON())
    result2 = client.post_json('u', None)
    assert result2 is None


def test_internal_post_handlers_and_retry_logic(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=3, retry_delay=0)
    # Test _should_retry_post behavior
    assert client._should_retry_post(None, 0)
    assert client._should_retry_post(None, 1)
    assert not client._should_retry_post(None, 2)
    # Test error handlers do not raise
    dummy_resp = DummyResponse(status_code=404)
    client._handle_post_error_response(dummy_resp)
    assert client._handle_post_connection_error(requests.ConnectionError(), 0) is None
    client._handle_post_json_error(json.JSONDecodeError('e', '', 0)) is None
    client._handle_post_request_error(requests.RequestException('e')) is None
