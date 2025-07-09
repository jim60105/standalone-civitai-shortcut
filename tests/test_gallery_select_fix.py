"""Test cases for gallery select event handling fix."""

from unittest.mock import Mock, patch

from scripts.civitai_manager_libs import setting
from scripts.civitai_manager_libs.recipe_action import (
    on_reference_sc_gallery_select,
    on_reference_gallery_select,
)
from scripts.civitai_manager_libs.classification_action import (
    on_sc_gallery_select,
    on_classification_gallery_select,
)
from scripts.civitai_manager_libs.recipe_browser_page import (
    on_recipe_reference_select_gallery_select,
    on_recipe_reference_gallery_select,
)


class TestGallerySelectFix:
    """Test cases for gallery select event handling fix."""

    def test_get_modelid_from_shortcutname_with_string(self):
        """Test get_modelid_from_shortcutname with string input."""
        # Test normal case
        result = setting.get_modelid_from_shortcutname("model_name:12345")
        assert result == "12345"

        # Test with empty string
        result = setting.get_modelid_from_shortcutname("")
        assert result is None

        # Test with None
        result = setting.get_modelid_from_shortcutname(None)
        assert result is None

        # Test with no colon
        result = setting.get_modelid_from_shortcutname("model_name")
        assert result is None

    def test_get_modelid_from_shortcutname_with_list(self):
        """Test get_modelid_from_shortcutname with list input (Gradio SelectData format)."""
        # Test normal case with list [image_url, shortcut_name]
        result = setting.get_modelid_from_shortcutname(
            ["http://example.com/image.jpg", "model_name:12345"]
        )
        assert result == "12345"

        # Test with single element list
        result = setting.get_modelid_from_shortcutname(["model_name:12345"])
        assert result == "12345"

        # Test with empty list
        result = setting.get_modelid_from_shortcutname([])
        assert result is None

        # Test with list containing non-string
        result = setting.get_modelid_from_shortcutname([123, 456])
        assert result is None

    def test_get_modelid_from_shortcutname_with_invalid_types(self):
        """Test get_modelid_from_shortcutname with invalid input types."""
        # Test with number
        result = setting.get_modelid_from_shortcutname(12345)
        assert result is None

        # Test with dict
        result = setting.get_modelid_from_shortcutname({"key": "value"})
        assert result is None

    @patch('scripts.civitai_manager_libs.recipe_action.logger')
    def test_on_reference_sc_gallery_select_with_list(self, mock_logger):
        """Test on_reference_sc_gallery_select with list input."""
        # Mock SelectData event
        evt = Mock()
        evt.value = ["http://example.com/image.jpg", "model_name:12345"]

        shortcuts = []
        result_shortcuts, result_time = on_reference_sc_gallery_select(evt, shortcuts)

        assert "12345" in result_shortcuts
        assert len(result_shortcuts) == 1

    @patch('scripts.civitai_manager_libs.recipe_action.logger')
    def test_on_reference_sc_gallery_select_with_string(self, mock_logger):
        """Test on_reference_sc_gallery_select with string input."""
        # Mock SelectData event
        evt = Mock()
        evt.value = "model_name:12345"

        shortcuts = []
        result_shortcuts, result_time = on_reference_sc_gallery_select(evt, shortcuts)

        assert "12345" in result_shortcuts
        assert len(result_shortcuts) == 1

    def test_on_reference_sc_gallery_select_with_invalid_input(self):
        """Test on_reference_sc_gallery_select with invalid input."""
        # Mock SelectData event
        evt = Mock()
        evt.value = 12345  # Invalid input

        shortcuts = []
        result_shortcuts, result_time = on_reference_sc_gallery_select(evt, shortcuts)

        # Should return original shortcuts without modification
        assert result_shortcuts == shortcuts
        assert len(result_shortcuts) == 0
        # Should return a datetime object as second element
        import datetime

        assert isinstance(result_time, datetime.datetime)

    @patch('scripts.civitai_manager_libs.recipe_action.logger')
    def test_on_reference_gallery_select_with_list(self, mock_logger):
        """Test on_reference_gallery_select with list input."""
        # Mock SelectData event
        evt = Mock()
        evt.value = ["http://example.com/image.jpg", "model_name:12345"]

        shortcuts = []
        result = on_reference_gallery_select(evt, shortcuts, delete_opt=False)

        shortcuts_result, visible_result, display_result, model_id = result
        assert model_id == "12345"

    @patch('scripts.civitai_manager_libs.classification_action.logger.warning')
    def test_on_sc_gallery_select_with_list(self, mock_warning):
        """Test on_sc_gallery_select with list input."""
        # Mock SelectData event
        evt = Mock()
        evt.value = ["http://example.com/image.jpg", "model_name:12345"]

        shortcuts = []
        page = 1
        result = on_sc_gallery_select(evt, shortcuts, page)

        # Result should be a 4-tuple when successful
        assert len(result) == 4
        shortcuts_result, page_result, time_result, selected_result = result
        assert "12345" in shortcuts_result
        assert len(shortcuts_result) == 1

    @patch('scripts.civitai_manager_libs.classification_action.logger.warning')
    def test_on_classification_gallery_select_with_list(self, mock_warning):
        """Test on_classification_gallery_select with list input."""
        # Mock SelectData event
        evt = Mock()
        evt.value = ["http://example.com/image.jpg", "model_name:12345"]

        shortcuts = []
        result = on_classification_gallery_select(evt, shortcuts, delete_opt=False)

        shortcuts_result, visible_result1, visible_result2, model_id = result
        assert model_id == "12345"

    @patch('scripts.civitai_manager_libs.recipe_browser_page.logger.warning')
    def test_on_recipe_reference_select_gallery_select_with_list(self, mock_warning):
        """Test on_recipe_reference_select_gallery_select with list input."""
        # Mock SelectData event
        evt = Mock()
        evt.value = ["http://example.com/image.jpg", "model_name:12345"]

        shortcuts = ["12345"]  # Model already in shortcuts
        result = on_recipe_reference_select_gallery_select(evt, shortcuts)

        shortcuts_result, none_result, time_result = result
        # Should be removed from shortcuts
        assert "12345" not in shortcuts_result

    @patch('scripts.civitai_manager_libs.recipe_browser_page.logger.warning')
    def test_on_recipe_reference_gallery_select_with_list(self, mock_warning):
        """Test on_recipe_reference_gallery_select with list input."""
        # Mock SelectData event
        evt = Mock()
        evt.value = ["http://example.com/image.jpg", "model_name:12345"]

        shortcuts = []
        result = on_recipe_reference_gallery_select(evt, shortcuts)

        shortcuts_result, time_result = result
        assert "12345" in shortcuts_result
        assert len(shortcuts_result) == 1
