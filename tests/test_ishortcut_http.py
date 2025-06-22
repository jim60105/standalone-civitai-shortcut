import os
import pytest

from scripts.civitai_manager_libs import util
from scripts.civitai_manager_libs.ishortcut import (
    _get_preview_image_url,
    _get_preview_image_path,
    download_model_preview_image_by_model_info,
    get_preview_image_by_model_info,
)


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
        'scripts.civitai_manager_libs.ishortcut._get_preview_image_path',
        lambda m: str(expected_path),
    )
    # Patch download_image_safe
    calls = []
    monkeypatch.setattr(
        util,
        'download_image_safe',
        lambda u, p, c, show_error=False: calls.append((u, p)) or True,
    )
    # Patch get_shortcut_client to avoid real HTTP client
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.ishortcut.get_shortcut_client',
        lambda: None,
    )
    downloaded = download_model_preview_image_by_model_info(info)
    assert downloaded == str(expected_path)
    assert calls and calls[0][0] == url


def test_get_preview_image_by_model_info_existing(tmp_path, monkeypatch):
    info = {"id": "99"}
    fake_path = tmp_path / "model_99_preview.jpg"
    fake_path.write_text("data")
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.ishortcut._get_preview_image_path', lambda m: str(fake_path)
    )
    assert get_preview_image_by_model_info(info) == str(fake_path)


def test_get_preview_image_by_model_info_fallback(monkeypatch):
    info = {"id": "nope"}
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.ishortcut._get_preview_image_path',
        lambda m: None,
    )
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.ishortcut.download_model_preview_image_by_model_info',
        lambda m: None,
    )
    from scripts.civitai_manager_libs.setting import no_card_preview_image

    assert get_preview_image_by_model_info(info) == no_card_preview_image
