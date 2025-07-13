import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.getcwd())

import pytest

from scripts.civitai_manager_libs.download import (
    add_number_to_duplicate_files,
    download_file,
    download_file_gr,
)

from scripts.civitai_manager_libs import settings

config_manager = settings.config_manager


def test_add_number_to_duplicate_files_basic():
    files = ["1:file.txt", "2:file.txt", "3:other.txt"]
    mapping = add_number_to_duplicate_files(files)
    # Same base name should get a counter suffix
    assert mapping["1"] == "file.txt"
    assert mapping["2"].startswith("file (1)")
    # Unique names unchanged
    assert mapping["3"] == "other.txt"


@pytest.mark.parametrize(
    "files, expected",
    [
        ([], {}),
        (["a.txt"], {}),  # no colon entries
        (["1:img.png", "1:img.png", "2:img.png"], {"1": "img.png", "2": "img (1).png"}),
    ],
)
def test_add_number_parametrized(files, expected):
    result = add_number_to_duplicate_files(files)
    assert result == expected


def test_download_file_uses_http_client(monkeypatch):
    calls = []

    class DummyDownloader:
        def download_file(self, url, file_path):
            calls.append((url, file_path))
            return True

    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.get_http_client',
        lambda: DummyDownloader(),
    )
    assert download_file('http://test', 'path/to/file') is True
    assert calls == [('http://test', 'path/to/file')]


def test_download_file_gr_uses_http_client(monkeypatch):
    calls = []
    progress_calls = []

    class DummyClient:
        def download_file(self, url, file_path, progress_callback=None):
            calls.append((url, file_path))
            if progress_callback:
                # Simulate partial progress: downloaded=1, total=2
                progress_callback(1, 2)
            return True

    # Monkey-patch HTTP client factory for downloader
    monkeypatch.setattr(
        'scripts.civitai_manager_libs.download.task_manager.get_http_client', lambda: DummyClient()
    )

    # Use a callback function to capture progress updates
    def progress_callback(fraction, status_message):
        progress_calls.append((fraction, status_message))

    # Execute and verify
    assert download_file_gr('http://test', 'path/to/file', progress_callback) is True
    assert calls == [('http://test', 'path/to/file')]
    # Fraction should reflect downloaded/total = 1/2
    assert progress_calls and progress_calls[-1][0] == 0.5


def test_create_shortcut_for_downloaded_model_with_preview(monkeypatch, tmp_path):
    """Test thumbnail creation from existing preview image."""

    # Mock the entire ImageProcessor import and class
    thumbnail_created = []

    class MockImageProcessor:
        def __init__(self, thumbnail_folder=None):
            pass

        def create_thumbnail(self, model_id, preview_path):
            thumbnail_created.append((model_id, preview_path))
            return True

        def download_thumbnail_image(self, model_id, url):
            return False  # Should not be called when preview exists

    # Mock the entire image_processor module
    import sys

    mock_module = type(sys)('mock_image_processor')
    mock_module.ImageProcessor = MockImageProcessor
    sys.modules['scripts.civitai_manager_libs.ishortcut_core.image_processor'] = mock_module

    try:
        from scripts.civitai_manager_libs.download.utilities import (
            _create_shortcut_for_downloaded_model,
        )

        # Create mock preview file (based on model_filename without extension)
        model_folder = tmp_path / "models"
        model_folder.mkdir()
        preview_file = model_folder / "test_model.safetensors.preview.png"
        preview_file.write_text("fake image")

        # Mock version info
        version_info = {"modelId": "12345", "images": [{"url": "http://example.com/image.jpg"}]}

        # Execute
        result = _create_shortcut_for_downloaded_model(
            version_info, "test_model.safetensors", str(model_folder), "12345"
        )

        # Verify
        assert result is True
        assert len(thumbnail_created) == 1
        assert thumbnail_created[0][0] == "12345"
        assert thumbnail_created[0][1] == str(preview_file)
    finally:
        # Cleanup
        if 'scripts.civitai_manager_libs.ishortcut_core.image_processor' in sys.modules:
            del sys.modules['scripts.civitai_manager_libs.ishortcut_core.image_processor']


def test_create_shortcut_for_downloaded_model_download_thumbnail(monkeypatch, tmp_path):
    """Test thumbnail download when no preview image exists."""

    # Mock ImageProcessor
    calls = []

    class MockImageProcessor:
        def __init__(self, thumbnail_folder=None):
            pass

        def create_thumbnail(self, model_id, preview_path):
            calls.append(("create", model_id, preview_path))
            return False  # Preview doesn't exist

        def download_thumbnail_image(self, model_id, url):
            calls.append(("download", model_id, url))
            return True

    # Mock the entire image_processor module
    import sys

    mock_module = type(sys)('mock_image_processor')
    mock_module.ImageProcessor = MockImageProcessor
    sys.modules['scripts.civitai_manager_libs.ishortcut_core.image_processor'] = mock_module

    try:
        from scripts.civitai_manager_libs.download.utilities import (
            _create_shortcut_for_downloaded_model,
        )

        # Create model folder without preview
        model_folder = tmp_path / "models"
        model_folder.mkdir()

        # Mock version info with image URL
        version_info = {"modelId": "12345", "images": [{"url": "http://example.com/image.jpg"}]}

        # Execute
        result = _create_shortcut_for_downloaded_model(
            version_info, "test_model.safetensors", str(model_folder), "12345"
        )

        # Verify - function should directly try download since no preview exists
        assert result is True
        assert len(calls) == 1  # Only download called since preview doesn't exist
        assert calls[0] == ("download", "12345", "http://example.com/image.jpg")
    finally:
        # Cleanup
        if 'scripts.civitai_manager_libs.ishortcut_core.image_processor' in sys.modules:
            del sys.modules['scripts.civitai_manager_libs.ishortcut_core.image_processor']


def test_create_shortcut_for_downloaded_model_no_images(monkeypatch, tmp_path):
    """Test handling when no images are available."""

    # Mock ImageProcessor
    calls = []

    class MockImageProcessor:
        def __init__(self, thumbnail_folder=None):
            pass

        def create_thumbnail(self, model_id, preview_path):
            calls.append(("create", model_id, preview_path))
            return False

        def download_thumbnail_image(self, model_id, url):
            calls.append(("download", model_id, url))
            return False

    # Mock the entire image_processor module
    import sys

    mock_module = type(sys)('mock_image_processor')
    mock_module.ImageProcessor = MockImageProcessor
    sys.modules['scripts.civitai_manager_libs.ishortcut_core.image_processor'] = mock_module

    try:
        from scripts.civitai_manager_libs.download.utilities import (
            _create_shortcut_for_downloaded_model,
        )

        # Create model folder without preview
        model_folder = tmp_path / "models"
        model_folder.mkdir()

        # Mock version info without images
        version_info = {"modelId": "12345", "images": []}

        # Execute
        result = _create_shortcut_for_downloaded_model(
            version_info, "test_model.safetensors", str(model_folder), "12345"
        )

        # Verify - should return False when no thumbnail can be created
        assert result is False
        # No calls should be made since there are no images and no preview
        assert len(calls) == 0
    finally:
        # Cleanup
        if 'scripts.civitai_manager_libs.ishortcut_core.image_processor' in sys.modules:
            del sys.modules['scripts.civitai_manager_libs.ishortcut_core.image_processor']
