import os
import time
import tempfile

import pytest

from scripts.civitai_manager_libs.http.file_downloader import FileDownloadMixin
from scripts.civitai_manager_libs.exceptions import AuthenticationError


class DummyMixin(FileDownloadMixin):
    def __init__(self):
        pass


class DummyStreamResp:
    def __init__(self, chunks, headers=None):
        self._chunks = chunks
        self.headers = headers or {}

    def iter_content(self, chunk_size=0):
        yield from self._chunks


def test_download_file_success(tmp_path):
    d = DummyMixin()
    # simulate stream with content length header and chunks
    resp = DummyStreamResp([b'aa', b'bb', b''], {'Content-Length': '4'})
    d.get_stream = lambda url: resp
    progress = []
    fp = tmp_path / 'out.bin'
    ok = d.download_file('url', str(fp), progress_callback=lambda dl, tot: progress.append((dl, tot)))
    assert ok is True
    assert fp.read_bytes() == b'aabb'
    assert any(dl == 4 and tot == 4 for dl, tot in progress)


def test_download_file_no_response(tmp_path):
    d = DummyMixin()
    d.get_stream = lambda url: None
    fp = tmp_path / 'none.bin'
    assert d.download_file('url', str(fp)) is False


def test_get_resume_position(monkeypatch, tmp_path):
    d = DummyMixin()
    monkeypatch.setattr('scripts.civitai_manager_libs.http.file_downloader.settings',
                        type('S', (), {'download_resume_enabled': True}))
    f = tmp_path / 'f'
    f.write_text('x')
    monkeypatch.setattr(os.path, 'exists', lambda p: True)
    monkeypatch.setattr(os.path, 'getsize', lambda p: 5)
    assert d._get_resume_position(str(f)) == 5


def test_prepare_headers_and_calc_size():
    d = DummyMixin()
    # headers none, resume 0
    hdr = d._prepare_download_headers(None, 0)
    assert hdr == {}
    # resume >0
    hdr2 = d._prepare_download_headers({'A': 'B'}, 10)
    assert hdr2.get('Range') == 'bytes=10-'
    # calculate total size
    class R:
        headers = {'Content-Length': '3'}
    assert d._calculate_total_size(R(), 0) == 3
    assert d._calculate_total_size(R(), 2) == 5


def test_calculate_speed():
    d = DummyMixin()
    assert d._calculate_speed(10, 0) == ''
    assert 'B/s' in d._calculate_speed(10, 1)
    assert 'KB/s' in d._calculate_speed(1024, 1)
    assert 'MB/s' in d._calculate_speed(1024*1024, 1)


def test_handle_download_error_rethrows_auth(monkeypatch):
    d = DummyMixin()
    ae = AuthenticationError('msg', status_code=401)
    with pytest.raises(AuthenticationError):
        d._handle_download_error(ae, 'u', 'p')


def test_process_download_error_types(monkeypatch):
    d = DummyMixin()
    import requests
    # Timeout
    err1 = requests.Timeout()
    assert d._process_download_error_type(err1, 'u') is True
    # ConnectionError
    err2 = requests.ConnectionError()
    assert d._process_download_error_type(err2, 'u') is True
    # response attr
    class E:
        response = True
    assert d._process_download_error_type(E(), 'u') is True
    # other
    assert d._process_download_error_type(Exception(), 'u') is False


def test_handle_timeout_and_connection_and_response_error():
    d = DummyMixin()
    assert d._handle_timeout_error('u') is True
    assert d._handle_connection_error_download('u') is True
    assert d._handle_download_response_error(type('R', (), {})()) is True


def test_cleanup_failed_download(tmp_path):
    d = DummyMixin()
    f = tmp_path / 'zero'
    f.write_text('')
    assert f.exists()
    d._cleanup_failed_download(str(f))
    assert not f.exists()


def test_validate_download_size(monkeypatch, tmp_path):
    d = DummyMixin()
    f = tmp_path / 'f'
    # not exists
    assert d._validate_download_size(str(f), 10) is False
    # exists expected_size<=0
    f.write_text('data')
    assert d._validate_download_size(str(f), 0) is True
    # mismatch > tolerance
    monkeypatch.setattr('scripts.civitai_manager_libs.http.file_downloader.util',
                        type('U', (), {'format_file_size': lambda x: f'{x}B'}))
    class Svc:
        def __init__(self): self.warnings=[]
        def show_warning(self, msg): self.warnings.append(msg)
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.http.file_downloader.get_notification_service',
        lambda: Svc()
    )
    # actual size 4 expected 2 -> mismatch
    assert d._validate_download_size(str(f), 2) is False
    # within tolerance
    assert d._validate_download_size(str(f), 4) is True
