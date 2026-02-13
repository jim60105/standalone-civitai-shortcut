import os

import pytest

from scripts.civitai_manager_libs import settings
from scripts.civitai_manager_libs.ishortcut_core.image_processor import ImageProcessor


@pytest.fixture(autouse=True)
def patch_exists_and_get(monkeypatch):
    """Patch os.path.exists and settings.get_image_url_to_shortcut_file for testing."""

    def fake_exists(path):
        return False

    monkeypatch.setattr(os.path, "exists", fake_exists)

    def fake_get_image_url_to_shortcut_file(modelid, vid, url):
        return f"/tmp/{modelid}_{vid}.jpg"

    monkeypatch.setattr(
        settings,
        "get_image_url_to_shortcut_file",
        fake_get_image_url_to_shortcut_file,
    )


def test_collect_images_all_static():
    """All static images should be collected when preview_only is False."""
    version_list = [
        [(1, "url1.jpg"), (2, "url2.png"), (3, "url3.webp")],
        [(4, "url4.jpeg"), (5, "url5.avif")],
    ]

    image_processor = ImageProcessor()
    result = image_processor._collect_images_to_download(version_list, modelid="123")
    assert len(result) == 5
    expected = [
        (1, "url1.jpg", "/tmp/123_1.jpg"),
        (2, "url2.png", "/tmp/123_2.jpg"),
        (3, "url3.webp", "/tmp/123_3.jpg"),
        (4, "url4.jpeg", "/tmp/123_4.jpg"),
        (5, "url5.avif", "/tmp/123_5.jpg"),
    ]
    assert result == expected


def test_collect_images_preview_only():
    """Only the first static image per version when preview_only is True."""
    version_list = [
        [(1, "url1.jpg"), (2, "url2.png"), (3, "url3.webp")],
        [(4, "url4.jpeg"), (5, "url5.avif")],
    ]

    image_processor = ImageProcessor()
    result = image_processor._collect_images_to_download(
        version_list, modelid="123", preview_only=True
    )
    assert len(result) == 2
    expected = [
        (1, "url1.jpg", "/tmp/123_1.jpg"),
        (4, "url4.jpeg", "/tmp/123_4.jpg"),
    ]
    assert result == expected


def test_collect_images_skips_dynamic():
    """Dynamic images should be skipped."""
    version_list = [[(1, "url1.mp4"), (2, "url2.gif"), (3, "url3.png")]]

    image_processor = ImageProcessor()
    result = image_processor._collect_images_to_download(version_list, modelid="abc")
    assert len(result) == 1
    expected = [
        (3, "url3.png", "/tmp/abc_3.jpg"),
    ]
    assert result == expected
