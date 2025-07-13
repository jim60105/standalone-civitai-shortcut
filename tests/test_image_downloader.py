import threading
import time

import pytest

from scripts.civitai_manager_libs.http.image_downloader import ParallelImageDownloader
from scripts.civitai_manager_libs.exceptions import AuthenticationError


def test_download_images_empty():
    d = ParallelImageDownloader(max_workers=2)
    assert d.download_images([]) == 0


def test_download_images_success(monkeypatch):
    stub_client = type('C', (), {'download_file': lambda self, u, p: True})()
    tasks = [('u1', 'p1'), ('u2', 'p2')]
    d = ParallelImageDownloader(max_workers=2)
    result = d.download_images(tasks, progress_callback=None, client=stub_client)
    assert result == 2


def test_download_images_auth_error(monkeypatch):
    # stub client raising AuthenticationError
    # stub client raising AuthenticationError
    def dl_fail(self, u, p):
        raise AuthenticationError('auth fail', status_code=401)

    stub_client = type('C', (), {'download_file': dl_fail})()
    # record notification on persistent service
    class Svc:
        def __init__(self): self.errors = []
        def show_error(self, msg): self.errors.append(msg)

    svc = Svc()
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.http.image_downloader.get_notification_service',
        lambda: svc,
    )
    tasks = [('u', 'p')]
    d = ParallelImageDownloader(max_workers=1)
    result = d.download_images(tasks, progress_callback=None, client=stub_client)
    assert result == 0
    # ensure auth error notified
    assert svc.errors
