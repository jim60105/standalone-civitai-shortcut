# type: ignore
"""
Test cases for evt.value list handling fix.

This module tests the fix for handling evt.value when it can be either
a string or a list [image_url, shortcut_name] in various gallery select
functions.
"""

from unittest.mock import patch
from types import SimpleNamespace

# Import functions to test
from scripts.civitai_manager_libs import classification_action
from scripts.civitai_manager_libs import recipe, classification
from scripts.civitai_manager_libs.recipe_actions.recipe_reference import RecipeReferenceManager
from scripts.civitai_manager_libs.recipe_actions.recipe_gallery import RecipeGallery

# Create instances for testing
_recipe_reference_manager = RecipeReferenceManager()
_recipe_gallery = RecipeGallery()


class TestEvtValueListHandling:
    """Test proper handling of evt.value in gallery select functions."""

    def test_recipe_get_recipe_with_list_input(self):
        """Test that get_recipe handles list input gracefully."""
        result = recipe.get_recipe(['image_url', 'recipe_name'])
        assert result is None

    def test_recipe_get_recipe_shortcuts_with_list_input(self):
        """Test that get_recipe_shortcuts handles list input gracefully."""
        result = recipe.get_recipe_shortcuts(['image_url', 'recipe_name'])
        assert result is None

    def test_classification_get_classification_info_with_list_input(self):
        """Test that get_classification_info handles list input gracefully."""
        result = classification.get_classification_info(['image_url', 'classification_name'])
        assert result is None

    def test_classification_get_classification_shortcuts_with_list_input(self):
        """Test that get_classification_shortcuts handles list input gracefully."""
        result = classification.get_classification_shortcuts(['image_url', 'classification_name'])
        assert result is None

    def test_on_recipe_gallery_select_with_string(self):
        """Test on_recipe_gallery_select with string evt.value."""
        # Mock evt object with string value
        evt = SimpleNamespace()
        evt.value = 'test_recipe'

        mock_path = (
            'scripts.civitai_manager_libs.recipe_actions.recipe_utilities.'
            'RecipeUtilities.get_recipe_information'
        )
        with patch(mock_path) as mock_get_info:
            mock_get_info.return_value = ("desc", "prompt", "neg", "opts", "gen", "class", None)

            with patch(
                'scripts.civitai_manager_libs.recipe.get_recipe_shortcuts'
            ) as mock_get_shortcuts:
                mock_get_shortcuts.return_value = []

                result = _recipe_gallery.on_recipe_gallery_select(evt)

                # Should call get_recipe_information with the string value
                mock_get_info.assert_called_once_with('test_recipe')
                assert result is not None

    def test_on_recipe_gallery_select_with_list(self):
        """Test on_recipe_gallery_select with list evt.value."""
        # Mock evt object with list value
        evt = SimpleNamespace()
        evt.value = ['image_url', 'test_recipe']

        mock_path = (
            'scripts.civitai_manager_libs.recipe_actions.recipe_utilities.'
            'RecipeUtilities.get_recipe_information'
        )
        with patch(mock_path) as mock_get_info:
            mock_get_info.return_value = ("desc", "prompt", "neg", "opts", "gen", "class", None)

            with patch(
                'scripts.civitai_manager_libs.recipe.get_recipe_shortcuts'
            ) as mock_get_shortcuts:
                mock_get_shortcuts.return_value = []

                result = _recipe_gallery.on_recipe_gallery_select(evt)

                # Should call get_recipe_information with the second element of the list
                mock_get_info.assert_called_once_with('test_recipe')
                assert result is not None

    def test_on_recipe_gallery_select_with_invalid_input(self):
        """Test on_recipe_gallery_select with invalid evt.value."""
        # Mock evt object with invalid value
        evt = SimpleNamespace()
        evt.value = {'invalid': 'type'}

        result = _recipe_gallery.on_recipe_gallery_select(evt)

        # Should return tuple with gr.update() objects
        assert result is not None
        assert len(result) == 16  # Should return 16 values to match UI binding
        # Check that first few values are gr.update objects with empty values
        assert hasattr(result[0], '__getitem__') and result[0].get('value') == ""
        assert hasattr(result[1], '__getitem__') and result[1].get('value') == ""

    def test_on_classification_list_select_with_string(self):
        """Test on_classification_list_select with string evt.value."""
        # Mock evt object with string value
        evt = SimpleNamespace()
        evt.value = 'test_classification'

        mock_path1 = 'scripts.civitai_manager_libs.classification.get_classification_info'
        with patch(mock_path1) as mock_get_info:
            mock_get_info.return_value = "Test info"

            mock_path2 = 'scripts.civitai_manager_libs.classification.get_classification_shortcuts'
            with patch(mock_path2) as mock_get_shortcuts:
                mock_get_shortcuts.return_value = []

                result = classification_action.on_classification_list_select(evt)

                # Should call functions with the string value
                mock_get_info.assert_called_once_with('test_classification')
                mock_get_shortcuts.assert_called_once_with('test_classification')
                assert result is not None

    def test_on_classification_list_select_with_list(self):
        """Test on_classification_list_select with list evt.value."""
        # Mock evt object with list value
        evt = SimpleNamespace()
        evt.value = ['image_url', 'test_classification']

        mock_path1 = 'scripts.civitai_manager_libs.classification.get_classification_info'
        with patch(mock_path1) as mock_get_info:
            mock_get_info.return_value = "Test info"

            mock_path2 = 'scripts.civitai_manager_libs.classification.get_classification_shortcuts'
            with patch(mock_path2) as mock_get_shortcuts:
                mock_get_shortcuts.return_value = []

                result = classification_action.on_classification_list_select(evt)

                # Should call functions with the second element of the list
                mock_get_info.assert_called_once_with('test_classification')
                mock_get_shortcuts.assert_called_once_with('test_classification')
                assert result is not None

    def test_on_classification_list_select_with_invalid_input(self):
        """Test on_classification_list_select with invalid evt.value."""
        # Mock evt object with invalid value
        evt = SimpleNamespace()
        evt.value = 123  # Invalid type

        result = classification_action.on_classification_list_select(evt)  # type: ignore

        # Should return empty updates
        assert result is not None
        # Check that it's a tuple with the expected structure
        assert len(result) == 5

    def test_edge_case_empty_list(self):
        """Test handling of empty list."""
        evt = SimpleNamespace()
        evt.value = []

        result = _recipe_gallery.on_recipe_gallery_select(evt)
        # Should return tuple with gr.update() objects
        assert result is not None
        assert len(result) == 16  # Should return 16 values to match UI binding
        # Check that first few values are gr.update objects with empty values
        assert hasattr(result[0], '__getitem__') and result[0].get('value') == ""

    def test_edge_case_single_element_list(self):
        """Test handling of single element list."""
        evt = SimpleNamespace()
        evt.value = ['only_one_element']

        result = _recipe_gallery.on_recipe_gallery_select(evt)
        # Should return tuple with gr.update() objects
        assert result is not None
        assert len(result) == 16  # Should return 16 values to match UI binding
        # Check that first few values are gr.update objects with empty values
        assert hasattr(result[0], '__getitem__') and result[0].get('value') == ""

    def test_recipe_functions_with_valid_string(self):
        """Test that recipe functions work correctly with valid string input."""
        # These functions should work normally with string input
        result = recipe.get_recipe("valid_string")
        # Function should return None for non-existent recipe, not crash
        assert result is None

        result = recipe.get_recipe_shortcuts("valid_string")
        assert result is None

    def test_classification_functions_with_valid_string(self):
        """Test that classification functions work correctly with valid string input."""
        # These functions should work normally with string input
        result = classification.get_classification_info("valid_string")
        # Function should return None for non-existent classification, not crash
        assert result is None

        result = classification.get_classification_shortcuts("valid_string")
        assert result is None
