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


def test_collect_images_no_limit():
    """When shortcut_max_download_image_per_version is 0, all images should be collected."""
    version_list = [
        [(1, "url1"), (2, "url2"), (3, "url3")],
        [(4, "url4"), (5, "url5")],
    ]
    settings.config_manager.set_setting('shortcut_max_download_image_per_version', 0)

    # Use ImageProcessor instead of the moved private function
    image_processor = ImageProcessor()
    result = image_processor._collect_images_to_download(version_list, modelid="123")
    assert len(result) == 5
    expected = [
        (1, "url1", "/tmp/123_1.jpg"),
        (2, "url2", "/tmp/123_2.jpg"),
        (3, "url3", "/tmp/123_3.jpg"),
        (4, "url4", "/tmp/123_4.jpg"),
        (5, "url5", "/tmp/123_5.jpg"),
    ]
    assert result == expected


def test_collect_images_with_limit():
    """
    When shortcut_max_download_image_per_version > 0,
    only up to the limit are collected per version.
    """
    version_list = [[(1, "url1"), (2, "url2"), (3, "url3")]]
    settings.config_manager.set_setting('shortcut_max_download_image_per_version', 2)

    # Use ImageProcessor instead of the moved private function
    image_processor = ImageProcessor()
    result = image_processor._collect_images_to_download(version_list, modelid="abc")
    assert len(result) == 2
    expected = [
        (1, "url1", "/tmp/abc_1.jpg"),
        (2, "url2", "/tmp/abc_2.jpg"),
    ]
    assert result == expected
