import os
import pytest

from scripts.civitai_manager_libs import settings
from scripts.civitai_manager_libs.ishortcut_core.preview_image_manager import (
    PreviewImageManager,
)


@pytest.fixture(autouse=True)
def isolate_preview_dir(tmp_path, monkeypatch):
    # isolate preview directory and fallback image
    pd = tmp_path / 'previews'
    monkeypatch.setattr(settings, 'shortcut_thumbnail_folder', str(pd))
    monkeypatch.setattr(settings, 'get_no_card_preview_image', lambda: 'fallback.jpg')
    return tmp_path


def test_get_preview_image_url():
    mgr = PreviewImageManager(None)
    # empty input
    assert mgr.get_preview_image_url({}) is None
    # modelVersions priority - must have static image type/extension
    model_info = {'modelVersions': [{'images': [{'url': 'http://example.com/img.jpeg'}]}]}
    assert mgr.get_preview_image_url(model_info) == 'http://example.com/img.jpeg'
    # fallback to images
    model_info2 = {'images': [{'url': 'http://example.com/img2.png'}]}
    assert mgr.get_preview_image_url(model_info2) == 'http://example.com/img2.png'
    # video type should be filtered out
    model_info3 = {
        'modelVersions': [
            {
                'images': [
                    {'url': 'http://example.com/vid.mp4', 'type': 'video'},
                    {'url': 'http://example.com/static.jpeg', 'type': 'image'},
                ]
            }
        ]
    }
    assert mgr.get_preview_image_url(model_info3) == 'http://example.com/static.jpeg'


def test_get_preview_image_path(isolate_preview_dir):
    mgr = PreviewImageManager(None)
    mi = {'id': '55'}
    path = mgr.get_preview_image_path(mi)
    assert path.endswith(os.path.join('previews', 'model_55_preview.jpg'))
    assert os.path.isdir(os.path.dirname(path))
    # invalid input
    assert mgr.get_preview_image_path({}) is None


def test_download_and_get_preview(monkeypatch, isolate_preview_dir):
    mgr = PreviewImageManager(None)
    sample = {'modelVersions': [{'images': [{'url': 'zu'}]}], 'images': []}
    # stub HTTP client and download
    monkeypatch.setattr(mgr, 'get_preview_image_url', lambda x: 'http://x')
    monkeypatch.setattr(
        mgr, 'get_preview_image_path', lambda x: str(isolate_preview_dir / 'test.jpg')
    )
    monkeypatch.setenv('HTTP_PROXY', '')
    # simulate existing file
    open(str(isolate_preview_dir / 'test.jpg'), 'w').close()
    assert mgr.download_preview_image(sample) == str(isolate_preview_dir / 'test.jpg')
    # simulate download
    os.remove(str(isolate_preview_dir / 'test.jpg'))
    monkeypatch.setenv('HTTP_PROXY', '')
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.ishortcut_core.preview_image_manager.download_image_safe',
        lambda u, p, c, show_error: True,
    )
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.ishortcut_core.preview_image_manager.get_http_client',
        lambda: None,
    )
    result = mgr.download_preview_image(sample)
    assert result == str(isolate_preview_dir / 'test.jpg')
    # get_preview_image fallback when download fails or file missing
    # ensure no preview file exists
    fpath = str(isolate_preview_dir / 'test.jpg')
    if os.path.exists(fpath):
        os.remove(fpath)
    monkeypatch.setattr(mgr, 'download_preview_image', lambda x: None)
    assert mgr.get_preview_image(sample) == 'fallback.jpg'


def test_cleanup_unused_previews(monkeypatch, isolate_preview_dir):
    # setup collection manager
    tmp = isolate_preview_dir
    # create preview files
    previews = tmp / 'previews'
    previews.mkdir(parents=True, exist_ok=True)
    f1 = previews / 'model_1_preview.jpg'
    f2 = previews / 'model_2_preview.jpg'
    f1.write_text('x')
    f2.write_text('y')
    # stub manager with only model 1
    coll = type('C', (), {'load_shortcuts': lambda self: {'1': {}}})()
    mgr = PreviewImageManager(coll)
    removed = mgr.cleanup_unused_previews()
    assert removed == 1
    assert not f2.exists()
    assert f1.exists()
