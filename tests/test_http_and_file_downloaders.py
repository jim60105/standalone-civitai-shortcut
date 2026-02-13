import json
import os
import time
import threading

import pytest

from scripts.civitai_manager_libs.http.client import CivitaiHttpClient
from scripts.civitai_manager_libs.http.image_downloader import ParallelImageDownloader
from scripts.civitai_manager_libs.http.file_downloader import FileDownloadMixin


class DummyResponse:
    def __init__(self, status_code=200, url="http://test", headers=None, data_chunks=None):
        self.status_code = status_code
        self.url = url
        self.headers = headers or {}
        self._chunks = data_chunks or []

    def json(self):
        return {"ok": True}

    def iter_content(self, chunk_size=8192):
        for chunk in self._chunks:
            yield chunk


class DummySession:
    def __init__(self, response):
        self.headers = {}
        self._response = response

    def get(self, url, params=None, timeout=None, headers=None, stream=False, allow_redirects=True):
        return self._response

    def post(self, url, json=None, timeout=None):
        return self._response


def test_get_json_success(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    resp = DummyResponse(status_code=200)
    client.session = DummySession(resp)
    result = client.get_json("http://test")
    assert result == {"ok": True}


def test_get_json_http_error(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    resp = DummyResponse(status_code=404)
    client.session = DummySession(resp)
    assert client.get_json("http://bad") is None


def test_post_json_success(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=2, retry_delay=0)
    resp = DummyResponse(status_code=200)
    client.session = DummySession(resp)
    data = client.post_json("http://post", json_data={"a": 1})
    assert data == {"ok": True}


def test_post_json_failure_and_json_error(monkeypatch):
    # status error
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    resp_err = DummyResponse(status_code=500)
    client.session = DummySession(resp_err)
    assert client.post_json("http://post") is None

    # json decode error
    class RespBadJson(DummyResponse):
        def json(self):
            raise json.JSONDecodeError("msg", "doc", 0)

    client.session = DummySession(RespBadJson(status_code=200))
    assert client.post_json("http://post") is None


def test_update_api_key_changes_header(monkeypatch):
    client = CivitaiHttpClient(api_key="old", timeout=1, max_retries=1, retry_delay=0)
    client.update_api_key("newkey")
    assert client.api_key == "newkey"
    assert client.session.headers.get("Authorization") == "Bearer newkey"


def test_get_stream_simple(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    resp = DummyResponse(status_code=200)
    client.session = DummySession(resp)
    result = client.get_stream("http://host/path")
    assert result is resp


def test_get_stream_authentication_error(monkeypatch):
    client = CivitaiHttpClient(api_key=None, timeout=1, max_retries=1, retry_delay=0)
    # stub response with 416 triggers AuthenticationError inside
    from scripts.civitai_manager_libs.exceptions import AuthenticationError

    resp = DummyResponse(status_code=416, url="http://test")
    client.session = DummySession(resp)
    # decorator returns None on exception
    with pytest.raises(AuthenticationError):
        client.get_stream("http://test")


def test_parallel_image_downloader_empty(monkeypatch):
    downloader = ParallelImageDownloader(max_workers=2)
    assert downloader.download_images([], progress_callback=None) == 0


def test_parallel_image_downloader_progress_and_auth(monkeypatch):
    # Prepare two tasks: one succeeds, one auth error
    calls = []

    class StubClient:
        def download_file(self, url, path):
            if "bad" in url:
                from scripts.civitai_manager_libs.exceptions import AuthenticationError

                raise AuthenticationError("auth fail", status_code=401)
            return True

    def progress_cb(done, total, desc):
        calls.append((done, total, desc))

    tasks = [("good_url", "p1"), ("bad_url", "p2")]
    downloader = ParallelImageDownloader(max_workers=2)
    count = downloader.download_images(tasks, progress_callback=progress_cb, client=StubClient())
    # Only one success
    assert count == 1
    # progress callback called at least final update
    assert calls, "Progress callback not called"


def test_file_download_mixin_success_and_resume(tmp_path, monkeypatch):
    # Create mixin instance
    class Tester(FileDownloadMixin):
        def get_stream(self, url, headers=None):
            headers_resp = {"Content-Length": "6"}
            data = [b"abc", b"def"]
            return DummyResponse(status_code=200, headers=headers_resp, data_chunks=data)

    t = Tester()
    # test download_file
    dest = tmp_path / "out.bin"
    assert t.download_file("u", str(dest))
    assert dest.read_bytes() == b"abcdef"
    # test resume download (initial)
    dest2 = tmp_path / "out2.bin"
    assert t.download_file_with_resume("u", str(dest2), headers={})
    assert dest2.exists()

    # test speed formatting and header preparation
    assert t._calculate_speed(1024, 1).endswith("KB/s")
    hdrs = t._prepare_download_headers({"A": "B"}, resume_pos=10)
    assert hdrs.get("Range") == "bytes=10-"


def test_cleanup_and_validate(tmp_path, monkeypatch):
    class Tester(FileDownloadMixin):
        pass

    t = Tester()
    # cleanup zero size
    f = tmp_path / "zero.bin"
    f.write_bytes(b"")
    t._cleanup_failed_download(str(f))
    assert not f.exists()
    # validate size match
    f2 = tmp_path / "file2.bin"
    f2.write_bytes(b"1234")
    assert t._validate_download_size(str(f2), expected_size=4)
    # validate size mismatch triggers warning
    warnings = []

    class WarnSvc:
        def show_warning(self, msg):
            warnings.append(msg)

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.http.file_downloader.get_notification_service',
        lambda: WarnSvc(),
    )
    assert not t._validate_download_size(str(f2), expected_size=1)
    assert warnings, "Warning not triggered on size mismatch"


# Download module tests below
from scripts.civitai_manager_libs.download.task_manager import (
    download_file_with_auth_handling,
    download_file_with_retry,
    download_file_with_file_handling,
    download_file_with_notifications,
    download_file,
    download_file_gr,
    DownloadTask,
    DownloadManager,
)
from scripts.civitai_manager_libs.download.notifier import DownloadNotifier
from scripts.civitai_manager_libs.download.utilities import (
    add_number_to_duplicate_files,
    get_save_base_name,
    download_preview_image,
    _is_lora_model,
)


class StubClientDM:
    def download_file_with_resume(self, url, path, headers=None, progress_callback=None):
        return True

    def download_file(self, url, file_path, progress_callback=None):
        return True


def test_download_handlers(monkeypatch):
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.get_http_client',
        lambda: StubClientDM(),
    )
    task = DownloadTask(1, 'f', 'u', 'p')
    assert download_file_with_auth_handling(task)
    assert download_file_with_retry(task)
    assert download_file_with_file_handling(task)
    assert download_file_with_notifications(task)


def test_download_file_and_gr(monkeypatch):
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.get_http_client',
        lambda: StubClientDM(),
    )
    assert download_file('u', 'p')
    assert download_file_gr('u', 'p', progress_gr=lambda v, d: None)


