"""Unit tests for model utility functions."""

import os
from unittest.mock import patch

from scripts.civitai_manager_libs.settings import model_utils


class TestModelUtils:
    """Tests for model utility functions."""

    def test_generate_type_basefolder_known_type(self):
        """Test generating base folder for known content type."""
        with patch.object(model_utils, 'model_folders', {'Checkpoint': '/models/checkpoint'}):
            result = model_utils.generate_type_basefolder('Checkpoint')
            assert result == '/models/checkpoint'

    def test_generate_type_basefolder_unknown_type(self):
        """Test generating base folder for unknown content type."""
        with patch.object(model_utils, 'model_folders',
                          {'Unknown': '/models/unknown'}), \
             patch.object(model_utils.util, 'replace_dirname', return_value='test_type'):
            result = model_utils.generate_type_basefolder('TestType')
            assert result == os.path.join('/models/unknown', 'test_type')

    def test_generate_type_basefolder_empty_type(self):
        """Test generating base folder for empty content type."""
        with patch.object(model_utils, 'model_folders', {'Unknown': '/models/unknown'}):
            result = model_utils.generate_type_basefolder('')
            assert result == '/models/unknown'

    def test_generate_type_basefolder_none_type(self):
        """Test generating base folder for None content type."""
        with patch.object(model_utils, 'model_folders', {'Unknown': '/models/unknown'}):
            result = model_utils.generate_type_basefolder(None)
            assert result == '/models/unknown'

    def test_generate_type_basefolder_no_unknown_folder(self):
        """Test generating base folder when Unknown folder is not available."""
        with patch.object(model_utils, 'model_folders', {}):
            result = model_utils.generate_type_basefolder('UnknownType')
            assert result == ''

    def test_generate_version_foldername(self):
        """Test generating version folder name."""
        result = model_utils.generate_version_foldername("TestModel", "v1.0", "12345")
        assert result == "TestModel-v1.0"

    def test_get_ui_typename_found(self):
        """Test getting UI type name for existing type."""
        # Mock UI_TYPENAMES to have a known mapping
        with patch.object(model_utils, 'UI_TYPENAMES', {'ui_type': 'model_type'}):
            result = model_utils.get_ui_typename('model_type')
            assert result == 'ui_type'

    def test_get_ui_typename_not_found(self):
        """Test getting UI type name for non-existent type."""
        with patch.object(model_utils, 'UI_TYPENAMES', {}):
            result = model_utils.get_ui_typename('unknown_type')
            assert result == 'unknown_type'

    def test_get_imagefn_and_shortcutid_from_recipe_image_valid(self):
        """Test extracting image filename and shortcut ID from valid recipe image."""
        result = model_utils.get_imagefn_and_shortcutid_from_recipe_image("123:image.jpg")
        # Function returns a list, not tuple
        assert result == ["123", "image.jpg"]

    def test_get_imagefn_and_shortcutid_from_recipe_image_no_colon(self):
        """Test extracting from recipe image without colon."""
        result = model_utils.get_imagefn_and_shortcutid_from_recipe_image("image.jpg")
        assert result == (None, None)

    def test_get_imagefn_and_shortcutid_from_recipe_image_empty(self):
        """Test extracting from empty recipe image."""
        result = model_utils.get_imagefn_and_shortcutid_from_recipe_image("")
        assert result == (None, None)

    def test_get_imagefn_and_shortcutid_from_recipe_image_none(self):
        """Test extracting from None recipe image."""
        result = model_utils.get_imagefn_and_shortcutid_from_recipe_image(None)
        assert result == (None, None)

    def test_set_imagefn_and_shortcutid_for_recipe_image_valid(self):
        """Test constructing recipe image from valid inputs."""
        result = model_utils.set_imagefn_and_shortcutid_for_recipe_image("123", "image.jpg")
        assert result == "123:image.jpg"

    def test_set_imagefn_and_shortcutid_for_recipe_image_missing_id(self):
        """Test constructing recipe image with missing shortcut ID."""
        result = model_utils.set_imagefn_and_shortcutid_for_recipe_image(None, "image.jpg")
        assert result is None

    def test_set_imagefn_and_shortcutid_for_recipe_image_missing_filename(self):
        """Test constructing recipe image with missing filename."""
        result = model_utils.set_imagefn_and_shortcutid_for_recipe_image("123", None)
        assert result is None

    def test_get_modelid_from_shortcutname_string_with_colon(self):
        """Test extracting model ID from string with colon."""
        result = model_utils.get_modelid_from_shortcutname("ModelName:12345")
        assert result == "12345"

    def test_get_modelid_from_shortcutname_string_without_colon(self):
        """Test extracting model ID from string without colon."""
        result = model_utils.get_modelid_from_shortcutname("ModelName")
        assert result is None

    def test_get_modelid_from_shortcutname_dict_with_caption(self):
        """Test extracting model ID from dict with caption."""
        result = model_utils.get_modelid_from_shortcutname({"caption": "ModelName:12345"})
        assert result == "12345"

    def test_get_modelid_from_shortcutname_list_multiple_items(self):
        """Test extracting model ID from list with multiple items."""
        result = model_utils.get_modelid_from_shortcutname(["first", "ModelName:12345"])
        assert result == "12345"

    def test_get_modelid_from_shortcutname_list_single_item(self):
        """Test extracting model ID from list with single item."""
        result = model_utils.get_modelid_from_shortcutname(["ModelName:12345"])
        assert result == "12345"

    def test_get_modelid_from_shortcutname_empty_list(self):
        """Test extracting model ID from empty list."""
        result = model_utils.get_modelid_from_shortcutname([])
        assert result is None

    def test_get_modelid_from_shortcutname_none(self):
        """Test extracting model ID from None."""
        result = model_utils.get_modelid_from_shortcutname(None)
        assert result is None

    def test_set_shortcutname_valid(self):
        """Test constructing shortcut name from valid inputs."""
        result = model_utils.set_shortcutname("ModelName", "12345")
        assert result == "ModelName:12345"

    def test_set_shortcutname_missing_name(self):
        """Test constructing shortcut name with missing model name."""
        result = model_utils.set_shortcutname(None, "12345")
        assert result is None

    def test_set_shortcutname_missing_id(self):
        """Test constructing shortcut name with missing model ID."""
        result = model_utils.set_shortcutname("ModelName", None)
        assert result is None
