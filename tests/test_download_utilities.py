import os

import pytest

from scripts.civitai_manager_libs.download.utilities import (
    add_number_to_duplicate_files,
    get_save_base_name,
    download_preview_image,
    _is_lora_model,
    download_file_thread_async,
)


def test_add_number_to_duplicate_files():
    files = ['1:foo.txt', '2:foo.txt', 'bad', '3:bar.txt', '4:foo.txt']
    res = add_number_to_duplicate_files(files)
    assert res['1'] == 'foo.txt'
    assert res['2'] == 'foo (1).txt'
    assert res['4'] == 'foo (2).txt'
    assert res['3'] == 'bar.txt'


def test_get_save_base_name(monkeypatch):
    vi = {'model': {'name': 'm'}, 'name': 'v', 'id': 123}
    # primary as dict
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.civitai.get_primary_file_by_version_info',
        lambda x: {'name': 'file.txt'}
    )
    assert get_save_base_name(vi) == 'file'
    # primary as list
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.civitai.get_primary_file_by_version_info',
        lambda x: [{'name': 'f.bin'}]
    )
    assert get_save_base_name(vi) == 'f'
    # no primary
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.civitai.get_primary_file_by_version_info',
        lambda x: None
    )
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.settings',
        type('S', (), {'generate_version_foldername': lambda m, n, i: 'gen'})
    )
    assert get_save_base_name(vi) == 'gen'


def test_download_preview_image(monkeypatch, tmp_path):
    fp = str(tmp_path / 'img')
    # empty version_info
    assert download_preview_image(fp, {}) is False
    # no images
    assert download_preview_image(fp, {'images': []}) is False
    # no url
    assert download_preview_image(fp, {'images': [{}]}) is False
    # with width and without width
    vi = {'images': [{'url': 'u', 'width': 100}]}
    # change width
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.util.change_width_from_image_url',
        lambda u, w: u + '?w=' + str(w)
    )
    # config api key
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.config_manager',
        type('C', (), {'get_setting': lambda key: 'key'})
    )
    # http client stub
    class C:
        def download_file_with_resume(self, u, p, headers=None):
            return True

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.get_http_client',
        lambda: C()
    )
    assert download_preview_image(fp, vi) is True


def test_is_lora_model_and_download_file_thread_async(monkeypatch):
    # is_lora_model
    assert not _is_lora_model({})
    assert not _is_lora_model({'model': {}})
    assert _is_lora_model({'model': {'type': 'LORA'}})
    # download_file_thread_async early return
    assert download_file_thread_async('', None, None, None, None, None, None) is None
    # version_info None triggers notify_complete
    class Notifier:
        calls = []

        @staticmethod
        def notify_complete(name, success, msg):
            Notifier.calls.append((name, success, msg))

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.civitai.get_version_info_by_version_id',
        lambda vid: None
    )
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.DownloadNotifier',
        Notifier
    )
    download_file_thread_async('file', 1, None, None, None, None, None)
    assert Notifier.calls and Notifier.calls[0][1] is False
