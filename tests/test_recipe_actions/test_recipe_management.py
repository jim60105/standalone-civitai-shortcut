import pytest
from unittest.mock import patch

from scripts.civitai_manager_libs import settings
from scripts.civitai_manager_libs.recipe_actions.recipe_management import RecipeManager
from scripts.civitai_manager_libs.exceptions import ValidationError, FileOperationError


@pytest.fixture(autouse=True)
def use_tmp_recipe_file(tmp_path, monkeypatch):
    """Redirect recipe storage to a temporary file for tests."""
    tmp_file = tmp_path / "recipes.json"
    tmp_folder = tmp_path / "sc_recipes"
    monkeypatch.setattr(settings, "shortcut_recipe", str(tmp_file))
    monkeypatch.setattr(settings, "shortcut_recipe_folder", str(tmp_folder))
    monkeypatch.setattr(settings, "NEWRECIPE", "New Recipe")
    monkeypatch.setattr(settings, "PLACEHOLDER", "Select Classification")
    yield


def test_recipe_manager_crud():
    manager = RecipeManager()
    data = {"name": "test1", "description": "desc", "prompt": "prompt", "classification": "cat"}
    recipe_id = manager.create_recipe(data)
    assert recipe_id == "test1"

    recipe = manager.get_recipe("test1")
    assert isinstance(recipe, dict)
    assert recipe.get("description") == "desc"

    # List recipes
    assert manager.list_recipes() == ["test1"]

    # Update recipe
    new_data = {"name": "test1", "description": "updated", "prompt": "p2", "classification": "dog"}
    assert manager.update_recipe("test1", new_data)
    updated = manager.get_recipe("test1")
    assert updated.get("description") == "updated"

    # Duplicate recipe
    dup_id = manager.duplicate_recipe("test1", "test2")
    assert dup_id == "test2"
    dup = manager.get_recipe("test2")
    assert dup.get("description") == "updated"

    # Delete recipe
    assert manager.delete_recipe("test1")
    assert manager.get_recipe("test1") is None


def test_invalid_create_raises():
    manager = RecipeManager()
    with pytest.raises(ValidationError):
        manager.create_recipe("not a dict")

    with pytest.raises(ValidationError):
        manager.create_recipe({"name": ""})  # Empty name

    with pytest.raises(ValidationError):
        manager.create_recipe({})  # No name


def test_create_recipe_error_handling():
    manager = RecipeManager()

    # Test when underlying create fails
    mock_path = 'scripts.civitai_manager_libs.recipe_actions.recipe_management._raw_create'
    with patch(mock_path, return_value=False):
        with pytest.raises(FileOperationError):
            manager.create_recipe({"name": "test", "description": "desc"})


def test_update_recipe_validation():
    manager = RecipeManager()

    # Invalid arguments
    with pytest.raises(ValidationError):
        manager.update_recipe("", {"name": "test"})

    with pytest.raises(ValidationError):
        manager.update_recipe("id", "not_dict")

    with pytest.raises(ValidationError):
        manager.update_recipe("id", {"name": ""})


def test_update_recipe_failure():
    manager = RecipeManager()

    # Test when underlying update fails
    mock_path = 'scripts.civitai_manager_libs.recipe_actions.recipe_management._raw_update'
    with patch(mock_path, return_value=False):
        result = manager.update_recipe("test_id", {"name": "test", "description": "desc"})
        assert result is False


def test_delete_recipe_validation():
    manager = RecipeManager()

    # Empty recipe_id
    with pytest.raises(ValidationError):
        manager.delete_recipe("")


def test_delete_recipe_failure():
    manager = RecipeManager()

    # Test when delete doesn't actually remove the recipe
    mock_path = 'scripts.civitai_manager_libs.recipe_actions.recipe_management._raw_get'
    with patch(mock_path, return_value={"name": "test"}):
        result = manager.delete_recipe("test_id")
        assert result is False


def test_get_recipe_validation():
    manager = RecipeManager()

    with pytest.raises(ValidationError):
        manager.get_recipe("")


