from unittest.mock import patch

from scripts.civitai_manager_libs import setting
from scripts.civitai_manager_libs.recipe_actions.recipe_management import RecipeManager

# Create instance for testing
_recipe_manager = RecipeManager()


class TestRecipeNameValidation:
    """Test suite for recipe name validation in recipe_action module."""

    @patch("gradio.Warning")
    def test_empty_recipe_name_shows_warning(self, mock_warning):
        """Test warning is shown when recipe name is empty."""
        result = _recipe_manager.on_recipe_create_btn_click(
            recipe_name="",
            recipe_desc="Test description",
            recipe_prompt="Test prompt",
            recipe_negative="",
            recipe_option="",
            recipe_classification=setting.PLACEHOLDER,
        )
        mock_warning.assert_called_once_with("Please enter a recipe name before creating.")
        assert isinstance(result, tuple)

    @patch("gradio.Warning")
    def test_whitespace_only_name_shows_warning(self, mock_warning):
        """Test warning is shown when name contains only whitespace."""
        result = _recipe_manager.on_recipe_create_btn_click(
            recipe_name="   \t\n   ",
            recipe_desc="Test description",
            recipe_prompt="Test prompt",
            recipe_negative="",
            recipe_option="",
            recipe_classification=setting.PLACEHOLDER,
        )
        mock_warning.assert_called_once_with("Please enter a recipe name before creating.")
        assert isinstance(result, tuple)

    @patch("gradio.Warning")
    def test_default_name_shows_warning(self, mock_warning):
        """Test warning is shown when using default recipe name."""
        result = _recipe_manager.on_recipe_create_btn_click(
            recipe_name=setting.NEWRECIPE,
            recipe_desc="Test description",
            recipe_prompt="Test prompt",
            recipe_negative="",
            recipe_option="",
            recipe_classification=setting.PLACEHOLDER,
        )
        mock_warning.assert_called_once_with("Please enter a recipe name before creating.")
        assert isinstance(result, tuple)

    @patch("scripts.civitai_manager_libs.recipe.create_recipe", return_value=True)
    def test_valid_name_creates_recipe(self, mock_create):
        """Test successful creation with valid recipe name."""
        result = _recipe_manager.on_recipe_create_btn_click(
            recipe_name="Valid Recipe Name",
            recipe_desc="Test description",
            recipe_prompt="Test prompt",
            recipe_negative="",
            recipe_option="",
            recipe_classification=setting.PLACEHOLDER,
        )
        mock_create.assert_called_once()
        assert isinstance(result, tuple)
