import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.getcwd())

import pytest

from scripts.civitai_manager_libs.downloader import (
    add_number_to_duplicate_files,
    download_file,
    download_file_gr,
)

from scripts.civitai_manager_libs import settings

config_manager = settings.config_manager


def test_add_number_to_duplicate_files_basic():
    files = ["1:file.txt", "2:file.txt", "3:other.txt"]
    mapping = add_number_to_duplicate_files(files)
    # Same base name should get a counter suffix
    assert mapping["1"] == "file.txt"
    assert mapping["2"].startswith("file (1)")
    # Unique names unchanged
    assert mapping["3"] == "other.txt"


@pytest.mark.parametrize(
    "files, expected",
    [
        ([], {}),
        (["a.txt"], {}),  # no colon entries
        (["1:img.png", "1:img.png", "2:img.png"], {"1": "img.png", "2": "img (1).png"}),
    ],
)
def test_add_number_parametrized(files, expected):
    result = add_number_to_duplicate_files(files)
    assert result == expected


def test_download_file_uses_chunked_downloader(monkeypatch):
    calls = []

    class DummyDownloader:
        def download_large_file(self, url, file_path):
            calls.append((url, file_path))
            return True

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.downloader.get_chunked_downloader', lambda: DummyDownloader()
    )
    assert download_file('http://test', 'path/to/file') is True
    assert calls == [('http://test', 'path/to/file')]


def test_download_file_gr_uses_http_client(monkeypatch):
    calls = []
    progress_calls = []

    class DummyClient:
        def download_file(self, url, file_path, progress_callback=None):
            calls.append((url, file_path))
            if progress_callback:
                # Simulate partial progress: downloaded=1, total=2
                progress_callback(1, 2)
            return True

    # Monkey-patch HTTP client factory for downloader
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.downloader.get_http_client', lambda: DummyClient()
    )

    # Use a callback function to capture progress updates
    def progress_callback(fraction, status_message):
        progress_calls.append((fraction, status_message))

    # Execute and verify
    assert download_file_gr('http://test', 'path/to/file', progress_callback) is True
    assert calls == [('http://test', 'path/to/file')]
    # Fraction should reflect downloaded/total = 1/2
    assert progress_calls and progress_calls[-1][0] == 0.5
