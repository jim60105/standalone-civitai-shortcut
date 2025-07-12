import pytest
from unittest.mock import patch, MagicMock
from scripts.civitai_manager_libs.gallery.gallery_utilities import GalleryUtilities, CompatibilityManager

@pytest.mark.parametrize("url, expected_model_id, expected_version_id", [
    ("https://civitai.com/models/123?modelVersionId=456", "123", "456"),
    ("https://civitai.com/models/123", "123", None),
    ("https://civitai.com/gallery/123", None, None),
    ("https://civitai.com/images?modelId=789", "789", None)
])
def test_extract_model_info(url, expected_model_id, expected_version_id):
    """Test extract_model_info with different URLs."""
    model_id, version_id = GalleryUtilities.extract_model_info(url)
    assert model_id == expected_model_id
    assert version_id == expected_version_id

@pytest.mark.parametrize("url, expected_cursor", [
    ("https://civitai.com/api/v1/images?cursor=12345", 12345),
    ("https://civitai.com/api/v1/images", 0),
])
def test_extract_url_cursor(url, expected_cursor):
    """Test extract_url_cursor with different URLs."""
    cursor = GalleryUtilities.extract_url_cursor(url)
    assert cursor == expected_cursor

def test_build_default_page_url():
    """Test build_default_page_url."""
    url = GalleryUtilities.build_default_page_url("123", "456")
    assert "modelId=123" in url
    assert "modelVersionId=456" in url

@pytest.mark.parametrize("url, use, expected_url", [
    ("https://civitai.com/api/v1/images?cursor=100", True, "https://civitai.com/api/v1/images?cursor=101"),
    ("https://civitai.com/api/v1/images?cursor=100", False, "https://civitai.com/api/v1/images?cursor=100"),
])
def test_fix_page_url_cursor(url, use, expected_url):
    """Test fix_page_url_cursor."""
    with patch('scripts.civitai_manager_libs.gallery.gallery_utilities.util.update_url', return_value=expected_url):
        new_url = GalleryUtilities.fix_page_url_cursor(url, use)
        assert new_url == expected_url

@pytest.mark.parametrize("model_id, expected_result", [
    ("123", True),
    ("abc", False),
    (None, False),
])
def test_validate_model_id(model_id, expected_result):
    """Test validate_model_id."""
    assert GalleryUtilities.validate_model_id(model_id) == expected_result

@pytest.mark.parametrize("url, expected_result", [
    ("https://civitai.com", True),
    ("http://civitai.com", True),
    ("civitai.com", False),
    (None, False),
])
def test_validate_url_format(url, expected_result):
    """Test validate_url_format."""
    assert GalleryUtilities.validate_url_format(url) == expected_result

@pytest.mark.parametrize("filename, expected_filename", [
    ("my:file<name>", "my_file_name_"),
    ("safe_filename", "safe_filename"),
    (None, "unknown"),
])
def test_sanitize_filename(filename, expected_filename):
    """Test sanitize_filename."""
    assert GalleryUtilities.sanitize_filename(filename) == expected_filename

@pytest.mark.parametrize("total_pages, current_page, window_size, expected_range", [
    (10, 5, 5, (3, 7)),
    (10, 1, 5, (1, 5)),
    (10, 10, 5, (6, 10)),
    (3, 2, 5, (1, 3)),
])
def test_calculate_pagination_range(total_pages, current_page, window_size, expected_range):
    """Test calculate_pagination_range."""
    assert GalleryUtilities.calculate_pagination_range(total_pages, current_page, window_size) == expected_range

def test_compatibility_manager():
    """Test CompatibilityManager."""
    manager = CompatibilityManager()
    assert manager.get_compatibility_layer() is None
    assert manager.is_standalone_mode() is False
    assert manager.is_webui_mode() is True

    compat_layer = MagicMock()
    compat_layer.is_standalone_mode.return_value = True
    compat_layer.is_webui_mode.return_value = False
    manager.set_compatibility_layer(compat_layer)
    assert manager.get_compatibility_layer() == compat_layer
    assert manager.is_standalone_mode() is True
    assert manager.is_webui_mode() is False