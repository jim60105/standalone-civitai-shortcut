"""Unit tests for download utilities: file naming, preview image, and async download logic."""
import os

import pytest

import scripts.civitai_manager_libs.download.utilities as util_mod
from scripts.civitai_manager_libs.settings import config_manager


def test_add_number_to_duplicate_files():
    entries = ['1:foo.txt', '2:foo.txt', '1:bar.txt']
    result = util_mod.add_number_to_duplicate_files(entries)
    # First entry key '1' gets 'foo.txt', next '2' gets numbered duplicate
    assert result['1'] == 'foo.txt'
    assert result['2'] == 'foo (1).txt'


def test_get_save_base_name_with_primary(monkeypatch):
    # Primary as dict
    vi = {'files': [], 'images': [], 'model': {}, 'name': 'v', 'id': 9}
    monkeypatch.setattr(util_mod.civitai, 'get_primary_file_by_version_info',
                        lambda x: {'name': 'myfile.bin'})
    name = util_mod.get_save_base_name(vi)
    assert name == 'myfile'
    # Primary as list
    monkeypatch.setattr(util_mod.civitai, 'get_primary_file_by_version_info',
                        lambda x: [{'name': 'other.txt'}])
    name2 = util_mod.get_save_base_name(vi)
    assert name2 == 'other'


def test_get_save_base_name_fallback(monkeypatch):
    # No primary available, fallback to version folder naming
    vi = {'model': {'name': 'Mod'}, 'name': 'Ver', 'id': 7}
    monkeypatch.setattr(util_mod.civitai, 'get_primary_file_by_version_info', lambda x: None)
    # generate_version_foldername returns 'Mod-Ver'
    name = util_mod.get_save_base_name(vi)
    assert name == 'Mod-Ver'


def test_download_preview_image_branches(monkeypatch, tmp_path):
    # No version_info => False
    assert util_mod.download_preview_image(str(tmp_path / 'a.png'), {}) is False
    # No images => False
    assert util_mod.download_preview_image(str(tmp_path / 'a.png'), {'images': []}) is False
    # No url => False
    assert util_mod.download_preview_image(str(tmp_path / 'a.png'), {'images': [{}]}) is False

    # Successful branch with width adjustment
    vi = {'images': [{'url': 'u.jpg', 'width': 123}]}
    # Patch util change_width and HTTP client method
    monkeypatch.setattr(util_mod.util, 'change_width_from_image_url', lambda url, w: f'{url}?w={w}')
    class DummyClient:
        def download_file_with_resume(self, u, fpath, headers=None):
            return True
    monkeypatch.setattr(util_mod, 'get_http_client', lambda: DummyClient())
    monkeypatch.setattr(config_manager, 'get_setting', lambda key: 'KEY')
    ok = util_mod.download_preview_image(str(tmp_path / 'b.png'), vi)
    assert ok is True


class DummyNotifier:
    starts = []
    completes = []

    @staticmethod
    def notify_start(name, size):
        DummyNotifier.starts.append((name, size))

    @staticmethod
    def notify_complete(name, success, msg=None):
        DummyNotifier.completes.append((name, success, msg))


class DummyDownloadManager:
    def __init__(self):
        self.tasks = []
    def start(self, url, path):
        self.tasks.append((url, path))
        return 'task1'


def test_download_file_thread_async_missing_inputs(monkeypatch):
    """No notifications when file_name or version_id missing."""
    monkeypatch.setattr(util_mod, 'DownloadNotifier', DummyNotifier)
    DummyNotifier.starts.clear(); DummyNotifier.completes.clear()
    util_mod.download_file_thread_async([], None, None, None, None, None, None)
    assert not DummyNotifier.starts and not DummyNotifier.completes


def test_download_file_thread_async_no_version(monkeypatch, tmp_path):
    """Notify failure when version info cannot be retrieved."""
    monkeypatch.setattr(util_mod, 'DownloadNotifier', DummyNotifier)
    DummyNotifier.completes.clear()
    monkeypatch.setattr(util_mod.civitai, 'get_version_info_by_version_id', lambda vid: None)
    util_mod.download_file_thread_async('1:fn', 'vid', None, None, None, None, None)
    assert DummyNotifier.completes[-1] == ('1:fn', False, 'Failed to get version info')


def test_download_file_thread_async_no_folder(monkeypatch, tmp_path):
    """Notify failure when download folder cannot be created."""
    monkeypatch.setattr(util_mod, 'DownloadNotifier', DummyNotifier)
    DummyNotifier.completes.clear()
    vi = {'files': [], 'model': {}, 'id': 1}
    monkeypatch.setattr(util_mod.civitai, 'get_version_info_by_version_id', lambda vid: vi)
    monkeypatch.setattr(util_mod.civitai, 'get_files_by_version_info', lambda x: {})
    monkeypatch.setattr(util_mod.util, 'make_download_model_folder', lambda *args: None)
    util_mod.download_file_thread_async('1:fn', 'vid', 'ms', 'vs', 'vsn', 'csn', 'msn')
    assert DummyNotifier.completes[-1] == ('1:fn', False, 'Failed to create download folder')


def test_download_file_thread_async_full_flow(monkeypatch, tmp_path):
    """Full download flow: start notifications and tasks for primary files."""
    monkeypatch.setattr(util_mod, 'DownloadNotifier', DummyNotifier)
    vi2 = {'files': [{'id': 1, 'primary': True}],
           'model': {'type': 'LORA', 'name': 'M', 'modelId': 100},
           'images': [{'url': 'u'}], 'id': 5}
    files_map = {'1': {'downloadUrl': 'url1'}}
    monkeypatch.setattr(util_mod.civitai, 'get_version_info_by_version_id', lambda vid: vi2)
    monkeypatch.setattr(util_mod.civitai, 'get_files_by_version_info', lambda x: files_map)
    folder = str(tmp_path / 'fld')
    monkeypatch.setattr(util_mod.util, 'make_download_model_folder', lambda *args: folder)
    monkeypatch.setattr(util_mod, '_is_lora_model', lambda info: True)
    monkeypatch.setattr(util_mod.civitai, 'write_version_info', lambda path, info: True)
    monkeypatch.setattr(util_mod, 'download_preview_image', lambda path, info: True)
    monkeypatch.setattr(util_mod.civitai, 'write_LoRa_metadata', lambda path, info: True)
    monkeypatch.setattr(util_mod, '_create_shortcut_for_downloaded_model', lambda vi, base, fld, mid: True)
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.DownloadManager',
        DummyDownloadManager,
    )
    DummyNotifier.starts.clear(); DummyNotifier.completes.clear()
    # Pass file_name as list to match intended API usage
    util_mod.download_file_thread_async(['1:file1'], 'vid', 'ms', 'vs', 'vsn', 'csn', 'msn')
    assert DummyNotifier.starts and DummyNotifier.starts[0][0] == 'file1'