def test_list_recipes_with_filters():
    manager = RecipeManager()

    # Test with invalid filter criteria
    mock_path = 'scripts.civitai_manager_libs.recipe_actions.recipe_management._raw_list'
    with patch(mock_path, return_value=["r1", "r2"]):
        result = manager.list_recipes("invalid_filter")
        assert result == ["r1", "r2"]

    # Test with valid filter criteria
    with patch(mock_path, return_value=["r1"]) as mock_list:
        result = manager.list_recipes({"search": "test", "classification": "cat"})
        assert result == ["r1"]
        mock_list.assert_called_with(search="test", classification="cat", shortcuts=None)


def test_duplicate_recipe_not_found():
    manager = RecipeManager()

    mock_path = 'scripts.civitai_manager_libs.recipe_actions.recipe_management._raw_get'
    with patch(mock_path, return_value=None):
        with pytest.raises(ValidationError):
            manager.duplicate_recipe("nonexistent", "new_name")


def test_duplicate_recipe_create_failure():
    manager = RecipeManager()

    original_recipe = {"description": "desc", "generate": "gen", "classification": "cat"}
    get_path = 'scripts.civitai_manager_libs.recipe_actions.recipe_management._raw_get'
    create_path = 'scripts.civitai_manager_libs.recipe_actions.recipe_management._raw_create'
    with patch(get_path, return_value=original_recipe), patch(create_path, return_value=False):
        with pytest.raises(FileOperationError):
            manager.duplicate_recipe("original", "new_name")


def test_validate_recipe_data_exception():
    manager = RecipeManager()

    # Test when validation utility raises exception
    with patch.object(
        manager._utils, 'validate_recipe_format', side_effect=Exception("validation error")
    ):
        result = manager.validate_recipe_data({"name": "test"})
        assert result is False


def test_on_recipe_new_btn_click_basic():
    """Test that new recipe button click handler exists and is callable."""
    manager = RecipeManager()

    # Test method exists
    assert hasattr(manager, 'on_recipe_new_btn_click')
    assert callable(getattr(manager, 'on_recipe_new_btn_click'))


def test_on_recipe_update_btn_click_basic():
    """Test that update recipe button click handler exists and is callable."""
    manager = RecipeManager()

    # Test method exists
    assert hasattr(manager, 'on_recipe_update_btn_click')
    assert callable(getattr(manager, 'on_recipe_update_btn_click'))


def test_on_recipe_delete_btn_click_basic():
    """Test that delete recipe button click handler exists and is callable."""
    manager = RecipeManager()

    # Test method exists
    assert hasattr(manager, 'on_recipe_delete_btn_click')
    assert callable(getattr(manager, 'on_recipe_delete_btn_click'))


def test_on_recipe_create_btn_click_basic():
    """Test that create recipe button click handler exists and is callable."""
    manager = RecipeManager()

    # Test method exists
    assert hasattr(manager, 'on_recipe_create_btn_click')
    assert callable(getattr(manager, 'on_recipe_create_btn_click'))


def test_list_recipes_empty_result():
    """Test list_recipes when underlying function returns None."""
    manager = RecipeManager()

    mock_path = 'scripts.civitai_manager_libs.recipe_actions.recipe_management._raw_list'
    with patch(mock_path, return_value=None):
        result = manager.list_recipes()
        assert result == []


def test_create_recipe_with_all_fields():
    """Test creating recipe with all possible fields."""
    manager = RecipeManager()

    data = {
        "name": "complete_recipe",
        "description": "A complete recipe",
        "prompt": "test prompt",
        "classification": "test_category",
    }

    recipe_id = manager.create_recipe(data)
    assert recipe_id == "complete_recipe"


def test_update_recipe_with_minimal_data():
    """Test updating recipe with minimal valid data."""
    manager = RecipeManager()

    # First create a recipe
    data = {"name": "test_recipe", "description": "desc"}
    manager.create_recipe(data)

    # Update with minimal data
    update_data = {"name": "updated_name"}
    result = manager.update_recipe("test_recipe", update_data)
    assert result is True


def test_duplicate_recipe_with_different_classification():
    """Test duplicating recipe preserves classification."""
    manager = RecipeManager()

    # Create original recipe
    data = {"name": "original", "description": "desc", "classification": "category1"}
    manager.create_recipe(data)

    # Duplicate it
    dup_id = manager.duplicate_recipe("original", "duplicate")
    assert dup_id == "duplicate"

    # Verify the duplicate has the same classification
    duplicate = manager.get_recipe("duplicate")
    assert duplicate.get("classification") == "category1"
