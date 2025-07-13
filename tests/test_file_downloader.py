import os
import time
import tempfile

import pytest

from scripts.civitai_manager_libs.http.file_downloader import FileDownloadMixin
from scripts.civitai_manager_libs.http.file_downloader import AuthenticationError


class DummyClient(FileDownloadMixin):
    """Dummy client to access FileDownloadMixin methods without HTTP calls."""
    pass


@pytest.fixture(autouse=True)
def patch_settings(monkeypatch):
    # Ensure resume enabled by default for testing
    import scripts.civitai_manager_libs.http.file_downloader as fd_mod
    monkeypatch.setattr(fd_mod.settings, 'download_resume_enabled', True)
    monkeypatch.setattr(fd_mod.settings, 'download_chunk_size', 4)
    yield


def test_prepare_download_headers_and_resume(tmp_path):
    client = DummyClient()
    # No resume position
    headers0 = client._prepare_download_headers(None, 0)
    assert headers0 == {}
    # With resume position and initial headers
    base = {'A': '1'}
    hdr = client._prepare_download_headers(base, 10)
    assert hdr.get('Range') == 'bytes=10-'
    # original headers unchanged
    assert base == {'A': '1'}


class DummyResponse:
    def __init__(self, length):
        self.headers = {'Content-Length': str(length)}


def test_calculate_total_size():
    client = DummyClient()
    resp = DummyResponse(100)
    # no resume
    assert client._calculate_total_size(resp, 0) == 100
    # with resume
    assert client._calculate_total_size(resp, 40) == 140


def test_get_resume_position(tmp_path):
    client = DummyClient()
    file = tmp_path / 'f.bin'
    # no file -> zero
    assert client._get_resume_position(str(file)) == 0
    # create file
    content = b'12345'
    file.write_bytes(content)
    pos = client._get_resume_position(str(file))
    assert pos == len(content)


def test_create_download_tracker_and_speed():
    client = DummyClient()
    tracker = client._create_download_tracker()
    assert 'start_time' in tracker and 'last_update' in tracker
    # simulate speed calculation
    speed = client._calculate_speed(1024, 1)
    assert speed.endswith('KB/s')
    speed2 = client._calculate_speed(512, 1)
    assert speed2.endswith('B/s')
    speed3 = client._calculate_speed(2 * 1024 * 1024, 1)
    assert speed3.endswith('MB/s')


def test_update_and_final_download_progress(monkeypatch):
    client = DummyClient()
    # prepare a tracker with interval zero to always update
    tracker = {'start_time': time.time(), 'last_update': time.time() - 1, 'update_interval': 0}
    calls = []
    def cb(downloaded, total, speed):
        calls.append((downloaded, total, speed))
    # update and final
    client._update_download_progress(cb, 5, 10, 0, tracker)
    client._send_final_download_progress(cb, 10, 10, 0, tracker)
    assert calls, 'Progress callbacks should be invoked'


def test_cleanup_and_validate_download_size(tmp_path, monkeypatch):
    client = DummyClient()
    # test cleanup: zero-size file removed
    file = tmp_path / 'tmp.bin'
    file.write_bytes(b'')
    client._cleanup_failed_download(str(file))
    assert not file.exists()
    # test validate: missing file
    assert not client._validate_download_size(str(file), 10)
    # test validate success when expected_size<=0
    file2 = tmp_path / 'a'
    file2.write_bytes(b'xyz')
    assert client._validate_download_size(str(file2), 0)
    # test validate mismatch triggers warning
    # patch notification service to capture warning
    from scripts.civitai_manager_libs.http.file_downloader import get_notification_service
    class Notifier:
        def __init__(self): self.warn = []
        def show_warning(self, msg): self.warn.append(msg)
    monkeypatch.setattr('scripts.civitai_manager_libs.http.file_downloader.get_notification_service', lambda: Notifier())
    # expected size small to trigger mismatch
    assert not client._validate_download_size(str(file2), 100)


def test_process_download_error_type(monkeypatch):
    client = DummyClient()
    import requests
    # Timeout
    err = requests.exceptions.Timeout()
    assert client._process_download_error_type(err, 'url')
    # ConnectionError
    err2 = requests.exceptions.ConnectionError()
    assert client._process_download_error_type(err2, 'url')
    # response error
    class E(Exception): pass
    resp = type('R', (), {})()
    setattr(resp, 'response', resp)
    assert not client._process_download_error_type(E(), 'url')


def test_handle_download_error_auth_and_other(tmp_path):
    client = DummyClient()
    # auth error should re-raise
    with pytest.raises(AuthenticationError):
        client._handle_download_error(AuthenticationError('auth'), 'u', 'p')
    # other error cleans up and returns False
    file = tmp_path / 'x'
    file.write_bytes(b'')
    ok = client._handle_download_error(Exception('oops'), 'u', str(file))
    assert ok is False
    assert not file.exists()
