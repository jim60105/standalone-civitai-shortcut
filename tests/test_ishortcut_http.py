import os

from scripts.civitai_manager_libs.ishortcut_core.preview_image_manager import PreviewImageManager

# instantiate PreviewImageManager with a dummy collection_manager for testing
preview_manager = PreviewImageManager(None)

_get_preview_image_url = preview_manager.get_preview_image_url
_get_preview_image_path = preview_manager.get_preview_image_path
download_model_preview_image_by_model_info = preview_manager.download_preview_image
get_preview_image_by_model_info = preview_manager.get_preview_image


def test_get_preview_image_url_from_versions():
    model_info = {"modelVersions": [{"images": [{"url": "http://example.com/v1.jpg"}]}]}
    assert _get_preview_image_url(model_info) == "http://example.com/v1.jpg"


def test_get_preview_image_url_from_images():
    model_info = {"images": [{"url": "http://example.com/img.jpg"}]}
    assert _get_preview_image_url(model_info) == "http://example.com/img.jpg"


def test_get_preview_image_url_none():
    assert _get_preview_image_url({}) is None


def test_get_preview_image_path(tmp_path, monkeypatch):
    monkeypatch.setattr(os, "makedirs", lambda p, exist_ok=True: None)
    info = {"id": 123}
    path = _get_preview_image_path(info)
    assert "model_123_preview.jpg" in path


def test_download_model_preview_image(monkeypatch, tmp_path):
    url = "http://example.com/img.jpg"
    info = {"id": "42", "modelVersions": [{"images": [{"url": url}]}]}
    expected_path = tmp_path / "model_42_preview.jpg"
    # Patch get_preview_image_path to use tmp_path
    monkeypatch.setattr(
        preview_manager,
        'get_preview_image_path',
        lambda m: str(expected_path),
    )
    # Patch download_image_safe in preview_image_manager module
    calls = []
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.ishortcut_core.preview_image_manager.download_image_safe',
        lambda u, p, c, show_error=False: calls.append((u, p)) or True,
    )
    downloaded = download_model_preview_image_by_model_info(info)
    assert downloaded == str(expected_path)
    assert calls and calls[0][0] == url


def test_get_preview_image_by_model_info_existing(tmp_path, monkeypatch):
    info = {"id": "99"}
    fake_path = tmp_path / "model_99_preview.jpg"
    fake_path.write_text("data")
    monkeypatch.setattr(
        preview_manager,
        'get_preview_image_path',
        lambda m: str(fake_path),
    )
    assert get_preview_image_by_model_info(info) == str(fake_path)


def test_get_preview_image_by_model_info_fallback(monkeypatch):
    info = {"id": "nope"}
    monkeypatch.setattr(preview_manager, 'get_preview_image_path', lambda m: None)
    monkeypatch.setattr(preview_manager, 'download_preview_image', lambda m: None)
    from scripts.civitai_manager_libs.setting import no_card_preview_image

    assert get_preview_image_by_model_info(info) == config_manager.get_setting('no_card_preview_image')
