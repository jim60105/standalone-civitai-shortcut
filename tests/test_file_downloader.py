"""Unit tests for FileDownloadMixin resume download and speed calculation."""
import os
import time

import pytest

from scripts.civitai_manager_libs.http.file_downloader import FileDownloadMixin
import scripts.civitai_manager_libs.http.file_downloader as fd_mod
import scripts.civitai_manager_libs.settings as settings


class DummyDownloader(FileDownloadMixin):
    """Dummy subclass to expose mixin methods for testing."""
    pass


@pytest.fixture(autouse=True)
def patch_create_tracker(monkeypatch):
    """Patch tracker to update immediately for progress callback."""
    monkeypatch.setattr(fd_mod.FileDownloadMixin, '_create_download_tracker',
                        lambda self: {'start_time': 0.0, 'last_update': 0.0, 'update_interval': 0.0})
    yield


def test_calculate_speed_various_units():
    dl = DummyDownloader()
    # Zero elapsed time yields empty string
    assert dl._calculate_speed(100, 0) == ''
    # Bytes per second
    assert dl._calculate_speed(500, 1) == '500.0 B/s'
    # Kilobytes per second
    assert dl._calculate_speed(2048, 1) == '2.0 KB/s'
    # Megabytes per second
    assert dl._calculate_speed(2 * 1024 * 1024, 1) == '2.0 MB/s'


def test_perform_resume_download_success_and_failure(tmp_path):
    dl = DummyDownloader()
    # Prepare initial file with resume_pos bytes
    filepath = tmp_path / 'test.bin'
    filepath.write_bytes(b'ABC')
    resume_pos = 3
    # Fake response yielding two chunks of data
    class Resp:
        headers = {}
        def __init__(self, chunks):
            self._chunks = chunks
        def iter_content(self, chunk_size=1):
            for c in self._chunks:
                yield c

    # Patch settings for chunk size
    settings.download_chunk_size = 1

    # Collect progress callback calls
    calls = []
    def progress(downloaded, total, speed):
        calls.append((downloaded, total, speed))

    # Success case: total_size matches actual downloaded size
    data = [b'DE', b'F']  # total new bytes = 3
    resp = Resp(data)
    total_size = resume_pos + sum(len(c) for c in data)
    result = dl._perform_resume_download(str(filepath), resp, resume_pos, total_size, progress)
    # Should succeed, and file size matches
    assert result is True
    assert os.path.getsize(filepath) == total_size
    # Progress callback should have been called at least once and final update
    assert any(call[0] == total_size for call in calls)

    # Failure case: total_size mismatch leads to validation failure
    # Reset file
    filepath.write_bytes(b'ABC')
    calls.clear()
    wrong_total = resume_pos + 100
    resp2 = Resp([b'X', b'Y'])
    result2 = dl._perform_resume_download(str(filepath), resp2, resume_pos, wrong_total, progress)
    assert result2 is False
