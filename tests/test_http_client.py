import json
import pytest
import requests

from scripts.civitai_manager_libs.http.client import (
    CivitaiHttpClient,
    _STATUS_CODE_MESSAGES,
)
from scripts.civitai_manager_libs.exceptions import (
    HTTPError,
    TimeoutError,
    ConnectionError,
    NetworkError,
    AuthenticationError,
)


class DummyResponse:
    def __init__(self, status_code=200, url='http://test', headers=None, json_data=None):
        self.status_code = status_code
        self.url = url
        self.headers = headers or {}
        self._json_data = json_data or {}

    def json(self):
        return self._json_data


def test_handle_response_error_raises_http_error():
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    resp = DummyResponse(status_code=404, url='http://x')
    with pytest.raises(HTTPError) as exc:
        client._handle_response_error(resp)
    assert exc.value.status_code == 404
    assert 'Not Found' in str(exc.value)


def test_update_api_key_updates_header():
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    client.session.headers.clear()
    client.update_api_key('abc123')
    assert client.api_key == 'abc123'
    assert client.session.headers.get('Authorization') == 'Bearer abc123'


def test_get_json_success(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    resp = DummyResponse(status_code=200, url='u', json_data={'a': 1})
    monkeypatch.setattr(client.session, 'get', lambda url, params=None, timeout=None: resp)
    data = client.get_json('u', {'p': 'v'})
    assert data == {'a': 1}


def test_get_json_error_returns_none(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    def bad_get(*args, **kwargs):
        raise requests.RequestException("fail")
    monkeypatch.setattr(client.session, 'get', bad_get)
    assert client.get_json('u') is None


def test_post_json_success(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=2, retry_delay=0)
    monkeypatch.setattr(client, '_attempt_post_request', lambda url, data, attempt: {'ok': True})
    res = client.post_json('u', {'x': 1})
    assert res == {'ok': True}


def test_post_json_retry(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=2, retry_delay=0)
    calls = []
    def attempt(url, data, attempt_idx):
        calls.append(attempt_idx)
        return None
    monkeypatch.setattr(client, '_attempt_post_request', attempt)
    res = client.post_json('u', {})
    assert res is None
    assert calls == [0, 1]


def test_attempt_post_request_error_responses(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    class ErrResp(DummyResponse):
        def __init__(self):
            super().__init__(status_code=500)
    resp = ErrResp()
    monkeypatch.setattr(client.session, 'post', lambda url, json=None, timeout=None: resp)
    result = client._attempt_post_request('u', {}, 0)
    assert result is None


def test_attempt_post_request_connection_error(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    def bad_post(url, json=None, timeout=None):
        raise requests.ConnectionError("conn")
    monkeypatch.setattr(client.session, 'post', bad_post)
    result = client._attempt_post_request('u', {}, 0)
    assert result is None


def test_attempt_post_request_json_error(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    class R(DummyResponse):
        def __init__(self):
            super().__init__(status_code=200)
        def json(self):
            raise json.JSONDecodeError("msg", "doc", 0)
    monkeypatch.setattr(client.session, 'post', lambda u, json=None, timeout=None: R())
    result = client._attempt_post_request('u', {}, 0)
    assert result is None


def test_should_retry_post():
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=3, retry_delay=0)
    assert client._should_retry_post(None, 0)
    assert client._should_retry_post(None, 1)
    assert not client._should_retry_post({'a': 1}, 0)
    assert not client._should_retry_post(None, 2)


def test_handle_stream_error_response(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    # dummy notification service
    class Svc:
        def __init__(self):
            self.errors = []
        def show_error(self, msg):
            self.errors.append(msg)
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.http.client.get_notification_service',
        lambda: Svc(),
    )
    resp = DummyResponse(status_code=500, url='u', headers={})
    ok = client._handle_stream_error_response(resp)
    assert ok is False


def test_handle_redirect_response():
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    resp = DummyResponse(status_code=301, url='u', headers={'Location': 'new'})
    assert client._handle_redirect_response(resp)


def test_handle_authentication_error():
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    resp = DummyResponse(status_code=307, url='u', headers={'Location': 'login'})
    with pytest.raises(AuthenticationError):
        client._handle_authentication_error(resp, 'HTTP 307 login redirect')