def test_add_number_and_save_base_and_preview(monkeypatch, tmp_path):
    # add_number_to_duplicate_files
    files = ['1:foo.txt', '2:foo.txt', '3:bar.png', 'bad']
    mapping = add_number_to_duplicate_files(files)
    assert '1' in mapping and mapping['3'] == 'bar.png'
    # get_save_base_name fallback
    vi = {'images': [], 'model': {'name': 'm'}, 'name': 'v', 'id': 99}
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.civitai.get_primary_file_by_version_info',
        lambda x: None,
    )
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.settings.generate_version_foldername',
        lambda m, n, i: 'gen',
    )
    assert get_save_base_name(vi) == 'gen'
    # preview image invalid
    assert download_preview_image(str(tmp_path / 'f'), {}) is False
    vi2 = {'images': [{'url': 'http://example.com/img.jpeg', 'type': 'image'}]}
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.get_http_client',
        lambda: StubClientDM(),
    )
    assert download_preview_image(str(tmp_path / 'f'), vi2) is True


def test_is_lora_model_types():
    assert not _is_lora_model({})
    assert _is_lora_model({'model': {'type': 'lora'}})
    assert _is_lora_model({'model': {'type': 'LyCoRiS'}})


def test_download_manager_sync(monkeypatch):
    # make threads synchronous
    class DummyThread:
        def __init__(self, target, args):
            self._target, self._args = target, args

        def start(self):
            self._target(*self._args)

        def daemon(self, d):
            pass

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.threading.Thread',
        DummyThread,
    )
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.get_http_client',
        lambda: StubClientDM(),
    )
    mgr = DownloadManager()
    tid = mgr.start('u', 'p', progress_cb=None)
    assert not mgr.list_active()
    assert mgr.history and mgr.history[0].get('success') is True


def test_notifier_logging(monkeypatch, caplog):
    calls = []

    class Svc:
        def show_info(self, m, duration=None):
            calls.append(('info', m))

        def show_error(self, m, duration=None):
            calls.append(('error', m))

        def show_warning(self, m, duration=None):
            calls.append(('warn', m))

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.notifier.get_notification_service',
        lambda: Svc(),
    )
    DownloadNotifier.notify_start('f', 10)
    assert any('Starting download' in m for _, m in calls)
    caplog.set_level('DEBUG')
    DownloadNotifier.notify_progress('f', 5, 10, '1 B/s')
    assert '[downloader] Progress:' in caplog.text
    calls.clear()
    caplog.clear()
    DownloadNotifier.notify_complete('f', True)
    assert any('Download completed' in m for _, m in calls)
    DownloadNotifier.notify_complete('f', False, 'err')
    assert any('Download failed' in m for _, m in calls)
