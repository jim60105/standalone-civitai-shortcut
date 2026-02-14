"""Tests for repair_missing_preview_images in scan_action."""

import json

from scripts.civitai_manager_libs.scan_action import repair_missing_preview_images


class FakeProgress:
    """Fake gr.Progress for testing."""

    def tqdm(self, iterable, **kwargs):
        return iterable


def _write_version_info(path, images):
    data = {"id": 1, "modelId": 100, "images": images}
    with open(path, "w") as f:
        json.dump(data, f)


def test_downloads_preview_when_missing(tmp_path, monkeypatch):
    """When preview image is missing, it should be downloaded."""
    info_file = str(tmp_path / "mymodel.civitai.info")
    _write_version_info(
        info_file,
        [{"url": "http://example.com/img.png", "type": "image", "width": 512}],
    )

    monkeypatch.setattr(
        "scripts.civitai_manager_libs.scan_action.model.Downloaded_InfoPath",
        {info_file: "1"},
    )

    downloaded = []

    def fake_download(url, save_path):
        downloaded.append((url, save_path))
        return True

    monkeypatch.setattr(
        "scripts.civitai_manager_libs.scan_action.download_scan_image",
        fake_download,
    )

    repair_missing_preview_images(FakeProgress())

    assert len(downloaded) == 1
    assert downloaded[0][1] == str(tmp_path / "mymodel.preview.png")


def test_skips_valid_preview(tmp_path, monkeypatch):
    """When preview image exists and is valid, it should be skipped."""
    info_file = str(tmp_path / "mymodel.civitai.info")
    _write_version_info(
        info_file,
        [{"url": "http://example.com/img.png", "type": "image", "width": 512}],
    )

    # Create a valid PNG file
    preview_path = str(tmp_path / "mymodel.preview.png")
    with open(preview_path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)

    monkeypatch.setattr(
        "scripts.civitai_manager_libs.scan_action.model.Downloaded_InfoPath",
        {info_file: "1"},
    )

    downloaded = []

    def fake_download(url, save_path):
        downloaded.append((url, save_path))
        return True

    monkeypatch.setattr(
        "scripts.civitai_manager_libs.scan_action.download_scan_image",
        fake_download,
    )

    repair_missing_preview_images(FakeProgress())

    assert len(downloaded) == 0


def test_downloads_when_preview_is_invalid(tmp_path, monkeypatch):
    """When preview image exists but is invalid (e.g. MP4), it should be re-downloaded."""
    info_file = str(tmp_path / "mymodel.civitai.info")
    _write_version_info(
        info_file,
        [{"url": "http://example.com/img.png", "type": "image", "width": 512}],
    )

    # Create an invalid preview file (MP4 magic bytes)
    preview_path = str(tmp_path / "mymodel.preview.png")
    with open(preview_path, "wb") as f:
        f.write(b"\x00\x00\x00\x1cftypisom" + b"\x00" * 100)

    monkeypatch.setattr(
        "scripts.civitai_manager_libs.scan_action.model.Downloaded_InfoPath",
        {info_file: "1"},
    )

    downloaded = []

    def fake_download(url, save_path):
        downloaded.append((url, save_path))
        return True

    monkeypatch.setattr(
        "scripts.civitai_manager_libs.scan_action.download_scan_image",
        fake_download,
    )

    repair_missing_preview_images(FakeProgress())

    assert len(downloaded) == 1


def test_skips_non_static_images_in_version_info(tmp_path, monkeypatch):
    """When version info only has video images, no download should occur."""
    info_file = str(tmp_path / "mymodel.civitai.info")
    _write_version_info(
        info_file,
        [{"url": "http://example.com/vid.mp4", "type": "video"}],
    )

    monkeypatch.setattr(
        "scripts.civitai_manager_libs.scan_action.model.Downloaded_InfoPath",
        {info_file: "1"},
    )

    downloaded = []

    def fake_download(url, save_path):
        downloaded.append((url, save_path))
        return True

    monkeypatch.setattr(
        "scripts.civitai_manager_libs.scan_action.download_scan_image",
        fake_download,
    )

    repair_missing_preview_images(FakeProgress())

    assert len(downloaded) == 0


def test_empty_downloaded_info_path(monkeypatch):
    """When no models are downloaded, nothing should happen."""
    monkeypatch.setattr(
        "scripts.civitai_manager_libs.scan_action.model.Downloaded_InfoPath",
        None,
    )
    # Should not raise
    repair_missing_preview_images(FakeProgress())
