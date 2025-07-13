from scripts.civitai_manager_libs.download.notifier import DownloadNotifier
from scripts.civitai_manager_libs import util
import pytest


class DummyService:
    def __init__(self):
        self.info = []
        self.warn = []
        self.err = []
    def show_info(self, msg, duration=None): self.info.append((msg, duration))
    def show_warning(self, msg): self.warn.append(msg)
    def show_error(self, msg, duration=None): self.err.append((msg, duration))


@pytest.fixture(autouse=True)
def patch_notifier(monkeypatch):
    # patch notification service
    # Patch global notification service getter used by notifier
    svc = DummyService()
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.ui.notification_service.get_notification_service',
        lambda: svc,
        raising=False,
    )
    yield svc


def test_notify_start_and_complete_and_progress(patch_notifier, caplog):
    svc = patch_notifier
    # start with size
    DownloadNotifier.notify_start('file.bin', 1024)
    assert svc.info, 'Info start should be called'
    # progress with total
    DownloadNotifier.notify_progress('file.bin', 512, 1024, '1KB/s')
    # progress without total
    DownloadNotifier.notify_progress('file.bin', 256, 0, '')
    # complete success
    DownloadNotifier.notify_complete('file.bin', True)
    assert svc.info[-1][0].startswith('✅ Download completed')
    # complete failure
    DownloadNotifier.notify_complete('file.bin', False, 'err')
    assert svc.err[-1][0].startswith('❌ Download failed')
