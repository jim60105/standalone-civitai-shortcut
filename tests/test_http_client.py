import json

import pytest

import requests

from scripts.civitai_manager_libs.http_client import CivitaiHttpClient, _STATUS_CODE_MESSAGES


class DummyResponse:
    def __init__(self, status_code=200, data=None, headers=None, raise_json=False):
        self.status_code = status_code
        self._data = data or {}
        self.headers = headers or {}
        self._raise_json = raise_json

    def json(self):
        if self._raise_json:
            raise json.JSONDecodeError("msg", "doc", 0)
        return self._data

    @property
    def text(self):
        return json.dumps(self._data)

    def iter_content(self, chunk_size=1):
        yield from [b"abc", b"123"]


@pytest.fixture(autouse=True)
def disable_gr_error(monkeypatch):
    # Prevent gradio.Error calls from interfering tests
    monkeypatch.setattr(
        "scripts.civitai_manager_libs.http_client.gr.Error", lambda *args, **kwargs: None
    )


@pytest.fixture(autouse=True)
def disable_printD(monkeypatch):
    monkeypatch.setattr(
        "scripts.civitai_manager_libs.http_client.util.printD", lambda *args, **kwargs: None
    )


def test_get_json_success(monkeypatch):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=200, data={"key": "value"})
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: dummy)
    result = client.get_json("http://test")
    assert result == {"key": "value"}


@pytest.mark.parametrize("code", [400, 404, 500])
def test_get_json_http_error(monkeypatch, code):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=code)
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: dummy)
    assert client.get_json("http://test") is None


def test_get_json_connection_error(monkeypatch):
    client = CivitaiHttpClient(max_retries=1)

    def raise_conn(*args, **kwargs):
        raise requests.exceptions.ConnectionError

    monkeypatch.setattr(client.session, "get", raise_conn)
    assert client.get_json("http://test") is None


def test_get_json_timeout(monkeypatch):
    client = CivitaiHttpClient(max_retries=1)

    def raise_to(*args, **kwargs):
        raise requests.exceptions.Timeout

    monkeypatch.setattr(client.session, "get", raise_to)
    assert client.get_json("http://test") is None


def test_get_json_json_error(monkeypatch):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=200, data=None, raise_json=True)
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: dummy)
    assert client.get_json("http://test") is None


def test_post_json_success(monkeypatch):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=200, data={"ok": True})
    monkeypatch.setattr(client.session, "post", lambda *args, **kwargs: dummy)
    result = client.post_json("http://test", json_data={})
    assert result == {"ok": True}


@pytest.mark.parametrize("code", [401, 503])
def test_post_json_http_error(monkeypatch, code):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=code)
    monkeypatch.setattr(client.session, "post", lambda *args, **kwargs: dummy)
    assert client.post_json("http://test", json_data={}) is None


def test_get_stream_success(monkeypatch):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=200)
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: dummy)
    resp = client.get_stream("http://test")
    assert resp is dummy


def test_get_stream_http_error(monkeypatch):
    client = CivitaiHttpClient()
    dummy = DummyResponse(status_code=404)
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: dummy)
    assert client.get_stream("http://test") is None


def test_download_file_success(monkeypatch, tmp_path):
    client = CivitaiHttpClient()
    # Mock get_stream to return DummyResponse with headers
    dummy = DummyResponse(status_code=200, headers={"content-length": "6"})
    monkeypatch.setattr(client, "get_stream", lambda url: dummy)
    target = tmp_path / "out.bin"
    called = []

    def prog(downloaded, total):
        called.append((downloaded, total))

    success = client.download_file("http://test", str(target), progress_callback=prog)
    assert success
    assert target.read_bytes() == b"abc123"
    assert called[-1] == (6, 6)


def test_download_file_stream_fail(monkeypatch, tmp_path):
    client = CivitaiHttpClient()
    monkeypatch.setattr(client, "get_stream", lambda url: None)
    target = tmp_path / "out.bin"
    assert not client.download_file("http://test", str(target))


def test_status_code_messages_defined():
    # Ensure the status code mapping is available
    assert isinstance(_STATUS_CODE_MESSAGES, dict)
    # Common HTTP error codes should be present
    for code in (400, 401, 403, 404, 429, 500, 502, 503, 504, 524):
        assert code in _STATUS_CODE_MESSAGES
