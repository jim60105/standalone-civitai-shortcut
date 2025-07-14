import os
import threading

import pytest

from scripts.civitai_manager_libs.download.task_manager import (
    DownloadTask,
    download_file_with_auth_handling,
    download_file_with_retry,
    download_file_with_file_handling,
    download_file_with_notifications,
    download_image_file,
    download_file,
    download_file_gr,
    DownloadManager,
)


class DummyClient:
    def download_file_with_resume(self, url, path):
        return True


@pytest.fixture(autouse=True)
def stub_http_client(monkeypatch):
    # stub get_http_client for auth, retry, file handling
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.get_http_client',
        lambda: DummyClient(),
    )


def test_download_task_classes_and_wrappers(tmp_path):
    task = DownloadTask(1, 'f', 'u', str(tmp_path / 'f'))
    assert task.fid == 1 and task.url == 'u'
    # auth handling should return True via stub client
    assert download_file_with_auth_handling(task)
    assert download_file_with_retry(task)
    assert download_file_with_file_handling(task)
    # notifications chains wrappers
    # monkeypatch underlying functions to control
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.download_file_with_auth_handling',
        lambda t: False,
    )
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.download_file_with_retry',
        lambda t: False,
    )
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.download_file_with_file_handling',
        lambda t: True,
    )
    assert download_file_with_notifications(task)
    monkeypatch.undo()


def test_download_file_and_gr(monkeypatch, tmp_path):
    # stub get_http_client.download_file
    class C:
        def download_file(self, u, p, progress_callback=None):
            return True

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.get_http_client',
        lambda: C(),
    )
    p = tmp_path / 'out'
    assert download_file('u', str(p))
    # progress wrapper can be provided but download completion is sufficient
    assert download_file_gr('u', str(p), progress_gr=lambda frac, desc: None)


def test_download_image_file_early(monkeypatch):
    # empty inputs
    assert download_image_file('', []) is None
    assert download_image_file('name', []) is None
    # make_download_image_folder returns falsy
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.util.make_download_image_folder',
        lambda name: '',
    )
    assert download_image_file('name', ['u']) is None


def test_download_image_file_final(monkeypatch, tmp_path):
    # cover final progress update
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.util.make_download_image_folder',
        lambda n: str(tmp_path / 'm'),
    )
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.util.is_url_or_filepath',
        lambda u: 'url'
    )
    # stub ParallelImageDownloader
    class PD:
        def __init__(self, max_workers): pass
        def download_images(self, tasks, progress_wrapper): return len(tasks)

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.ParallelImageDownloader',
        PD,
    )
    # call with dummy data and capture final progress
    progress = []
    def pg(frac, desc):
        progress.append((frac, desc))
    download_image_file('name', ['u1', 'u2'], progress_gr=pg)
    assert any(f == 1.0 for f, _ in progress)


def test_download_manager_start_cancel(monkeypatch):
    # stub thread to avoid running
    class DummyThread:
        def __init__(self, target, args): pass
        def start(self): pass

    monkeypatch.setattr(threading, 'Thread', DummyThread)
    # stub client
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.get_http_client',
        lambda: DummyClient(),
    )
    dm = DownloadManager()
    tid = dm.start('u', 'p', progress_cb=None)
    assert isinstance(tid, str)
    assert dm.list_active() == {}
    assert dm.cancel('nope') is False
