import os
import sys
import pytest

from scripts.civitai_manager_libs.download.utilities import (
    add_number_to_duplicate_files,
    get_save_base_name,
    download_preview_image,
    _is_lora_model,
    _create_shortcut_for_downloaded_model,
)


def test_add_number_to_duplicate_files():
    files = ['1:foo.txt', '2:foo.txt', '3:bar.jpg', 'nope']
    result = add_number_to_duplicate_files(files)
    # keys should be '1' and '3'
    assert '1' in result and '3' in result
    # duplicate name suffix
    assert result['1'] == 'foo.txt'
    # second foo should be ignored (key 2 skipped)


def test_get_save_base_name_primary(monkeypatch):
    vi = {'foo': 1}
    monkeypatch.setattr('scripts.civitai_manager_libs.download.utilities.civitai',
                        type('M', (), {'get_primary_file_by_version_info': lambda v: [{'name': 'a.bin'}]}))
    name = get_save_base_name(vi)
    assert name == 'a'


def test_get_save_base_name_fallback(monkeypatch):
    vi = {'model': {'name': 'mod'}, 'name': 'ver', 'id': 10}
    fake = type('S', (), {'generate_version_foldername': lambda m, n, i: 'gen'})
    monkeypatch.setattr('scripts.civitai_manager_libs.download.utilities.settings', fake)
    monkeypatch.setattr('scripts.civitai_manager_libs.download.utilities.civitai',
                        type('M', (), {'get_primary_file_by_version_info': lambda v: None}))
    name = get_save_base_name(vi)
    assert name == 'gen'


def test_download_preview_image(monkeypatch, tmp_path):
    # empty vi
    assert not download_preview_image(str(tmp_path / 'p'), {})
    # no images
    assert not download_preview_image(str(tmp_path / 'p'), {'images': []})
    # no url
    assert not download_preview_image(str(tmp_path / 'p'), {'images': [{}]})
    # with width
    vi = {'images': [{'url': 'u', 'width': 100}]}
    # patch change_width and client
    monkeypatch.setattr('scripts.civitai_manager_libs.download.utilities.util',
                        type('U', (), {'change_width_from_image_url': lambda u, w: u + f'?w={w}'}))
    class Client:
        def download_file_with_resume(self, url, path, headers=None):
            return True
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.utilities.get_http_client',
        lambda: Client(),
        raising=False,
    )
    # patch config_manager.get_setting
    from scripts.civitai_manager_libs.download import utilities as util_mod
    monkeypatch.setattr('scripts.civitai_manager_libs.download.utilities.config_manager',
                        type('C', (), {'get_setting': lambda k: 'k'}))
    ok = download_preview_image(str(tmp_path / 'p'), vi)
    assert ok


def test_is_lora_model():
    assert not _is_lora_model({})
    assert _is_lora_model({'model': {'type': 'LoRA'}})
    assert _is_lora_model({'model': {'type': 'lycoris'}})
    assert not _is_lora_model({'model': {'type': 'other'}})


def test_create_shortcut_for_downloaded_model(monkeypatch, tmp_path, caplog):
    folder = tmp_path / 'f'
    folder.mkdir()
    # no preview and no images
    vi = {'images': []}
    out = _create_shortcut_for_downloaded_model(vi, 'name', str(folder), 'id')
    assert out is False
    # with preview file and successful thumbnail
    # create preview file
    fname = 'name_preview.png'
    pre = folder / fname
    pre.write_text('x')
    class ImgProc:
        def create_thumbnail(self, mid, path): return True
    monkeypatch.setattr('scripts.civitai_manager_libs.download.utilities.util',
                        type('U2', (), {'replace_filename': lambda s: s}))
    monkeypatch.setattr('scripts.civitai_manager_libs.download.utilities.settings',
                        type('S2', (), {'PREVIEW_IMAGE_SUFFIX': '_preview', 'PREVIEW_IMAGE_EXT': '.png'}))
    monkeypatch.setitem(sys.modules, 'scripts.civitai_manager_libs.ishortcut_core.image_processor',
                      type('M2', (), {'ImageProcessor': lambda: ImgProc()}))
    out2 = _create_shortcut_for_downloaded_model(vi, 'name', str(folder), 'id')
    assert out2 is True
