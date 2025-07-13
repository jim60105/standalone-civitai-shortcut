import pytest

from scripts.civitai_manager_libs.download.notifier import DownloadNotifier


class DummyService:
    def __init__(self):
        self.infos = []
        self.errors = []

    def show_info(self, msg, duration=None):
        self.infos.append((msg, duration))

    def show_error(self, msg, duration=None):
        self.errors.append((msg, duration))


def test_notify_start_and_complete_and_progress(monkeypatch):
    svc = DummyService()
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.notifier.get_notification_service',
        lambda: svc,
    )
    # test start
    DownloadNotifier.notify_start('file.txt', file_size=1024)
    assert svc.infos and 'Starting download' in svc.infos[0][0]
    # test progress with total >0
    DownloadNotifier.notify_progress('file.txt', downloaded=512, total=1024, speed='1 KB/s')
    # test progress with total=0
    DownloadNotifier.notify_progress('file.txt', downloaded=256, total=0)
    # test complete success
    DownloadNotifier.notify_complete('file.txt', success=True)
    assert any('Download completed' in msg for msg, _ in svc.infos)
    # test complete failure
    DownloadNotifier.notify_complete('file.txt', success=False, error_msg='err')
    assert any('Download failed' in msg for msg, _ in svc.errors)
