import pytest

import scripts.civitai_manager_libs.setting as setting
from scripts.civitai_manager_libs.recipe_actions.recipe_management import RecipeManager


@pytest.fixture(autouse=True)
def use_tmp_recipe_file(tmp_path, monkeypatch):
    """Redirect recipe storage to a temporary file for tests."""
    tmp_file = tmp_path / "recipes.json"
    tmp_folder = tmp_path / "sc_recipes"
    monkeypatch.setattr(setting, "shortcut_recipe", str(tmp_file))
    monkeypatch.setattr(setting, "shortcut_recipe_folder", str(tmp_folder))
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
    with pytest.raises(Exception):
        manager.create_recipe("not a dict")
