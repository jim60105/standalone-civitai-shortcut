import json
import os
import pytest

import scripts.civitai_manager_libs.setting as setting
from scripts.civitai_manager_libs.recipe_actions.recipe_utilities import RecipeUtilities


@pytest.fixture(autouse=True)
def use_tmp_recipe_file(tmp_path, monkeypatch):
    """Redirect recipe storage to a temporary file for tests."""
    tmp_file = tmp_path / "recipes.json"
    tmp_folder = tmp_path / "sc_recipes"
    monkeypatch.setattr(setting, "shortcut_recipe", str(tmp_file))
    monkeypatch.setattr(setting, "shortcut_recipe_folder", str(tmp_folder))
    os.makedirs(tmp_folder, exist_ok=True)
    tmp_file.write_text("{}")
    yield


def test_generate_recipe_id():
    rid = RecipeUtilities.generate_recipe_id()
    assert isinstance(rid, str)
    assert len(rid) == 32


def test_validate_recipe_format():
    assert RecipeUtilities.validate_recipe_format({"name": "a"})
    assert not RecipeUtilities.validate_recipe_format({})
    assert not RecipeUtilities.validate_recipe_format({"name": ""})


def test_export_and_import_recipe(tmp_path):
    utils = RecipeUtilities()
    test_id = "petest"
    data = {test_id: {"description": "d", "generate": "g", "classification": None}}
    import_file = tmp_path / "import.json"
    import_file.write_text(json.dumps(data))
    # Import recipe
    out_id = utils.import_recipe(str(import_file))
    assert out_id == test_id
    # Export recipe
    export_path = utils.export_recipe(test_id, "json")
    assert os.path.isfile(export_path)
    with open(export_path, "r", encoding="utf-8") as f:
        loaded = json.load(f)
    assert test_id in loaded


def test_backup_and_restore_recipe(tmp_path, monkeypatch):
    utils = RecipeUtilities()
    # override settings for file paths
    monkeypatch.setattr(setting, "shortcut_recipe_folder", str(tmp_path))
    monkeypatch.setattr(setting, "shortcut_recipe", str(tmp_path / "recipes.json"))
    test_id = "bptest"
    # simulate original recipe file
    origin_file = tmp_path / f"{test_id}.json"
    origin_file.write_text("{}")
    # Backup
    backup_path = utils.backup_recipe_data(test_id)
    assert os.path.isfile(backup_path)
    # Remove and restore
    origin_file.unlink()
    assert utils.restore_recipe_data(backup_path)
    assert origin_file.exists()
