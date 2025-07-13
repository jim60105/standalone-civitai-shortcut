import json
import urllib.parse

import pytest

import requests
from scripts.civitai_manager_libs.http.client import CivitaiHttpClient, _STATUS_CODE_MESSAGES
from scripts.civitai_manager_libs.exceptions import HTTPError, TimeoutError, ConnectionError as ConnErr, NetworkError, AuthenticationError


class DummyResponse:
    def __init__(self, status_code=200, url='http://test', headers=None, content=b''):
        self.status_code = status_code
        self.url = url
        self.headers = headers or {}
        self._content = content

    def json(self):
        return {'ok': True}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError()

    @property
    def text(self):
        return self._content.decode('utf-8', errors='ignore')


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    # Prevent real HTTP calls
    monkeypatch.setattr(requests.Session, 'get', lambda self, *args, **kwargs: DummyResponse())
    monkeypatch.setattr(requests.Session, 'post', lambda self, *args, **kwargs: DummyResponse())
    yield


def test_update_api_key_changes_header():
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    client.update_api_key('newkey')
    assert 'Authorization' in client.session.headers
    assert client.session.headers['Authorization'] == 'Bearer newkey'


def test_handle_response_error_raises_for_status():
    client = CivitaiHttpClient()
    # Only status codes >=400 should raise HTTPError
    for code, msg in _STATUS_CODE_MESSAGES.items():
        if code < 400:
            continue
        resp = DummyResponse(status_code=code, url='u')
        with pytest.raises(HTTPError) as exc:
            client._handle_response_error(resp)
        assert exc.value.status_code == code


def test_handle_connection_error_types():
    client = CivitaiHttpClient()
    # Timeout
    with pytest.raises(TimeoutError):
        client._handle_connection_error(requests.exceptions.Timeout(), 'u')
    # ConnectionError
    with pytest.raises(ConnErr):
        client._handle_connection_error(requests.exceptions.ConnectionError(), 'u')
    # Other
    with pytest.raises(NetworkError):
        client._handle_connection_error(Exception('fail'), 'u')


def test_get_json_success_and_decorator(monkeypatch):
    client = CivitaiHttpClient()
    # monkeypatch session.get to return ok
    result = client.get_json('http://x')
    assert result == {'ok': True}


def test_post_json_retries_and_error(monkeypatch):
    client = CivitaiHttpClient(timeout=0, max_retries=2, retry_delay=0)
    calls = {'cnt': 0}

    def attempt(url, data, attempt):
        calls['cnt'] += 1
        return None

    monkeypatch.setattr(client, '_attempt_post_request', attempt)
    monkeypatch.setattr(client, '_should_retry_post', lambda res, att: att < client.max_retries - 1)
    res = client.post_json('u', {'a': 1})
    assert res is None
    assert calls['cnt'] == client.max_retries


def test_should_retry_post():
    client = CivitaiHttpClient(timeout=0, max_retries=3, retry_delay=0)
    assert client._should_retry_post(None, 0)
    assert client._should_retry_post(None, 1)
    assert not client._should_retry_post({'ok': True}, 1)
    assert not client._should_retry_post(None, client.max_retries - 1)


def test_is_stream_response_valid_and_stream_logic(monkeypatch):
    client = CivitaiHttpClient()
    # 416 triggers AuthenticationError
    resp = DummyResponse(status_code=416)
    with pytest.raises(AuthenticationError):
        client._is_stream_response_valid(resp)
    # 307 login redirect
    resp = DummyResponse(status_code=307, headers={'Location': 'https://login'})
    with pytest.raises(AuthenticationError):
        client._is_stream_response_valid(resp)
    # other 307 non-login returns True
    resp = DummyResponse(status_code=307, headers={'Location': 'https://x'})
    assert client._is_stream_response_valid(resp)
    # redirect codes
    for code in [301, 302, 303, 308]:
        resp = DummyResponse(status_code=code, headers={'Location': 'l'})
        assert client._is_stream_response_valid(resp)
    # error >=400
    # patch notification service
    class Notif:
        def __init__(self): self.err = []
        def show_error(self, m): self.err.append(m)
    monkeypatch.setattr('scripts.civitai_manager_libs.http.client.get_notification_service', lambda: Notif())
    resp = DummyResponse(status_code=500)
    assert not client._is_stream_response_valid(resp)


def test_get_stream_response_calls_get_stream(monkeypatch):
    client = CivitaiHttpClient()
    monkeypatch.setattr(client, 'get_stream', lambda url, headers=None, _origin_host=None: 'STREAM')
    assert client.get_stream_response('u') == 'STREAM'
